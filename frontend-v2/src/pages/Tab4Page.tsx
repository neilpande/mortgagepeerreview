import { WireframePage } from './WireframePage';

export function Tab4Page() {
  return (
    <WireframePage
      no="04"
      milestone="Milestone M4 · Not started"
      title="Benchmark Yourself"
      description="Peer median and peer range across published metrics, with a company-vs-peer-group comparison view. Depends on Tabs 1-3 being live for full metric coverage."
      columns={['Your figure', 'Peer median', 'Peer range']}
    />
  );
}
