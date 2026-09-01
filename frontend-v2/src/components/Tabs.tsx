export type TabId = '1' | '2' | '3' | '4';

// PRD Section 4: additional tabs are recognized as part of the overall
// dashboard but are out of scope for this phase -- clickable so the shape
// of the product is visible, each showing a basic wireframe for now.
const TAB_DEFS: { id: TabId; no: string; label: string }[] = [
  { id: '1', no: '01', label: 'MSR & Level 3' },
  { id: '2', no: '02', label: 'Flows & Economics' },
  { id: '3', no: '03', label: 'Credit & Balance Sheet' },
  { id: '4', no: '04', label: 'Benchmark Yourself' },
];

export function Tabs({ active, onSelect }: { active: TabId; onSelect: (id: TabId) => void }) {
  return (
    <div className="tabs" role="tablist">
      {TAB_DEFS.map((t) => (
        <button
          key={t.id}
          className="tab"
          role="tab"
          aria-selected={active === t.id}
          onClick={() => onSelect(t.id)}
        >
          <i>{t.no}</i>
          {t.label}
        </button>
      ))}
    </div>
  );
}
