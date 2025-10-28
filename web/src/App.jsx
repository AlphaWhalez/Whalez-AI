import React, { useEffect, useState } from "react";
import axios from "axios";
const API = import.meta.env.VITE_API_BASE;

export default function App() {
  const [health, setHealth] = useState(null);
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    axios.get(`${API}/api/health`).then(r => setHealth(r.data)).catch(()=>{});
    axios.get(`${API}/api/agents/status`).then(r => setAgents(r.data.agents||[])).catch(()=>{});
  }, []);

  return (
    <div style={{fontFamily:"Inter, system-ui", background:"#0b1120", minHeight:"100vh", color:"#fff", padding:"32px"}}>
      <h2 style={{color:"#22d3ee"}}>🐋 Whalez-AI Web Console</h2>
      <section style={{marginTop:16}}>
        <h3 style={{color:"#a5f3fc"}}>Health</h3>
        <pre style={{background:"#0f172a", padding:16, border:"1px solid #22d3ee", borderRadius:12}}>
          {JSON.stringify(health, null, 2)}
        </pre>
      </section>
      <section style={{marginTop:16}}>
        <h3 style={{color:"#a5f3fc"}}>Agents</h3>
        <pre style={{background:"#0f172a", padding:16, border:"1px solid #22d3ee", borderRadius:12}}>
          {JSON.stringify(agents, null, 2)}
        </pre>
      </section>
    </div>
  );
}

