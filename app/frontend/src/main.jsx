import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import AgentPanel from "./AgentPanel";

function Dashboard() {
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState("Loading...");

  useEffect(() => {
    axios.get("/api/ping")
      .then(res => setStatus(res.data.status))
      .catch(() => setStatus("Offline"));
    axios.get("/api/health")
      .then(res => setLogs(res.data.recent_logs))
      .catch(() => setLogs([]));
  }, []);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-3xl font-bold text-center">🐋 Whalez-AI Dashboard</h1>
      <p className="text-center text-green-400">{status}</p>

      <div className="bg-gray-800 p-4 rounded-lg shadow">
        <h2 className="text-xl mb-2">Runtime Health Metrics</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={logs}>
            <Line type="monotone" dataKey="metrics.cpu_percent" stroke="#34d399" name="CPU %" />
            <Line type="monotone" dataKey="metrics.memory_percent" stroke="#60a5fa" name="Memory %" />
            <XAxis dataKey="timestamp" hide />
            <YAxis />
            <Tooltip />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <AgentPanel />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<Dashboard />);
