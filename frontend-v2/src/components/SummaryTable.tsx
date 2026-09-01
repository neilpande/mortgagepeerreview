import { CompanyLabel } from './CompanyLabel';
import { CoverageStitch } from './CoverageStitch';
import { DerivedCell, SourcedCell } from './SourceTooltip';
import type { CompanyRow } from '../types';

// PRD Section 6: exactly 5 data columns, one row per company, sorted by
// UPB descending (the backend already returns rows in that order).
export function SummaryTable({ rows }: { rows: CompanyRow[] }) {
  return (
    <div className="tablewrap">
      <table>
        <thead>
          <tr>
            <th className="lbl">Servicer</th>
            <th>UPB</th>
            <th>Fair Value</th>
            <th>Servicing Fee (bps)</th>
            <th>Price (bps)</th>
            <th>Mult</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.ticker}>
              <CompanyLabel ticker={c.ticker} name={c.name} note={c.note} filedThisPeriod={c.filed_this_period} after={<CoverageStitch row={c} />} />
              <SourcedCell value={c.upb} decimals={0} />
              <SourcedCell value={c.fair_value} decimals={0} />
              <DerivedCell value={c.servicing_fee_bps} decimals={1} />
              <DerivedCell value={c.price_bps} decimals={1} />
              <DerivedCell value={c.mult} decimals={2} suffix="×" />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
