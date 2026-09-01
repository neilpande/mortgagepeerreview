import { useState, type ReactNode } from 'react';
import { logoUrl } from '../lib/companyMeta';

function CompanyMark({ ticker }: { ticker: string }) {
  const [failed, setFailed] = useState(false);
  const url = logoUrl(ticker);

  if (!url || failed) {
    return <span className="tk">{ticker}</span>;
  }
  return (
    <span className="logo-mark">
      <img src={url} alt="" onError={() => setFailed(true)} />
    </span>
  );
}

export function CompanyLabel({
  ticker,
  name,
  note,
  filedThisPeriod = true,
  after,
}: {
  ticker: string;
  name: string;
  note: string;
  filedThisPeriod?: boolean;
  after?: ReactNode;
}) {
  return (
    <td className="lbl">
      <span className="co">
        <CompanyMark ticker={ticker} />
        <span className="nm-block">
          <span className="nm">
            {name}
            {note ? <em> {note}</em> : null}
          </span>
          {!filedThisPeriod && (
            <span className="not-filed">Has not filed for this period yet</span>
          )}
        </span>
        {after}
      </span>
    </td>
  );
}
