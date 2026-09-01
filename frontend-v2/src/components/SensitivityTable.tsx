import { CompanyLabel } from './CompanyLabel';
import { DerivedCell, SourcedCell } from './SourceTooltip';
import type { CompanyRow } from '../types';

// Reference design Table C: the adverse-change sensitivity disclosure.
export function SensitivityTable({ rows }: { rows: CompanyRow[] }) {
  return (
    <div className="tablewrap">
      <table>
        <thead>
          <tr>
            <th className="lbl">Servicer</th>
            <th>Prepay +10% $</th>
            <th>Prepay +20% $</th>
            <th>Discount +10% $</th>
            <th>Discount +20% $</th>
            <th>Worst case % of equity</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.ticker}>
              <CompanyLabel ticker={c.ticker} name={c.name} note={c.note} filedThisPeriod={c.filed_this_period} />
              <SourcedCell value={c.sensitivity.prepay_plus_10} decimals={0} />
              <SourcedCell value={c.sensitivity.prepay_plus_20} decimals={0} />
              <SourcedCell value={c.sensitivity.discount_plus_10} decimals={0} />
              <SourcedCell value={c.sensitivity.discount_plus_20} decimals={0} />
              <DerivedCell value={c.sensitivity.worst_case_pct_equity} decimals={1} />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
