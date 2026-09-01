import { CompanyLabel } from './CompanyLabel';
import { SourcedCell } from './SourceTooltip';
import type { Tab2CompanyRow } from '../types';

export function FlowSummaryTable({ rows }: { rows: Tab2CompanyRow[] }) {
  return (
    <div className="tablewrap">
      <table>
        <thead>
          <tr>
            <th className="lbl">Servicer</th>
            <th>Servicing fee income</th>
            <th>Late fee income</th>
            <th>Ancillary fee income</th>
            <th>Gain on sale</th>
            <th>LHFS origination cash</th>
            <th>MSR purchases</th>
            <th>MSR sale proceeds</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.ticker}>
              <CompanyLabel ticker={c.ticker} name={c.name} note={c.note} filedThisPeriod={c.filed_this_period} />
              <SourcedCell value={c.flows.servicing_fee_income} decimals={0} />
              <SourcedCell value={c.flows.late_fee_income} decimals={0} />
              <SourcedCell value={c.flows.ancillary_fee_income} decimals={0} />
              <SourcedCell value={c.flows.gain_on_sale} decimals={0} />
              <SourcedCell value={c.flows.lhfs_origination_cash} decimals={0} />
              <SourcedCell value={c.flows.msr_purchases_cash} decimals={0} />
              <SourcedCell value={c.flows.msr_sale_proceeds_cash} decimals={0} />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
