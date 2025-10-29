import React from "react";

export default function AuditLog({ events }) {
  if (!events || events.length === 0) {
    return <div className="card">No audit events yet.</div>;
  }
  return (
    <div className="card">
      <h3>Deployment Audit Trail</h3>
      <ul className="audit-list">
        {events.map((evt, idx) => (
          <li key={`${evt.ts}-${idx}`}>
            <div>
              <strong>{evt.service}</strong> · {evt.event}
            </div>
            <div className="meta">{new Date(evt.ts * 1000).toLocaleString()}</div>
            <pre>{JSON.stringify(evt.details, null, 2)}</pre>
          </li>
        ))}
      </ul>
    </div>
  );
}
