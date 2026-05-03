export default function AlertBadge({ status }) {
  if (status === 'RUPTURE') return <span className="badge badge-danger">⚠ Rupture</span>;
  if (status === 'FLUX_TENDU') return <span className="badge badge-warning">⟳ Flux Tendu</span>;
  if (status === 'SUFFISANT') return <span className="badge badge-success">✓ Suffisant</span>;
  if (status === 'SURSTOCK') return <span className="badge badge-info">↑ Sur-Stock</span>;
  return <span className="badge badge-muted">{status}</span>;
}
