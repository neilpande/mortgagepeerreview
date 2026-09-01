import type { ScatterPoint } from '../types';

// Ported from the reference design's scatter() builder: CPR against
// discount yield, bubble area proportional to UPB. Driven entirely by the
// `comparison_scatter` series already computed by the backend -- no
// client-side math beyond SVG layout.
export function ComparisonChart({ points }: { points: ScatterPoint[] }) {
  const plottable = points.filter((p) => p.cpr !== null && p.discount_yield !== null);
  if (plottable.length === 0) return <div className="empty">Not enough data to plot for this period.</div>;

  const W = 560, H = 330, padL = 54, padR = 26, padT = 18, padB = 48;
  const xs = plottable.map((p) => p.cpr as number);
  const ys = plottable.map((p) => p.discount_yield as number);
  const x0 = Math.min(...xs) - 0.7, x1 = Math.max(...xs) + 0.7;
  const y0 = Math.min(...ys) - 0.4, y1 = Math.max(...ys) + 0.4;
  const X = (v: number) => padL + ((v - x0) / (x1 - x0)) * (W - padL - padR);
  const Y = (v: number) => H - padB - ((v - y0) / (y1 - y0)) * (H - padT - padB);
  const rmax = Math.max(...plottable.map((p) => p.upb ?? 0), 1);

  const yTicks = Array.from({ length: 5 }, (_, i) => y0 + ((y1 - y0) * i) / 4);
  const xTicks = Array.from({ length: 5 }, (_, i) => x0 + ((x1 - x0) * i) / 4);

  return (
    <svg
      className="chart"
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label="CPR against discount yield, bubble size is UPB"
    >
      <line className="zl" x1={padL} y1={padT} x2={padL} y2={H - padB} />
      <line className="zl" x1={padL} y1={H - padB} x2={W - padR} y2={H - padB} />
      {yTicks.map((v, i) => (
        <g key={i}>
          <line className="gl" x1={padL} y1={Y(v)} x2={W - padR} y2={Y(v)} />
          <text className="ax" x={padL - 8} y={Y(v) + 3.5} textAnchor="end">{v.toFixed(1)}</text>
        </g>
      ))}
      {xTicks.map((v, i) => (
        <text key={i} className="ax" x={X(v)} y={H - padB + 16} textAnchor="middle">{v.toFixed(1)}</text>
      ))}
      {plottable.map((p) => {
        const r = 8 + Math.sqrt((p.upb ?? 0) / rmax) * 20;
        return (
          <g className="hoverable" key={p.ticker}>
            <circle cx={X(p.cpr as number)} cy={Y(p.discount_yield as number)} r={r} fill="var(--s1)" opacity={0.26} stroke="var(--surface)" strokeWidth={2}>
              <title>{`${p.name} — CPR ${p.cpr}%, discount yield ${p.discount_yield}%, UPB ${p.upb ?? '—'}`}</title>
            </circle>
            <circle cx={X(p.cpr as number)} cy={Y(p.discount_yield as number)} r={4} fill="var(--s1)" />
            <text className="dl" x={X(p.cpr as number)} y={Y(p.discount_yield as number) - r - 5} textAnchor="middle">{p.ticker}</text>
          </g>
        );
      })}
      <text className="ax" x={(W + padL) / 2} y={H - 8} textAnchor="middle">CPR — prepayment speed assumption, %</text>
      <text className="ax" x={14} y={(H - padB + padT) / 2} textAnchor="middle" transform={`rotate(-90 14 ${(H - padB + padT) / 2})`}>Discount yield, %</text>
    </svg>
  );
}
