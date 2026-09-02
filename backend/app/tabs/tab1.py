"""Assembles the Tab 1 (MSR & Level 3) response for a given period.

Loops the peer group through cache -> extractor -> concepts ->
calculations, in one pass, per PRD Section 11's data flow.
"""

from __future__ import annotations

from statistics import median

from .. import cache
from ..calculations import annualize_duration, derive_price_mult, derive_servicing_fee_bps
from ..companies import COMPANIES, Company
from ..concepts import BY_KEY
from ..extractor import extract_metric
from ..periods import Period, company_has_filed
from ..schemas import (
    ChartData,
    CompanyRow,
    DerivedValue,
    DeviationPoint,
    Level3Block,
    PeriodInfo,
    ScatterPoint,
    SensitivityBlock,
    Tab1Response,
)
from .common import sourced as _sourced


def _has_price_bps(company: Company, period: Period) -> bool:
    """Cheap check of just the 3 concepts Price/Mult need, instead of
    resolving all 11 concepts a full company row needs.

    best_period_for_coverage calls this up to (scan_limit x 7 companies)
    times just to compare coverage across candidate periods -- resolving
    every Level 3/sensitivity concept each time was pure waste there, and
    measurably slow under Python-level JSON scanning on a CPU-constrained
    host, since it's the same underlying data walked repeatedly either way.
    """
    facts = cache.get_company_facts(company.cik)
    upb_fact = extract_metric(facts, BY_KEY["msr_upb"], period)
    fv_fact = extract_metric(facts, BY_KEY["msr_fair_value"], period)
    fee_fact = extract_metric(facts, BY_KEY["servicing_fee_income"], period)

    upb = upb_fact["value"] if upb_fact else None
    fair_value = fv_fact["value"] if fv_fact else None
    fee_annualized = (
        annualize_duration(fee_fact["value"], fee_fact["start"], fee_fact["end"])
        if fee_fact
        else None
    )
    servicing_fee_bps = derive_servicing_fee_bps(fee_annualized, upb)
    return derive_price_mult(upb, fair_value, servicing_fee_bps) is not None


def _resolve_company_row(company: Company, period: Period) -> tuple[CompanyRow, dict]:
    facts = cache.get_company_facts(company.cik)

    upb_fact = extract_metric(facts, BY_KEY["msr_upb"], period)
    fv_fact = extract_metric(facts, BY_KEY["msr_fair_value"], period)
    fee_fact = extract_metric(facts, BY_KEY["servicing_fee_income"], period)
    cpr_fact = extract_metric(facts, BY_KEY["msr_cpr"], period)
    yld_fact = extract_metric(facts, BY_KEY["msr_discount_rate"], period)
    cts_fact = extract_metric(facts, BY_KEY["msr_cost_to_service"], period)
    p10_fact = extract_metric(facts, BY_KEY["msr_sensitivity_prepay_10"], period)
    p20_fact = extract_metric(facts, BY_KEY["msr_sensitivity_prepay_20"], period)
    d10_fact = extract_metric(facts, BY_KEY["msr_sensitivity_discount_10"], period)
    d20_fact = extract_metric(facts, BY_KEY["msr_sensitivity_discount_20"], period)
    eq_fact = extract_metric(facts, BY_KEY["equity"], period)

    upb = upb_fact["value"] if upb_fact else None
    fair_value = fv_fact["value"] if fv_fact else None

    fee_annualized = (
        annualize_duration(fee_fact["value"], fee_fact["start"], fee_fact["end"])
        if fee_fact
        else None
    )
    servicing_fee_bps = derive_servicing_fee_bps(fee_annualized, upb)
    price_mult = derive_price_mult(upb, fair_value, servicing_fee_bps)

    equity = eq_fact["value"] if eq_fact else None
    p20 = p20_fact["value"] if p20_fact else None
    d20 = d20_fact["value"] if d20_fact else None
    worst_case_pct_equity = None
    if p20 is not None and d20 is not None and equity:
        worst_case_pct_equity = abs(min(p20, d20)) / equity * 100

    row = CompanyRow(
        ticker=company.ticker,
        name=company.name,
        note=company.note,
        filed_this_period=company_has_filed(facts, period),
        upb=_sourced(upb_fact),
        fair_value=_sourced(fv_fact),
        servicing_fee_bps=DerivedValue(
            value=servicing_fee_bps,
            formula="servicing_fee_income (annualized) / upb * 10,000",
            inputs={"servicing_fee_income_annualized": fee_annualized, "upb": upb},
        ),
        price_bps=(
            DerivedValue(
                value=price_mult.price_bps,
                formula="fair_value / upb * 10,000",
                inputs={"fair_value": fair_value, "upb": upb},
            )
            if price_mult
            else None
        ),
        mult=(
            DerivedValue(
                value=price_mult.mult,
                formula="price_bps / servicing_fee_bps",
                inputs={"price_bps": price_mult.price_bps if price_mult else None, "servicing_fee_bps": servicing_fee_bps},
            )
            if price_mult
            else None
        ),
        level3=Level3Block(
            cpr=_sourced(cpr_fact),
            discount_yield=_sourced(yld_fact),
            cost_to_service=_sourced(cts_fact),
        ),
        sensitivity=SensitivityBlock(
            prepay_plus_10=_sourced(p10_fact),
            prepay_plus_20=_sourced(p20_fact),
            discount_plus_10=_sourced(d10_fact),
            discount_plus_20=_sourced(d20_fact),
            worst_case_pct_equity=DerivedValue(
                value=worst_case_pct_equity,
                formula="|min(prepay_+20%, discount_+20%)| / equity * 100",
                inputs={"prepay_plus_20": p20, "discount_plus_20": d20, "equity": equity},
            ),
        ),
    )

    raw = {
        "upb": upb,
        "fair_value": fair_value,
        "cpr": cpr_fact["value"] if cpr_fact else None,
        "discount_yield": yld_fact["value"] if yld_fact else None,
        "price_bps": price_mult.price_bps if price_mult else None,
    }
    return row, raw


