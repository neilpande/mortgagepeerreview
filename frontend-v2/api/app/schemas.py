"""Response models for the Tab 1 API (PRD Section 12).

Every value the frontend renders carries its provenance inline, so a
hover tooltip never needs a separate request (PRD Section 9/13).
"""

from __future__ import annotations

from pydantic import BaseModel


class SourcedValue(BaseModel):
    """A value resolved directly from an XBRL fact."""

    value: float | None
    tag: str | None = None
    form: str | None = None
    filed: str | None = None
    accn: str | None = None
    end: str | None = None


class DerivedValue(BaseModel):
    """A value computed on the backend from other resolved values."""

    value: float | None
    formula: str
    inputs: dict[str, float | None]


class Level3Block(BaseModel):
    cpr: SourcedValue
    discount_yield: SourcedValue
    cost_to_service: SourcedValue


class SensitivityBlock(BaseModel):
    prepay_plus_10: SourcedValue
    prepay_plus_20: SourcedValue
    discount_plus_10: SourcedValue
    discount_plus_20: SourcedValue
    worst_case_pct_equity: DerivedValue


class CompanyRow(BaseModel):
    ticker: str
    name: str
    note: str
    filed_this_period: bool
    upb: SourcedValue
    fair_value: SourcedValue
    servicing_fee_bps: DerivedValue
    price_bps: DerivedValue | None
    mult: DerivedValue | None
    level3: Level3Block
    sensitivity: SensitivityBlock


class PeriodInfo(BaseModel):
    id: str
    form: str
    fy: int
    fp: str
    label: str


class ScatterPoint(BaseModel):
    ticker: str
    name: str
    cpr: float | None
    discount_yield: float | None
    upb: float | None


class DeviationPoint(BaseModel):
    ticker: str
    name: str
    value: float | None
    median: float | None
    deviation: float | None


class ChartData(BaseModel):
    comparison_scatter: list[ScatterPoint]
    peer_deviation: list[DeviationPoint]


class Tab1Response(BaseModel):
    period: PeriodInfo
    companies: list[CompanyRow]
    charts: ChartData


class PeriodsResponse(BaseModel):
    periods: list[PeriodInfo]
    default_period_id: str


# ---------------------------------------------------------------------------
# Tab 2 -- Flows & Economics
# ---------------------------------------------------------------------------


class RollforwardBlock(BaseModel):
    opening: SourcedValue
    originations: SourcedValue
    purchases: SourcedValue
    disposals: SourcedValue
    valuation_change: SourcedValue
    cashflow_realization: SourcedValue
    closing: SourcedValue


class FlowSummaryBlock(BaseModel):
    servicing_fee_income: SourcedValue
    late_fee_income: SourcedValue
    ancillary_fee_income: SourcedValue
    gain_on_sale: SourcedValue
    lhfs_origination_cash: SourcedValue
    msr_purchases_cash: SourcedValue
    msr_sale_proceeds_cash: SourcedValue


class Tab2CompanyRow(BaseModel):
    ticker: str
    name: str
    note: str
    filed_this_period: bool
    rollforward: RollforwardBlock
    flows: FlowSummaryBlock


class FlowComparisonSeries(BaseModel):
    ticker: str
    name: str
    metric: str
    current_value: float | None
    prior_value: float | None


class Tab2ChartData(BaseModel):
    period_over_period: list[FlowComparisonSeries]


class Tab2Response(BaseModel):
    period: PeriodInfo
    prior_period: PeriodInfo | None
    companies: list[Tab2CompanyRow]
    charts: Tab2ChartData


# ---------------------------------------------------------------------------
# Tab 3 -- Credit & Balance Sheet
# ---------------------------------------------------------------------------


class BalanceSheetBlock(BaseModel):
    assets: SourcedValue
    liabilities: SourcedValue
    equity: SourcedValue
    repo_liability: SourcedValue
    servicing_liability: SourcedValue
    leverage: DerivedValue | None


class Tab3CompanyRow(BaseModel):
    ticker: str
    name: str
    note: str
    filed_this_period: bool
    balance_sheet: BalanceSheetBlock
    delinquent_upb: SourcedValue
    delinquency_rate: DerivedValue | None


class Tab3ChartData(BaseModel):
    delinquency_deviation: list[DeviationPoint]


class Tab3Response(BaseModel):
    period: PeriodInfo
    companies: list[Tab3CompanyRow]
    charts: Tab3ChartData
