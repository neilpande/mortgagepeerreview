import { nf } from '../lib/format';
import type { DeviationPoint } from '../types';

// Ported from the reference design's divBar() builder: how far each
// company's Price (bps) mark sits from the peer-group median for the
// selected period.
export function DeviationChart({ points }: { points: DeviationPoint[] }) {
  const rows = points.filter((p) => p.deviation !== null && p.median !== null);
  if (rows.length === 0) return <div className="empty">Not enough data to plot for this period.</div>;

  const median = rows[0].median as number;
  const W = 560, rowH = 32, padL = 58, padR = 18, padT = 22;
  const H = padT + rows.length * rowH + 28;
  const m = Math.max(...rows.map((r) => Math.abs(r.deviation as number))) * 1.4 || 1;
  const mid = padL + (W - padL - padR) / 2, half = (W - padL - padR) / 2;
  const x = (v: number) => mid + (v / m) * half;

  const ticks = [-1, -0.5, 0, 0.5, 1];

  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Peer-median deviation chart">
      {ticks.map((f) => {
        const v = m * f;
        return (
          <g key={f}>
            <line className={f === 0 ? 'zl' : 'gl'} x1={x(v)} y1={padT - 6} x2={x(v)} y2={padT + rows.length * rowH} />
            <text className="ax" x={x(v)} y={padT + rows.length * rowH + 16} textAnchor="middle">
              {f === 0 ? `median ${nf(median, 1)}` : nf(median + v, 1)}
            </text>
          </g>
        );
      })}
      {rows.map((r, i) => {
        const d = r.deviation as number;
        const y = padT + i * rowH + 8, h = rowH - 16, pos = d >= 0;
        return (
          <g className="hoverable" key={r.ticker}>
            <text className="axl" x={padL - 9} y={y + h / 2 + 3.5} textAnchor="end">{r.ticker}</text>
            <rect
              x={pos ? mid : x(d)}
              y={y}
              width={Math.max(1.5, Math.abs(x(d) - mid))}
              height={h}
              rx={4}
              fill={pos ? 'var(--s1)' : 'var(--crit)'}
            >
              <title>{`${r.name}: ${nf(r.value, 1)} bps (median ${nf(r.median, 1)})`}</title>
            </rect>
            <text className="dl" x={pos ? x(d) + 8 : x(d) - 8} y={y + h / 2 + 3.5} textAnchor={pos ? 'start' : 'end'}>
              {nf(r.value, 1)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
