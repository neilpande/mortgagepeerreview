// Company domains for logo lookup (via Clearbit's public logo API,
// https://logo.clearbit.com/<domain> -- no auth, standard practice for
// exactly this use case). Kept separate from the backend's companies.py
// since it's presentation-only, not filing/CIK data.
export const COMPANY_DOMAINS: Record<string, string> = {
  RKT: 'rocketcompanies.com',
  RITM: 'rithmcap.com',
  PFSI: 'pennymacfinancial.com',
  ONIT: 'onitygroup.com',
  PMT: 'pennymac-reit.com',
  NLY: 'annaly.com',
  TWO: 'twoharborsinvestment.com',
};

export function logoUrl(ticker: string): string | null {
  const domain = COMPANY_DOMAINS[ticker];
  return domain ? `https://logo.clearbit.com/${domain}` : null;
}
