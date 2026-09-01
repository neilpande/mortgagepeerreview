import { useEffect, useState } from 'react';
import { fetchPeriods, fetchTab1 } from './api';
import { PeriodSelector } from './components/PeriodSelector';
import { Tabs } from './components/Tabs';
import { Tab1Page } from './pages/Tab1Page';
import type { PeriodInfo, Tab1Response } from './types';

export default function App() {
  const [periods, setPeriods] = useState<PeriodInfo[]>([]);
  const [periodId, setPeriodId] = useState<string | null>(null);
  const [data, setData] = useState<Tab1Response | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Load the selectable periods once on mount.
  useEffect(() => {
    fetchPeriods()
      .then((res) => {
        setPeriods(res.periods);
        if (res.default_period_id) setPeriodId(res.default_period_id);
        else if (res.periods.length > 0) setPeriodId(res.periods[0].id);
      })
      .catch((e) => setError(String(e)));
  }, []);

  // PRD Section 5/11: selecting a period requests fresh data and replaces
  // the entire in-memory data set at once -- table and both charts update
  // together, in place, from a single response.
  useEffect(() => {
    if (!periodId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchTab1(periodId)
      .then((resp) => {
        if (!cancelled) setData(resp);
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [periodId]);

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <div className="mark">SERVICER·PEER</div>
          <div className="sub">Cloverstone · Servicer Peer Analytics Dashboard</div>
        </div>
        <PeriodSelector periods={periods} value={periodId} onChange={setPeriodId} />
      </div>
      <Tabs />
      <main>
        {error && <div className="error">Failed to load: {error}</div>}
        {!error && loading && !data && <div className="loading">Loading…</div>}
        {!error && data && <Tab1Page data={data} />}
      </main>
    </>
  );
}
