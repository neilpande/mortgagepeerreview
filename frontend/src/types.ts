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
