import type { PeriodsResponse, Tab1Response, Tab2Response, Tab3Response } from './types';

// In local dev, requests to /api/* are proxied to the backend (see
// vite.config.ts). In production (e.g. Vercel) there's no dev proxy, so
// VITE_API_BASE_URL must point at the deployed backend's origin.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';

async function getJson<T>(path: string): Promise<T> {
  const url = `${API_BASE}${path}`;
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

export function fetchTab2(periodId: string): Promise<Tab2Response> {
  return getJson(`/api/tabs/2?period=${encodeURIComponent(periodId)}`);
}

export function fetchTab3(periodId: string): Promise<Tab3Response> {
  return getJson(`/api/tabs/3?period=${encodeURIComponent(periodId)}`);
}
