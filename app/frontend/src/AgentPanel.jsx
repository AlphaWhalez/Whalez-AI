import React, { useEffect, useState } from "react";
import axios from "axios";

export default function AgentPanel() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    axios.get("/api/agents/status")
      .then(res => setAgents(res.data.agents))
      .catch(() => setAgents([]));
  }, []);

  const colorForStatus = (s) => {
    if (s === "active") return "text-green-400";
    if (s === "idle") return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow mt-6">
      <h2 className="text-xl mb-3">Agent Activity Panel</h2>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-gray-400 border-b border-gray-700">
            <th className="text-left py-1">Agent</th>
            <th className="text-left py-1">Status</th>
            <th className="text-left py-1">Last Heartbeat</th>
            <th className="text-left py-1">Current Task</th>
          </tr>
        </thead>
        <tbody>
          {agents.map((a, i) => (
            <tr key={i} className="border-b border-gray-700">
              <td className="py-1">{a.name}</td>
              <td className={`py-1 ${colorForStatus(a.status)}`}>{a.status}</td>
              <td className="py-1">{new Date(a.last_heartbeat).toLocaleTimeString()}</td>
              <td className="py-1 text-gray-300">{a.task}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
