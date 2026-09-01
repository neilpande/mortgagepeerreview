// Local logo files, served from public/logos/ (added straight to the repo
// rather than fetched from a third party). Kept separate from the
// backend's companies.py since it's presentation-only, not filing/CIK data.
export const COMPANY_LOGOS: Record<string, string> = {
  RKT: '/logos/rkt.png',
  RITM: '/logos/ritm.png',
  PFSI: '/logos/pfsi.png',
  ONIT: '/logos/onit.jpeg',
  PMT: '/logos/pmt.png',
  NLY: '/logos/nly.png',
  TWO: '/logos/two.png',
};

export function logoUrl(ticker: string): string | null {
  return COMPANY_LOGOS[ticker] ?? null;
}
