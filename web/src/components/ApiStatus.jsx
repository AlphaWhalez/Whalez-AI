import { useEffect, useState } from "react";
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5050";

export default function ApiStatus() {
  const [status, setStatus] = useState("checking...");
  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((r) => r.json())
      .then((j) => setStatus(j.status || "unknown"))
      .catch(() => setStatus("offline"));
  }, []);
  return (
    <span>
      Gateway: <strong>{status}</strong>
    </span>
  );
}
