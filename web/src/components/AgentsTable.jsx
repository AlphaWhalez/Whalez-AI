import React from "react";

export default function AgentsTable({ agents }) {
  if (!agents?.agents) return null;
  return (
    <div className="card">
      <h3>Agents</h3>
      <table>
        <thead>
          <tr><th>Name</th><th>Status</th><th>Task</th><th>Last Heartbeat</th></tr>
        </thead>
        <tbody>
          {agents.agents.map((a,i)=>(
            <tr key={i}>
              <td>{a.name}</td>
              <td>{a.status}</td>
              <td>{a.task}</td>
              <td>{a.last_heartbeat}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
