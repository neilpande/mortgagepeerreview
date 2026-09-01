"""Assembles the Tab 3 (Credit & Balance Sheet) response for a given period.

Same shape as tabs/tab1.py: loop the peer group through cache ->
extractor -> concepts -> calculations, in one pass.
"""

from __future__ import annotations

from statistics import median

from .. import cache
from ..calculations import derive_delinquency_rate, derive_leverage
from ..companies import COMPANIES, Company
from ..concepts import BY_KEY
from ..extractor import extract_metric
from ..periods import Period, company_has_filed
from ..schemas import (
    BalanceSheetBlock,
    DerivedValue,
    DeviationPoint,
    PeriodInfo,
    Tab3ChartData,
    Tab3CompanyRow,
    Tab3Response,
)
from .common import sourced


def _resolve_company_row(company: Company, period: Period) -> tuple[Tab3CompanyRow, dict]:
    facts = cache.get_company_facts(company.cik)

    assets_fact = extract_metric(facts, BY_KEY["assets"], period)
    liabilities_fact = extract_metric(facts, BY_KEY["liabilities"], period)
    equity_fact = extract_metric(facts, BY_KEY["equity"], period)
    repo_fact = extract_metric(facts, BY_KEY["repo_liability"], period)
    servicing_liability_fact = extract_metric(facts, BY_KEY["servicing_liability"], period)
    delinquent_fact = extract_metric(facts, BY_KEY["delinquent_upb"], period)
    upb_fact = extract_metric(facts, BY_KEY["msr_upb"], period)

    liabilities = liabilities_fact["value"] if liabilities_fact else None
    equity = equity_fact["value"] if equity_fact else None
    leverage = derive_leverage(liabilities, equity)

    upb = upb_fact["value"] if upb_fact else None
    delinquent_upb = delinquent_fact["value"] if delinquent_fact else None
    delinquency_rate = derive_delinquency_rate(delinquent_upb, upb)

    row = Tab3CompanyRow(
        ticker=company.ticker,
        name=company.name,
        note=company.note,
        filed_this_period=company_has_filed(facts, period),
        balance_sheet=BalanceSheetBlock(
            assets=sourced(assets_fact),
            liabilities=sourced(liabilities_fact),
            equity=sourced(equity_fact),
            repo_liability=sourced(repo_fact),
            servicing_liability=sourced(servicing_liability_fact),
            leverage=(
                DerivedValue(
                    value=leverage,
                    formula="liabilities / equity",
                    inputs={"liabilities": liabilities, "equity": equity},
                )
                if leverage is not None
                else None
            ),
        ),
        delinquent_upb=sourced(delinquent_fact),
        delinquency_rate=(
            DerivedValue(
                value=delinquency_rate,
                formula="delinquent_upb / upb * 100",
                inputs={"delinquent_upb": delinquent_upb, "upb": upb},
            )
            if delinquency_rate is not None
            else None
        ),
    )

    return row, {"delinquency_rate": delinquency_rate}


def _build_delinquency_chart(rows_raw: list[dict], companies: list[Company]) -> Tab3ChartData:
    values = [r["delinquency_rate"] for r in rows_raw if r["delinquency_rate"] is not None]
    peer_median = median(values) if values else None
    points = [
        DeviationPoint(
            ticker=c.ticker,
            name=c.name,
            value=r["delinquency_rate"],
            median=peer_median,
            deviation=(
                r["delinquency_rate"] - peer_median
                if r["delinquency_rate"] is not None and peer_median is not None
                else None
            ),
        )
        for c, r in zip(companies, rows_raw)
    ]
    return Tab3ChartData(delinquency_deviation=points)


def build_tab3_response(period: Period) -> Tab3Response:
    rows: list[Tab3CompanyRow] = []
    raws: list[dict] = []
    for company in COMPANIES:
        row, raw = _resolve_company_row(company, period)
        rows.append(row)
        raws.append(raw)

    charts = _build_delinquency_chart(raws, list(COMPANIES))

    return Tab3Response(
        period=PeriodInfo(id=period.id, form=period.form, fy=period.fy, fp=period.fp, label=period.label),
        companies=rows,
        charts=charts,
    )
