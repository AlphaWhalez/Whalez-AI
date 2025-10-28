import React from "react";
export default function HealthCard({ data }) {
  if (!data) return <div className="card">No data</div>;
  const m = data.metrics || {};
  return (
    <div className="card">
      <h3>Gateway Health</h3>
      <div>Status: <b>{data.status}</b></div>
      <div>CPU: {m.cpu_percent}% • MEM: {m.memory_mb} MB • Host: {m.hostname}</div>
      <div>Uptime: {m.uptime_sec}s • Blocks: {m.ledger_indexed}</div>
    </div>
  );
}
