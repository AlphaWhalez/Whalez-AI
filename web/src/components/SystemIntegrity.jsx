import React, { useState } from "react";
import { apiGet, apiPost } from "../api";

export default function SystemIntegrity() {
  const [status, setStatus] = useState(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const fetchStatus = async () => {
    setBusy(true);
    const res = await apiGet("/recovery/status");
    setStatus(res);
    setBusy(false);
  };

  const reconcile = async () => {
    setBusy(true);
    const res = await apiPost("/recovery/reconcile", {});
    setMsg(JSON.stringify(res));
    await fetchStatus();
    setBusy(false);
  };

  return (
    <div style={{border:'1px solid #ddd', padding:12, borderRadius:12}}>
      <h3>System Integrity</h3>
      <button disabled={busy} onClick={fetchStatus}>Check</button>{" "}
      <button disabled={busy} onClick={reconcile}>Reconcile</button>
      <pre style={{fontSize:12, whiteSpace:'pre-wrap'}}>{status ? JSON.stringify(status,null,2) : "[no data]"}</pre>
      {msg && <small>{msg}</small>}
    </div>
  );
}
