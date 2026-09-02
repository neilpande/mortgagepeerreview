import type { PeriodsResponse, Tab1Response, Tab2Response, Tab3Response } from './types';

// Same-origin in both local dev (Vite proxies /api/* to the local
// FastAPI dev server, see vite.config.ts) and production (Vercel serves
// the API as functions from api/* alongside this static build) -- no
// separate backend origin to configure.

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`${path} -> ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function fetchPeriods(): Promise<PeriodsResponse> {
  return getJson('/api/periods');
}

export function fetchTab1(periodId: string): Promise<Tab1Response> {
  return getJson(`/api/tabs/1?period=${encodeURIComponent(periodId)}`);
}

export function fetchTab2(periodId: string): Promise<Tab2Response> {
  return getJson(`/api/tabs/2?period=${encodeURIComponent(periodId)}`);
}

export function fetchTab3(periodId: string): Promise<Tab3Response> {
  return getJson(`/api/tabs/3?period=${encodeURIComponent(periodId)}`);
}
