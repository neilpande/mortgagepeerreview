"""Assembles the Tab 2 (Flows & Economics) response for a given period.

Same shape as tabs/tab1.py: loop the peer group through cache ->
extractor -> concepts, in one pass. Additionally resolves the previous
selectable period per company for the period-over-period flow chart.
"""

from __future__ import annotations

from .. import cache
from ..companies import COMPANIES, Company
from ..concepts import BY_KEY
from ..extractor import extract_metric
from ..periods import Period, company_has_filed, period_sort_key
from ..schemas import (
    FlowComparisonSeries,
    FlowSummaryBlock,
    PeriodInfo,
    RollforwardBlock,
    Tab2ChartData,
    Tab2CompanyRow,
    Tab2Response,
)
from .common import sourced

# (schema field name, concept key) -- also drives the period-over-period chart
_FLOW_FIELDS = [
    ("servicing_fee_income", "servicing_fee_income"),
    ("late_fee_income", "late_fee_income"),
    ("ancillary_fee_income", "ancillary_fee_income"),
    ("gain_on_sale", "gain_on_sale"),
    ("lhfs_origination_cash", "lhfs_origination_cash"),
    ("msr_purchases_cash", "msr_purchases_cash"),
    ("msr_sale_proceeds_cash", "msr_sale_proceeds_cash"),
]


def _resolve_flows(company: Company, period: Period) -> dict[str, dict | None]:
    facts = cache.get_company_facts(company.cik)
    return {field: extract_metric(facts, BY_KEY[concept_key], period) for field, concept_key in _FLOW_FIELDS}


def _resolve_company_row(company: Company, period: Period, prior: Period | None) -> Tab2CompanyRow:
    facts = cache.get_company_facts(company.cik)

    opening = extract_metric(facts, BY_KEY["msr_fair_value"], prior) if prior else None
    closing = extract_metric(facts, BY_KEY["msr_fair_value"], period)
    rollforward = RollforwardBlock(
        opening=sourced(opening),
        originations=sourced(extract_metric(facts, BY_KEY["msr_rf_originations"], period)),
        purchases=sourced(extract_metric(facts, BY_KEY["msr_rf_purchases"], period)),
        disposals=sourced(extract_metric(facts, BY_KEY["msr_rf_disposals"], period)),
        valuation_change=sourced(extract_metric(facts, BY_KEY["msr_rf_valuation_change"], period)),
        cashflow_realization=sourced(extract_metric(facts, BY_KEY["msr_rf_cashflow_realization"], period)),
        closing=sourced(closing),
    )

    flows = _resolve_flows(company, period)
    flow_block = FlowSummaryBlock(**{field: sourced(fact) for field, fact in flows.items()})

    return Tab2CompanyRow(
        ticker=company.ticker,
        name=company.name,
        note=company.note,
        filed_this_period=company_has_filed(facts, period),
        rollforward=rollforward,
        flows=flow_block,
    )


def _previous_period(period: Period, all_periods: list[Period]) -> Period | None:
    ordered = sorted(all_periods, key=period_sort_key, reverse=True)
    try:
        idx = next(i for i, p in enumerate(ordered) if p.id == period.id)
    except StopIteration:
        return None
    return ordered[idx + 1] if idx + 1 < len(ordered) else None


def _build_comparison_chart(period: Period, prior: Period | None) -> Tab2ChartData:
    if prior is None:
        return Tab2ChartData(period_over_period=[])

    series: list[FlowComparisonSeries] = []
    for company in COMPANIES:
        current_flows = _resolve_flows(company, period)
        prior_flows = _resolve_flows(company, prior)
        for field, _ in _FLOW_FIELDS:
            current_fact = current_flows[field]
            prior_fact = prior_flows[field]
            series.append(
                FlowComparisonSeries(
                    ticker=company.ticker,
                    name=company.name,
                    metric=field,
                    current_value=current_fact["value"] if current_fact else None,
                    prior_value=prior_fact["value"] if prior_fact else None,
                )
            )
    return Tab2ChartData(period_over_period=series)


def build_tab2_response(period: Period, all_periods: list[Period]) -> Tab2Response:
    prior = _previous_period(period, all_periods)
    rows = [_resolve_company_row(company, period, prior) for company in COMPANIES]
    charts = _build_comparison_chart(period, prior)

    return Tab2Response(
        period=PeriodInfo(id=period.id, form=period.form, fy=period.fy, fp=period.fp, label=period.label),
        prior_period=(
            PeriodInfo(id=prior.id, form=prior.form, fy=prior.fy, fp=prior.fp, label=prior.label)
            if prior
            else None
        ),
        companies=rows,
        charts=charts,
    )
