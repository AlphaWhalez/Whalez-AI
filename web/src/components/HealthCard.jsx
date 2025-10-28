import React from "react";

export default function HealthCard({ health }) {
  if (!health) return null;
  const m = health.metrics || {};
  return (
    <div className="card">
      <h3>Gateway Health</h3>
      <div className="grid">
        <div><strong>Status:</strong> {health.status}</div>
        <div><strong>CPU%:</strong> {m.cpu_percent}</div>
        <div><strong>Memory(MB):</strong> {m.memory_mb}</div>
        <div><strong>Host:</strong> {m.hostname}</div>
        <div><strong>Uptime(s):</strong> {m.uptime_sec}</div>
      </div>
    </div>
  );
}
