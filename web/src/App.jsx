import { useEffect, useState } from "react";
import "./styles.css";
import { getHealth, getAgents } from "./api";
import HealthCard from "./components/HealthCard";
import AgentsTable from "./components/AgentsTable";
import PayrollSimulator from "./components/PayrollSimulator";
import ApiStatus from "./components/ApiStatus";

export default function App() {
  const [health, setHealth] = useState(null);
  const [agents, setAgents] = useState(null);

  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const [h, a] = await Promise.all([getHealth(), getAgents()]);
        if (!alive) return;
        setHealth(h);
        setAgents(a);
      } catch (e) {
        console.warn("Backend not reachable", e.message);
      }
    };
    tick();
    const id = setInterval(tick, 10000);
    return () => { alive = false; clearInterval(id); };
  }, []);

  return (
    <div className="wrap">
      <h1>🐋 Whalez-AI — Ops Dashboard</h1>
      <div className="card">
        <ApiStatus />
      </div>
      <HealthCard health={health} />
      <AgentsTable agents={agents} />
      <PayrollSimulator />
      <footer>Backend: /api → http://127.0.0.1:5050 (proxied by Vite)</footer>
    </div>
  );
}
