import { CompanyLabel } from './CompanyLabel';
import { SourcedCell } from './SourceTooltip';
import type { CompanyRow } from '../types';

// Reference design Table B: the three Level 3 measurement inputs.
export function Level3Table({ rows }: { rows: CompanyRow[] }) {
  return (
    <div className="tablewrap">
      <table>
        <thead>
          <tr>
            <th className="lbl">Servicer</th>
            <th>CPR %</th>
            <th>Discount Yield %</th>
            <th>Cost to Service $/loan</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.ticker}>
              <CompanyLabel ticker={c.ticker} name={c.name} note={c.note} />
              <SourcedCell value={c.level3.cpr} decimals={1} />
              <SourcedCell value={c.level3.discount_yield} decimals={1} />
              <SourcedCell value={c.level3.cost_to_service} decimals={0} />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
