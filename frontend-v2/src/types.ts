// Mirrors backend/app/schemas.py -- keep in sync by hand for Phase 1.

export interface SourcedValue {
  value: number | null;
  tag: string | null;
  form: string | null;
  filed: string | null;
  accn: string | null;
  end: string | null;
}

export interface DerivedValue {
  value: number | null;
  formula: string;
  inputs: Record<string, number | null>;
}

export interface Level3Block {
  cpr: SourcedValue;
  discount_yield: SourcedValue;
  cost_to_service: SourcedValue;
}

export interface SensitivityBlock {
  prepay_plus_10: SourcedValue;
  prepay_plus_20: SourcedValue;
  discount_plus_10: SourcedValue;
  discount_plus_20: SourcedValue;
  worst_case_pct_equity: DerivedValue;
}

export interface CompanyRow {
  ticker: string;
  name: string;
  note: string;
  filed_this_period: boolean;
  upb: SourcedValue;
  fair_value: SourcedValue;
  servicing_fee_bps: DerivedValue;
  price_bps: DerivedValue | null;
  mult: DerivedValue | null;
  level3: Level3Block;
  sensitivity: SensitivityBlock;
}

export interface PeriodInfo {
  id: string;
  form: string;
  fy: number;
  fp: string;
  label: string;
}

export interface ScatterPoint {
  ticker: string;
  name: string;
  cpr: number | null;
  discount_yield: number | null;
  upb: number | null;
}

export interface DeviationPoint {
  ticker: string;
  name: string;
  value: number | null;
  median: number | null;
  deviation: number | null;
}

export interface ChartData {
  comparison_scatter: ScatterPoint[];
  peer_deviation: DeviationPoint[];
}

export interface Tab1Response {
  period: PeriodInfo;
  companies: CompanyRow[];
  charts: ChartData;
}

export interface PeriodsResponse {
  periods: PeriodInfo[];
  default_period_id: string;
}

// ---------------------------------------------------------------------------
// Tab 2 -- Flows & Economics
// ---------------------------------------------------------------------------

export interface RollforwardBlock {
  opening: SourcedValue;
  originations: SourcedValue;
  purchases: SourcedValue;
  disposals: SourcedValue;
  valuation_change: SourcedValue;
  cashflow_realization: SourcedValue;
  closing: SourcedValue;
}

export interface FlowSummaryBlock {
  servicing_fee_income: SourcedValue;
  late_fee_income: SourcedValue;
  ancillary_fee_income: SourcedValue;
  gain_on_sale: SourcedValue;
  lhfs_origination_cash: SourcedValue;
  msr_purchases_cash: SourcedValue;
  msr_sale_proceeds_cash: SourcedValue;
}

export interface Tab2CompanyRow {
  ticker: string;
  name: string;
  note: string;
  filed_this_period: boolean;
  rollforward: RollforwardBlock;
  flows: FlowSummaryBlock;
}

export interface FlowComparisonSeries {
  ticker: string;
  name: string;
  metric: string;
  current_value: number | null;
  prior_value: number | null;
}

export interface Tab2ChartData {
  period_over_period: FlowComparisonSeries[];
}

export interface Tab2Response {
  period: PeriodInfo;
  prior_period: PeriodInfo | null;
  companies: Tab2CompanyRow[];
  charts: Tab2ChartData;
}

// ---------------------------------------------------------------------------
// Tab 3 -- Credit & Balance Sheet
// ---------------------------------------------------------------------------

export interface BalanceSheetBlock {
  assets: SourcedValue;
  liabilities: SourcedValue;
  equity: SourcedValue;
  repo_liability: SourcedValue;
  servicing_liability: SourcedValue;
  leverage: DerivedValue | null;
}

export interface Tab3CompanyRow {
  ticker: string;
  name: string;
  note: string;
  filed_this_period: boolean;
  balance_sheet: BalanceSheetBlock;
  delinquent_upb: SourcedValue;
  delinquency_rate: DerivedValue | null;
}

export interface Tab3ChartData {
  delinquency_deviation: DeviationPoint[];
}

export interface Tab3Response {
  period: PeriodInfo;
  companies: Tab3CompanyRow[];
  charts: Tab3ChartData;
}
