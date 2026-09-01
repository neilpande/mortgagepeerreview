export function CompanyLabel({ ticker, name, note }: { ticker: string; name: string; note: string }) {
  return (
    <td className="lbl">
      <span className="co">
        <span className="tk">{ticker}</span>
        <span className="nm">
          {name}
          {note ? <em> {note}</em> : null}
        </span>
      </span>
    </td>
  );
}
