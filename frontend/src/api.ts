import type { PeriodsResponse, Tab1Response } from './types';

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`${url} -> ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function fetchPeriods(): Promise<PeriodsResponse> {
  return getJson('/api/periods');
}

export function fetchTab1(periodId: string): Promise<Tab1Response> {
  return getJson(`/api/tabs/1?period=${encodeURIComponent(periodId)}`);
}
