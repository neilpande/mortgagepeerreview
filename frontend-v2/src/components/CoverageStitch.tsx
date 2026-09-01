import type { CompanyRow } from '../types';

// Signature element: how many of this row's 5 primary fields actually
// resolved for the selected period. The dashboard's honesty about missing
// filing data is the whole point -- this makes that visible at a glance
// instead of burying it in a row of dashes.
export function CoverageStitch({ row }: { row: CompanyRow }) {
  const values = [
    row.upb.value,
    row.fair_value.value,
    row.servicing_fee_bps.value,
    row.price_bps?.value ?? null,
    row.mult?.value ?? null,
  ];
  const filled = values.filter((v) => v !== null).length;

  return (
    <span className="stitch-wrap" title={`${filled} of 5 fields resolved for this period`}>
      <span className="stitch">
        {values.map((v, i) => (
          <i key={i} className={v !== null ? 'filled' : ''} />
        ))}
      </span>
    </span>
  );
}
