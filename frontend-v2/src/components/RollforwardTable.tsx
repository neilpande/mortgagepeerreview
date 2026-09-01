import { CompanyLabel } from './CompanyLabel';
import { SourcedCell } from './SourceTooltip';
import type { Tab2CompanyRow } from '../types';

export function RollforwardTable({ rows }: { rows: Tab2CompanyRow[] }) {
  return (
    <div className="tablewrap">
      <table>
        <thead>
          <tr>
            <th className="lbl">Servicer</th>
            <th>Opening</th>
            <th>Originations retained</th>
            <th>Purchases</th>
            <th>Disposals</th>
            <th>Valuation change</th>
            <th>Cash-flow realization</th>
            <th>Closing</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.ticker}>
              <CompanyLabel ticker={c.ticker} name={c.name} note={c.note} filedThisPeriod={c.filed_this_period} />
              <SourcedCell value={c.rollforward.opening} decimals={0} />
              <SourcedCell value={c.rollforward.originations} decimals={0} />
              <SourcedCell value={c.rollforward.purchases} decimals={0} />
              <SourcedCell value={c.rollforward.disposals} decimals={0} />
              <SourcedCell value={c.rollforward.valuation_change} decimals={0} />
              <SourcedCell value={c.rollforward.cashflow_realization} decimals={0} />
              <SourcedCell value={c.rollforward.closing} decimals={0} />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
