import { nf } from '../lib/format';
import type { DerivedValue, SourcedValue } from '../types';

// PRD Section 9: hovering (or keyboard-focusing) any value reveals its
// source -- tag/form/filed/accession for raw facts, or formula+inputs for
// derived fields. One reusable pair of table-cell components for both.

export function SourcedCell({ value, decimals = 1 }: { value: SourcedValue; decimals?: number }) {
  const text = nf(value.value, decimals);
  if (value.value === null) return <td className="num">—</td>;
  return (
    <td className="num">
      <span className="pv" tabIndex={0}>
        <span>{text}</span>
        <span className="card-tip">
          <span className="r"><b>Tag</b><span>{value.tag ?? '—'}</span></span>
          <span className="r"><b>Form</b><span>{value.form ?? '—'}</span></span>
          <span className="r"><b>Filed</b><span>{value.filed ?? '—'}</span></span>
          <span className="r"><b>Accn</b><span>{value.accn ?? '—'}</span></span>
          <span className="r"><b>Period end</b><span>{value.end ?? '—'}</span></span>
        </span>
      </span>
    </td>
  );
}

export function DerivedCell({
  value,
  decimals = 1,
  suffix = '',
}: {
  value: DerivedValue | null;
  decimals?: number;
  suffix?: string;
}) {
  if (value === null || value.value === null) return <td className="num">—</td>;
  const text = nf(value.value, decimals) + suffix;
  return (
    <td className="num">
      <span className="pv" tabIndex={0}>
        <span>{text}</span>
        <span className="card-tip">
          <span className="r"><b>Formula</b><span>{value.formula}</span></span>
          {Object.entries(value.inputs).map(([k, v]) => (
            <span className="r" key={k}>
              <b>{k}</b>
              <span>{v === null ? '—' : nf(v, 2)}</span>
            </span>
          ))}
        </span>
      </span>
    </td>
  );
}
