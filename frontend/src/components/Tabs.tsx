// PRD Section 4: additional tabs are recognized as part of the overall
// dashboard but are out of scope for this phase.
const TAB_DEFS = [
  { no: '01', label: 'MSR & Level 3', enabled: true },
  { no: '02', label: 'Flows & Economics', enabled: false },
  { no: '03', label: 'Credit & Balance Sheet', enabled: false },
  { no: '04', label: 'Benchmark Yourself', enabled: false },
];

export function Tabs() {
  return (
    <div className="tabs" role="tablist">
      {TAB_DEFS.map((t) => (
        <button
          key={t.no}
          className="tab"
          role="tab"
          aria-selected={t.enabled}
          disabled={!t.enabled}
          title={t.enabled ? undefined : 'Out of scope for this phase'}
        >
          <i>{t.no}</i>
          {t.label}
        </button>
      ))}
    </div>
  );
}
