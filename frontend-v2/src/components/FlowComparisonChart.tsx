import { nf } from '../lib/format';
import type { FlowComparisonSeries } from '../types';

const METRIC_LABELS: Record<string, string> = {
  servicing_fee_income: 'Servicing fee income',
  late_fee_income: 'Late fee income',
  ancillary_fee_income: 'Ancillary fee income',
  gain_on_sale: 'Gain on sale',
  lhfs_origination_cash: 'LHFS origination cash',
  msr_purchases_cash: 'MSR purchases',
  msr_sale_proceeds_cash: 'MSR sale proceeds',
};

// Grouped current-vs-prior-period bars for one metric at a time. The
// backend hands back every metric x company combination; this picks
// whichever metric has the best current-period coverage so the chart
// isn't empty by default, rather than hardcoding one that might be sparse.
export function FlowComparisonChart({ series }: { series: FlowComparisonSeries[] }) {
  if (series.length === 0) return <div className="empty">Not enough data to plot for this period.</div>;

  const metrics = Array.from(new Set(series.map((s) => s.metric)));
  const coverage = (metric: string) =>
    series.filter((s) => s.metric === metric && s.current_value !== null).length;
  const bestMetric = metrics.reduce((a, b) => (coverage(b) > coverage(a) ? b : a), metrics[0]);

  const rows = series.filter(
    (s) => s.metric === bestMetric && (s.current_value !== null || s.prior_value !== null)
  );
  if (rows.length === 0) return <div className="empty">Not enough data to plot for this period.</div>;

  const W = 560, groupW = 90, padL = 62, padR = 18, padT = 20;
  const H = padT + rows.length * groupW * 0.62 + 28;
  const max = Math.max(...rows.flatMap((r) => [r.current_value ?? 0, r.prior_value ?? 0])) * 1.1 || 1;
  const x = (v: number) => padL + (v / max) * (W - padL - padR);
  const rowH = groupW * 0.62;

  return (
    <>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${METRIC_LABELS[bestMetric]}, current vs prior period`}>
        <line className="zl" x1={padL} y1={padT} x2={padL} y2={padT + rows.length * rowH} />
        {rows.map((r, i) => {
          const y = padT + i * rowH;
          const curW = Math.max(1.5, x(r.current_value ?? 0) - padL);
          const priW = Math.max(1.5, x(r.prior_value ?? 0) - padL);
          return (
            <g className="hoverable" key={r.ticker}>
              <text className="axl" x={padL - 9} y={y + rowH / 2 + 3.5} textAnchor="end">{r.ticker}</text>
              <rect x={padL} y={y + 4} width={priW} height={rowH * 0.32} rx={3} fill="var(--ink-3)" opacity={0.45}>
                <title>{`${r.name} prior period: ${nf(r.prior_value, 0)}`}</title>
              </rect>
              <rect x={padL} y={y + 4 + rowH * 0.36} width={curW} height={rowH * 0.32} rx={3} fill="var(--accent)">
                <title>{`${r.name} current period: ${nf(r.current_value, 0)}`}</title>
              </rect>
            </g>
          );
        })}
      </svg>
      <div className="legend">
        <span><i style={{ background: 'var(--accent)' }} />Current period</span>
        <span><i style={{ background: 'var(--ink-3)', opacity: 0.45 }} />Prior period</span>
      </div>
      <p style={{ fontSize: '12.5px', color: 'var(--ink-3)', marginTop: '10px' }}>
        Showing {METRIC_LABELS[bestMetric] ?? bestMetric} — the flow metric with the most current-period coverage this period.
      </p>
    </>
  );
}
