import { CompanyLabel } from './CompanyLabel';
import { DerivedCell, SourcedCell } from './SourceTooltip';
import type { Tab3CompanyRow } from '../types';

export function BalanceSheetTable({ rows }: { rows: Tab3CompanyRow[] }) {
  return (
    <div className="tablewrap">
      <table>
        <thead>
          <tr>
            <th className="lbl">Servicer</th>
            <th>Total assets</th>
            <th>Liabilities</th>
            <th>Stockholders' equity</th>
            <th>Repo / warehouse funding</th>
            <th>Servicing liability</th>
            <th>Leverage</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.ticker}>
              <CompanyLabel ticker={c.ticker} name={c.name} note={c.note} filedThisPeriod={c.filed_this_period} />
              <SourcedCell value={c.balance_sheet.assets} decimals={0} />
              <SourcedCell value={c.balance_sheet.liabilities} decimals={0} />
              <SourcedCell value={c.balance_sheet.equity} decimals={0} />
              <SourcedCell value={c.balance_sheet.repo_liability} decimals={0} />
              <SourcedCell value={c.balance_sheet.servicing_liability} decimals={0} />
              <DerivedCell value={c.balance_sheet.leverage} decimals={2} suffix="×" />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
