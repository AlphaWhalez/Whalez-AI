import { useEffect, useState } from "react";
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5050";

export default function ApiStatus() {
  const [status, setStatus] = useState("checking…");
  const [tlsStatus, setTlsStatus] = useState("checking…");

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((r) => r.json())
      .then((j) => setStatus(j.status || (j.ok ? "online" : "unknown")))
      .catch(() => setStatus("offline"));
  }, []);

  useEffect(() => {
    fetch(`${API_BASE}/api/health/tls`)
      .then((r) => r.json())
      .then((j) => setTlsStatus(j.tls_ok ? "ready" : "missing"))
      .catch(() => setTlsStatus("unknown"));
  }, []);

  return (
    <ul>
      <li>
        Gateway: <strong>{status}</strong>
      </li>
      <li>
        TLS: <span id="tls-status">{tlsStatus}</span>
      </li>
    </ul>
  );
}
