import React from "react";

function ServiceRow({ name, item }) {
  const notes = item.notes || {};
  const slo = notes.slo ? `p95 ${notes.slo.latency_p95_ms}ms / ${notes.slo.success_rate}%` : "—";
  return (
    <tr key={name}>
      <td>{name}</td>
      <td>{item.status}</td>
      <td>{item.strategy}</td>
      <td>{notes.version || "n/a"}</td>
      <td>{slo}</td>
    </tr>
  );
}

export default function DeployCard({ summary }) {
  if (!summary) {
    return <div className="card">Governance summary unavailable.</div>;
  }
  const services = Object.entries(summary.services || {});
  return (
    <div className="card">
      <h3>Service Governance</h3>
      <div className="meta">
        Adapter: <strong>{summary.adapter}</strong> · Mode: {summary.dry_run ? "dry-run" : "execute"}
      </div>
      <div className="meta">Last sync: {new Date(summary.timestamp * 1000).toLocaleString()}</div>
      <table className="table">
        <thead>
          <tr>
            <th>Service</th>
            <th>Status</th>
            <th>Strategy</th>
            <th>Version</th>
            <th>SLO snapshot</th>
          </tr>
        </thead>
        <tbody>
          {services.length === 0 && (
            <tr>
              <td colSpan="5">No services reconciled yet.</td>
            </tr>
          )}
          {services.map(([name, item]) => (
            <ServiceRow key={name} name={name} item={item} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
