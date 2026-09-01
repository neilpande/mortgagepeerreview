import type { PeriodInfo } from '../types';

export function PeriodSelector({
  periods,
  value,
  onChange,
}: {
  periods: PeriodInfo[];
  value: string | null;
  onChange: (periodId: string) => void;
}) {
  return (
    <div className="ctl">
      <label htmlFor="period-select">Period</label>
      <select
        id="period-select"
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        disabled={periods.length === 0}
      >
        {periods.map((p) => (
          <option key={p.id} value={p.id}>
            {p.label}
          </option>
        ))}
      </select>
    </div>
  );
}
