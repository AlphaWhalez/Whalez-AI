from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from core.ledger import IntentLedger
from core.telemetry.streamer import TelemetryStreamer

router = APIRouter(prefix="/console", tags=["console-history"])

ledger = IntentLedger()
streamer = TelemetryStreamer.get()


# Serve the console page
@router.get("/history", response_class=HTMLResponse)
def console_history_page():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
<head>
  <title>Whalez-AI Intent History</title>
  <meta charset="UTF-8">
  <style>
    body { font-family: Inter, sans-serif; background: #0f1115; color: #eee; margin: 0; padding: 2em; }
    h2 { color: #00bcd4; margin-top: 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 1em; }
    th, td { border-bottom: 1px solid #222; padding: 0.5em; font-size: 14px; }
    tr:hover { background: #181b22; }
    button { background: #00bcd4; border: none; color: black; padding: 6px 10px;
             border-radius: 6px; cursor: pointer; font-weight: 600; }
    button:hover { background: #06d1e6; }
    #stream { margin-top: 1.5em; font-size: 12px; color: #aaa; }
  </style>
</head>
<body>
  <h2>Whalez-AI: Intent Ledger Console</h2>
  <table id="ledger">
    <thead><tr><th>ID</th><th>Kind</th><th>Status</th><th>Created</th><th>Replay</th></tr></thead>
    <tbody></tbody>
  </table>
  <div id="stream">Live telemetry connected...</div>
  <script>
    async function loadHistory() {
      const res = await fetch("/intent/history?limit=100");
      const data = await res.json();
      const tbody = document.querySelector("#ledger tbody");
      tbody.innerHTML = "";
      for (const row of data.items) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.id}</td>
          <td>${row.kind}</td>
          <td>${row.status}</td>
          <td>${new Date(row.created_at * 1000).toLocaleString()}</td>
          <td><button onclick="replay('${row.id}')">Replay</button></td>`;
        tbody.appendChild(tr);
      }
    }

    async function replay(id) {
      const res = await fetch("/intent/replay/" + id, { method: "POST" });
      const data = await res.json();
      alert("Replayed " + id + " (mode: " + (data.dry_run ? "dry-run" : "live") + ")");
    }

    // Live telemetry via WebSocket
    const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/intent/ws');
    ws.onmessage = ev => {
      const msg = JSON.parse(ev.data);
      const stream = document.getElementById("stream");
      stream.innerText = "📡 " + new Date().toLocaleTimeString() + " — " + msg.event + " " + JSON.stringify(msg.data);
      if (msg.event && msg.event.startsWith("intent.")) loadHistory();
    };
    ws.onclose = () => document.getElementById("stream").innerText = "🔌 Telemetry disconnected";

    loadHistory();
  </script>
</body>
</html>
"""
    )


# Optional REST endpoint to get the current live telemetry feed
@router.get("/stream")
async def get_stream():
    return {"message": "Telemetry connected", "active": True}
