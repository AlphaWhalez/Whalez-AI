
import { useState } from "react";
import { reconcile } from "../api";

export default function DeployCard() {
  const [log, setLog] = useState([]);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true);
    try {
      const r = await reconcile([{ name: "demo-api", port: 8080, runtime: "local" }]);
      setLog(r.audit ?? []);
    } catch (e) {
      setLog([{ event: "error", details: String(e) }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="p-4 rounded-2xl shadow">
      <div className="font-semibold mb-2">Governance Deploy</div>
      <button disabled={busy} onClick={run} className="px-3 py-1 rounded bg-black/80 text-white">
        {busy ? "Deploying…" : "Reconcile & Deploy"}
      </button>
      <pre className="mt-3 text-xs overflow-auto max-h-64">{JSON.stringify(log, null, 2)}</pre>
    </div>
  );
}
