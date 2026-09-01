export function WireframePage({
  no,
  title,
  milestone,
  description,
  columns,
}: {
  no: string;
  title: string;
  milestone: string;
  description: string;
  columns: string[];
}) {
  return (
    <section className="page stack">
      <div className="wire">
        <div className="badge">
          <span>Tab {no}</span> · {milestone}
        </div>
        <h1>{title}</h1>
        <p>{description}</p>

        <div className="wire-skeleton card">
          <div className="row">
            <div className="bar" style={{ width: '90px' }} />
            {columns.map((c) => (
              <div key={c} className="bar" style={{ flex: 1, maxWidth: '110px', marginLeft: 'auto' }} />
            ))}
          </div>
          {[1, 2, 3, 4].map((r) => (
            <div className="row" key={r}>
              <div className="bar" style={{ width: '90px' }} />
              {columns.map((c) => (
                <div key={c} className="bar" style={{ flex: 1, maxWidth: '90px', marginLeft: 'auto', opacity: 0.6 }} />
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