def _build_charts(rows_raw: list[dict], companies: list[Company]) -> ChartData:
    scatter = [
        ScatterPoint(
            ticker=c.ticker,
            name=c.name,
            cpr=r["cpr"],
            discount_yield=r["discount_yield"],
            upb=r["upb"],
        )
        for c, r in zip(companies, rows_raw)
    ]

    price_values = [r["price_bps"] for r in rows_raw if r["price_bps"] is not None]
    peer_median = median(price_values) if price_values else None
    deviation = [
        DeviationPoint(
            ticker=c.ticker,
            name=c.name,
            value=r["price_bps"],
            median=peer_median,
            deviation=(r["price_bps"] - peer_median) if r["price_bps"] is not None and peer_median is not None else None,
        )
        for c, r in zip(companies, rows_raw)
    ]

    return ChartData(comparison_scatter=scatter, peer_deviation=deviation)


def best_period_for_coverage(candidates: list[Period], *, scan_limit: int = 6) -> Period:
    """Pick the period with the most fully-populated primary-table rows.

    The most recent selectable period is frequently the sparsest -- interim
    (10-Q) filings often lag on Level 3 disclosures, and the newest quarter
    may not be tagged by every peer yet. Scoring the most recent
    `scan_limit` candidates by how many companies get a real Price/Mult and
    preferring the best-covered one (ties broken by recency) gives a much
    more useful default than "chronologically newest" while still avoiding
    reaching arbitrarily far back into history.
    """
    if not candidates:
        raise ValueError("no candidate periods to choose from")

    best_period = candidates[0]
    best_score = -1
    for period in candidates[:scan_limit]:
        score = sum(1 for company in COMPANIES if _has_price_bps(company, period))
        if score > best_score:
            best_score = score
            best_period = period
        if score == len(COMPANIES):
            break  # full coverage -- nothing later in the scan can beat it
    return best_period


def build_tab1_response(period: Period) -> Tab1Response:
    rows: list[CompanyRow] = []
    raws: list[dict] = []
    for company in COMPANIES:
        row, raw = _resolve_company_row(company, period)
        rows.append(row)
        raws.append(raw)

    rows_sorted = sorted(
        zip(rows, raws), key=lambda pair: pair[1]["upb"] or 0, reverse=True
    )
    rows = [r for r, _ in rows_sorted]

    charts = _build_charts(raws, list(COMPANIES))

    return Tab1Response(
        period=PeriodInfo(id=period.id, form=period.form, fy=period.fy, fp=period.fp, label=period.label),
        companies=rows,
        charts=charts,
    )
