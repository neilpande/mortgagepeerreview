import { useState } from 'react';

export function ExportButton({ onExport }: { onExport: () => Promise<void> | void }) {
  const [busy, setBusy] = useState(false);

  const handleClick = async () => {
    setBusy(true);
    try {
      await onExport();
    } finally {
      setBusy(false);
    }
  };

  return (
    <button className="btn-export" onClick={handleClick} disabled={busy}>
      {busy ? 'Preparing…' : 'Download as Excel'}
    </button>
  );
}
