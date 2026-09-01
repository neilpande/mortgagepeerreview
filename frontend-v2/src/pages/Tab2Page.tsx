import type { Tab2CompanyRow, Tab2Response } from '../types';
import { RollforwardTable } from '../components/RollforwardTable';
import { FlowSummaryTable } from '../components/FlowSummaryTable';
import { FlowComparisonChart } from '../components/FlowComparisonChart';
import { ExportButton } from '../components/ExportButton';
import { exportWorkbook, type SheetDef } from '../lib/exportExcel';

function buildTab2Sheets(data: Tab2Response): SheetDef<Tab2CompanyRow>[] {
  const label = (c: Tab2CompanyRow) => `${c.ticker} — ${c.name}`;
  return [
    {
      sheetName: 'MSR Roll-forward',
      rows: data.companies,
      labelHeader: 'Servicer',
      labelGet: label,
      columns: [
        { header: 'Opening', get: (c) => c.rollforward.opening.value, numFmt: '#,##0' },
        { header: 'Originations retained', get: (c) => c.rollforward.originations.value, numFmt: '#,##0' },
        { header: 'Purchases', get: (c) => c.rollforward.purchases.value, numFmt: '#,##0' },
        { header: 'Disposals', get: (c) => c.rollforward.disposals.value, numFmt: '#,##0' },
        { header: 'Valuation change', get: (c) => c.rollforward.valuation_change.value, numFmt: '#,##0' },
        { header: 'Cash-flow realization', get: (c) => c.rollforward.cashflow_realization.value, numFmt: '#,##0' },
        { header: 'Closing', get: (c) => c.rollforward.closing.value, numFmt: '#,##0' },
      ],
    },
    {
      sheetName: 'Revenue & Flows',
      rows: data.companies,
      labelHeader: 'Servicer',
      labelGet: label,
      columns: [
        { header: 'Servicing fee income', get: (c) => c.flows.servicing_fee_income.value, numFmt: '#,##0' },
        { header: 'Late fee income', get: (c) => c.flows.late_fee_income.value, numFmt: '#,##0' },
        { header: 'Ancillary fee income', get: (c) => c.flows.ancillary_fee_income.value, numFmt: '#,##0' },
        { header: 'Gain on sale', get: (c) => c.flows.gain_on_sale.value, numFmt: '#,##0' },
        { header: 'LHFS origination cash', get: (c) => c.flows.lhfs_origination_cash.value, numFmt: '#,##0' },
        { header: 'MSR purchases', get: (c) => c.flows.msr_purchases_cash.value, numFmt: '#,##0' },
        { header: 'MSR sale proceeds', get: (c) => c.flows.msr_sale_proceeds_cash.value, numFmt: '#,##0' },
      ],
    },
  ];
}

export function Tab2Page({ data }: { data: Tab2Response }) {
  return (
    <section className="page stack">
      <div className="pagehead">
        <div className="no">TAB 02</div>
        <div style={{ flex: '1 1 420px' }}>
          <h1>Flows &amp; economics</h1>
          <p className="lede">
            What moved the MSR asset over the period, and what the book
            earned, across the peer group.
          </p>
        </div>
        <div className="meta">
          <ExportButton
            onExport={() =>
              exportWorkbook(`flows-economics-${data.period.id}.xlsx`, buildTab2Sheets(data))
            }
          />
          <span className="eyebrow">
            {data.companies.length} peers · as of {data.period.label}
            {data.prior_period ? ` · prior period ${data.prior_period.label}` : ''}
          </span>
        </div>
      </div>

      <div className="card">
        <header>
          <div>
            <h2>MSR roll-forward</h2>
            <p className="hint">
              Opening and closing MSR fair value, and the additions,
              disposals, and mark that moved it in between. Hover any value
              for its source.
            </p>
          </div>
        </header>
        <div className="body flush">
          <RollforwardTable rows={data.companies} />
        </div>
      </div>

      <div className="card">
        <header>
          <div>
            <h2>Revenue &amp; flow summary</h2>
            <p className="hint">
              Servicing and ancillary fee income, gain on sale, and MSR /
              LHFS cash-flow activity for the period.
            </p>
          </div>
        </header>
        <div className="body flush">
          <FlowSummaryTable rows={data.companies} />
        </div>
      </div>

      <div className="card">
        <header>
          <div>
            <h2>Period-over-period comparison</h2>
            <p className="hint">This period against the prior selectable period, by company.</p>
          </div>
        </header>
        <div className="body">
          <FlowComparisonChart series={data.charts.period_over_period} />
        </div>
      </div>
    </section>
  );
}
