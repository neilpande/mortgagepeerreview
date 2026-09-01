import { useEffect, useState } from 'react';
import { fetchPeriods, fetchTab1, fetchTab2, fetchTab3 } from './api';
import { PeriodSelector } from './components/PeriodSelector';
import { Tabs, type TabId } from './components/Tabs';
import { Tab1Page } from './pages/Tab1Page';
import { Tab2Page } from './pages/Tab2Page';
import { Tab3Page } from './pages/Tab3Page';
import { Tab4Page } from './pages/Tab4Page';
import type { PeriodInfo, Tab1Response, Tab2Response, Tab3Response } from './types';

type TabData = { '1': Tab1Response | null; '2': Tab2Response | null; '3': Tab3Response | null };

const FETCHERS = {
  '1': fetchTab1,
  '2': fetchTab2,
  '3': fetchTab3,
} as const;

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('1');
  const [periods, setPeriods] = useState<PeriodInfo[]>([]);
  const [periodId, setPeriodId] = useState<string | null>(null);
  const [data, setData] = useState<TabData>({ '1': null, '2': null, '3': null });
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

  // Fetches the *active* tab's endpoint whenever the tab or the period
  // changes -- each tab requests only its own data, and (PRD Section 5/11
  // pattern, extended to more than one tab) a period switch replaces that
  // tab's entire in-memory data set at once. Tab 4 has no real endpoint yet
  // (M4 depends on Tabs 1-3 being live) so it keeps its wireframe.
  useEffect(() => {
    if (!periodId || activeTab === '4') return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    const fetcher = FETCHERS[activeTab];
    fetcher(periodId)
      .then((resp) => {
        if (!cancelled) setData((prev) => ({ ...prev, [activeTab]: resp }));
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
  }, [activeTab, periodId]);

  const activeData = activeTab === '4' ? null : data[activeTab as '1' | '2' | '3'];

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <img className="logo" src="/cloverstone-logo.png" alt="Cloverstone" />
          <div className="names">
            <div className="mark">Servicer Peer</div>
            <div className="sub">Servicer Peer Analytics Dashboard</div>
          </div>
        </div>
        <PeriodSelector periods={periods} value={periodId} onChange={setPeriodId} />
      </div>
      <Tabs active={activeTab} onSelect={setActiveTab} />
      <main>
        {activeTab === '4' && <Tab4Page />}
        {activeTab !== '4' && (
          <>
            {error && <div className="error">Couldn't load this period: {error}</div>}
            {!error && loading && !activeData && <div className="loading">Loading the peer group…</div>}
            {!error && activeTab === '1' && data['1'] && <Tab1Page data={data['1']} />}
            {!error && activeTab === '2' && data['2'] && <Tab2Page data={data['2']} />}
            {!error && activeTab === '3' && data['3'] && <Tab3Page data={data['3']} />}
          </>
        )}
      </main>
    </>
  );
}
