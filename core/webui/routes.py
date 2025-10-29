from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_CONSOLE_HTML = """
<!doctype html><meta charset="utf-8">
<title>Whalez-AI • Pulse Console</title>
<style>
body{margin:0;background:#000;color:#51f851;font:14px/1.5 ui-monospace,Consolas,monospace}
#log{white-space:pre-wrap;padding:12px;height:100vh;overflow:auto}
.badge{color:#000;background:#51f851;border-radius:6px;padding:2px 6px;margin-right:8px}
</style>
<div id="log"></div>
<script>
const el = document.getElementById('log');
function print(line){el.insertAdjacentHTML('beforeend', line+'\\n'); el.scrollTop = el.scrollHeight;}
const proto = location.protocol === 'https:' ? 'wss' : 'ws';
const ws = new WebSocket(proto + '://' + location.host + '/ws/stream');
ws.onopen    = () => print('[•] connected');
ws.onclose   = () => print('[x] disconnected');
ws.onmessage = (e) => {
  let out=e.data;
  try { const o=JSON.parse(e.data); out = `[${o.t}] <span class=badge>${o.k}</span> ${typeof o.d==='string'?o.d:JSON.stringify(o.d)}` } catch{}
  print(out);
};
setInterval(()=>{ if(ws.readyState===1) ws.send('ping') }, 15000);
</script>
"""

_CALL_HTML = """
<!doctype html><meta charset="utf-8">
<title>Whalez-AI • Signal Link</title>
<style>
body{margin:0;background:#0a0a0a;color:#e6e6e6;font:14px Inter,system-ui,sans-serif;display:grid;place-items:center;height:100vh}
.card{background:#111;border:1px solid #2a2a2a;border-radius:16px;padding:20px;max-width:560px;width:92%}
.row{display:flex;gap:8px;margin-top:12px}
button{background:#2a2a2a;color:#fff;border:0;border-radius:10px;padding:10px 14px}
#log{font:13px ui-monospace,Consolas,monospace;background:#000;color:#a0ffa0;border-radius:10px;padding:10px;height:200px;overflow:auto}
</style>
<div class="card">
  <h2>Alpha-Whalez ⇄ Whalez-AI</h2>
  <p>Prototype call bridge (text channel). Voice/WebRTC attach in Phase-G expansion.</p>
  <div class="row">
    <input id="msg" placeholder="say something…" style="flex:1;padding:10px;border-radius:10px;border:1px solid #333;background:#0f0f0f;color:#fff">
    <button id="send">Send</button>
  </div>
  <div id="log"></div>
</div>
<script>
const log = document.getElementById('log');
function print(l){log.insertAdjacentHTML('beforeend',l+'\\n');log.scrollTop=log.scrollHeight;}
const proto = location.protocol === 'https:' ? 'wss' : 'ws';
const ws = new WebSocket(proto + '://' + location.host + '/ws/bridge');
ws.onopen=()=>print('[•] session open');
ws.onclose=()=>print('[x] session closed');
ws.onmessage=(e)=>print(e.data);
document.getElementById('send').onclick=()=>{
  const v=document.getElementById('msg').value;
  if(v){ ws.send(v); print('you: '+v); document.getElementById('msg').value=''; }
};
</script>
"""


@router.get("/console", response_class=HTMLResponse)
async def console_page():
    return HTMLResponse(_CONSOLE_HTML)


@router.get("/call", response_class=HTMLResponse)
async def call_page():
    return HTMLResponse(_CALL_HTML)
