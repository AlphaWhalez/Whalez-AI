import { useEffect, useState } from "react";

export default function SecurityStatus() {
  const [status, setStatus] = useState("…");

  useEffect(() => {
    const controller = new AbortController();
    fetch("/security/auth/verify", {
      headers: { Authorization: "Bearer invalid" },
      signal: controller.signal,
    })
      .then((res) => setStatus(res.status === 401 ? "secured" : "open"))
      .catch(() => setStatus("unknown"));

    return () => controller.abort();
  }, []);

  return (
    <div className="p-4 rounded-2xl shadow">
      <div className="font-semibold mb-1">Security</div>
      <div className="text-sm text-gray-600">Bearer middleware check</div>
      <div className="mt-2 text-lg font-bold">{status}</div>
    </div>
  );
}
