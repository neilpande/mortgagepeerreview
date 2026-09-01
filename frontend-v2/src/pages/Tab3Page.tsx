import type { Tab3CompanyRow, Tab3Response } from '../types';
import { BalanceSheetTable } from '../components/BalanceSheetTable';
import { DeviationChart } from '../components/DeviationChart';
import { ExportButton } from '../components/ExportButton';
import { exportWorkbook, type SheetDef } from '../lib/exportExcel';

function buildTab3Sheets(data: Tab3Response): SheetDef<Tab3CompanyRow>[] {
  const label = (c: Tab3CompanyRow) => `${c.ticker} — ${c.name}`;
  return [
    {
      sheetName: 'Balance Sheet',
      rows: data.companies,
      labelHeader: 'Servicer',
      labelGet: label,
      columns: [
        { header: 'Total assets', get: (c) => c.balance_sheet.assets.value, numFmt: '#,##0' },
        { header: 'Liabilities', get: (c) => c.balance_sheet.liabilities.value, numFmt: '#,##0' },
        { header: "Stockholders' equity", get: (c) => c.balance_sheet.equity.value, numFmt: '#,##0' },
        { header: 'Repo / warehouse funding', get: (c) => c.balance_sheet.repo_liability.value, numFmt: '#,##0' },
        { header: 'Servicing liability', get: (c) => c.balance_sheet.servicing_liability.value, numFmt: '#,##0' },
        { header: 'Leverage', get: (c) => c.balance_sheet.leverage?.value ?? null, numFmt: '0.00"×"' },
        { header: 'Delinquent UPB', get: (c) => c.delinquent_upb.value, numFmt: '#,##0' },
        { header: 'Delinquency rate %', get: (c) => c.delinquency_rate?.value ?? null, numFmt: '0.00' },
      ],
    },
  ];
}

export function Tab3Page({ data }: { data: Tab3Response }) {
  return (
    <section className="page stack">
      <div className="pagehead">
        <div className="no">TAB 03</div>
        <div style={{ flex: '1 1 420px' }}>
          <h1>Credit &amp; balance sheet</h1>
          <p className="lede">
            Balance sheet strength and credit quality across the peer
            group for the selected reporting period.
          </p>
        </div>
        <div className="meta">
          <ExportButton
            onExport={() =>
              exportWorkbook(`credit-balance-sheet-${data.period.id}.xlsx`, buildTab3Sheets(data))
            }
          />
          <span className="eyebrow">{data.companies.length} peers · as of {data.period.label}</span>
        </div>
      </div>

      <div className="card">
        <header>
          <div>
            <h2>Balance sheet summary</h2>
            <p className="hint">
              Total assets, liabilities, equity, repo/warehouse funding,
              and servicing liability as reported, with leverage
              calculated from liabilities and equity.
            </p>
          </div>
        </header>
        <div className="body flush">
          <BalanceSheetTable rows={data.companies} />
        </div>
      </div>

      <div className="card">
        <header>
          <div>
            <h2>Delinquency against the peer median</h2>
            <p className="hint">Delinquent UPB as a percentage of total UPB, per company, vs. the peer-group median.</p>
          </div>
        </header>
        <div className="body">
          <DeviationChart points={data.charts.delinquency_deviation} />
        </div>
      </div>
    </section>
  );
}
