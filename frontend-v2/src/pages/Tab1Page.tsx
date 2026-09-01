import type { CompanyRow, Tab1Response } from '../types';
import { SummaryTable } from '../components/SummaryTable';
import { Level3Table } from '../components/Level3Table';
import { SensitivityTable } from '../components/SensitivityTable';
import { ComparisonChart } from '../components/ComparisonChart';
import { DeviationChart } from '../components/DeviationChart';
import { ExportButton } from '../components/ExportButton';
import { exportWorkbook, type SheetDef } from '../lib/exportExcel';

function buildTab1Sheets(data: Tab1Response): SheetDef<CompanyRow>[] {
  const label = (c: CompanyRow) => `${c.ticker} — ${c.name}`;
  return [
    {
      sheetName: 'Summary',
      rows: data.companies,
      labelHeader: 'Servicer',
      labelGet: label,
      columns: [
        { header: 'UPB', get: (c) => c.upb.value, numFmt: '#,##0' },
        { header: 'Fair Value', get: (c) => c.fair_value.value, numFmt: '#,##0' },
        { header: 'Servicing Fee (bps)', get: (c) => c.servicing_fee_bps.value, numFmt: '0.0' },
        { header: 'Price (bps)', get: (c) => c.price_bps?.value ?? null, numFmt: '0.0' },
        { header: 'Mult', get: (c) => c.mult?.value ?? null, numFmt: '0.00"×"' },
      ],
    },
    {
      sheetName: 'Level 3 Inputs',
      rows: data.companies,
      labelHeader: 'Servicer',
      labelGet: label,
      columns: [
        { header: 'CPR %', get: (c) => c.level3.cpr.value, numFmt: '0.0' },
        { header: 'Discount Yield %', get: (c) => c.level3.discount_yield.value, numFmt: '0.0' },
        { header: 'Cost to Service $/loan', get: (c) => c.level3.cost_to_service.value, numFmt: '#,##0' },
      ],
    },
    {
      sheetName: 'Sensitivity',
      rows: data.companies,
      labelHeader: 'Servicer',
      labelGet: label,
      columns: [
        { header: 'Prepay +10%', get: (c) => c.sensitivity.prepay_plus_10.value, numFmt: '#,##0' },
        { header: 'Prepay +20%', get: (c) => c.sensitivity.prepay_plus_20.value, numFmt: '#,##0' },
        { header: 'Discount +10%', get: (c) => c.sensitivity.discount_plus_10.value, numFmt: '#,##0' },
        { header: 'Discount +20%', get: (c) => c.sensitivity.discount_plus_20.value, numFmt: '#,##0' },
        { header: 'Worst case % of equity', get: (c) => c.sensitivity.worst_case_pct_equity.value, numFmt: '0.0' },
      ],
    },
  ];
}

export function Tab1Page({ data }: { data: Tab1Response }) {
  return (
    <section className="page stack">
      <div className="pagehead">
        <div className="no">TAB 01</div>
        <div style={{ flex: '1 1 420px' }}>
          <h1>MSR &amp; Level 3 inputs</h1>
          <p className="lede">
            Servicing book size, carrying value, and servicing economics
            across the peer group for the selected reporting period.
          </p>
        </div>
        <div className="meta">
          <ExportButton
            onExport={() =>
              exportWorkbook(`msr-level3-${data.period.id}.xlsx`, buildTab1Sheets(data))
            }
          />
          <span className="eyebrow">{data.companies.length} peers · as of {data.period.label}</span>
        </div>
      </div>

      <div className="card">
        <header>
          <div>
            <h2>Servicing book and carrying value</h2>
            <p className="hint">
              UPB, MSR fair value, and servicing fee rate as reported, with
              Price (bps) and Mult calculated from those three inputs.
              Hover any value for its source.
            </p>
          </div>
        </header>
        <div className="body flush">
          <SummaryTable rows={data.companies} />
        </div>
      </div>

      <div className="grid2">
        <div className="card">
          <header>
            <div>
              <h2>Prepay speed against discount rate</h2>
              <p className="hint">Bubble area is UPB.</p>
            </div>
          </header>
          <div className="body">
            <ComparisonChart points={data.charts.comparison_scatter} />
          </div>
        </div>
        <div className="card">
          <header>
            <div>
              <h2>How far each mark sits from the peer median</h2>
              <p className="hint">Price (bps) deviation from the peer-group median for this period.</p>
            </div>
          </header>
          <div className="body">
            <DeviationChart points={data.charts.peer_deviation} />
          </div>
        </div>
      </div>

      <div className="card">
        <header>
          <div>
            <h2>Level 3 measurement inputs</h2>
            <p className="hint">CPR, discount yield, and cost to service, as reported.</p>
          </div>
        </header>
        <div className="body flush">
          <Level3Table rows={data.companies} />
        </div>
      </div>

      <div className="card">
        <header>
          <div>
            <h2>Adverse-change sensitivity disclosure</h2>
            <p className="hint">
              MSR value impact of a 10%/20% adverse change in prepayment
              speed or discount rate, as reported, and the worst case as a
              percentage of equity.
            </p>
          </div>
        </header>
        <div className="body flush">
          <SensitivityTable rows={data.companies} />
        </div>
      </div>
    </section>
  );
}
