import React, { useState } from "react";
import { postPayrollPreview } from "../api";

export default function PayrollSimulator() {
  const [total, setTotal] = useState(500);
  const [perf, setPerf] = useState({
    founder: 1.0, whalez_ai_core: 0.9, head_coaches: 1.1,
    vip_users: 1.0, sub_model_ais: 0.95, validator_council: 1.05, general_users: 0.8
  });
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true);
    try {
      const data = await postPayrollPreview({ total_pltr: Number(total), performance: perf });
      setResult(data.preview);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card">
      <h3>Payroll Preview</h3>
      <div className="row">
        <label>Total PLTR</label>
        <input type="number" value={total} onChange={e=>setTotal(e.target.value)} />
        <button onClick={run} disabled={busy}>{busy ? "Running..." : "Preview"}</button>
      </div>
      <details>
        <summary>Tuning (performance multipliers)</summary>
        {Object.keys(perf).map(k=>(
          <div className="row" key={k}>
            <label style={{width:180}}>{k}</label>
            <input type="number" step="0.05" value={perf[k]} onChange={e=>setPerf({...perf, [k]: Number(e.target.value)})}/>
          </div>
        ))}
      </details>
      {result && (
        <div className="grid">
          {Object.entries(result).map(([k,v])=>(
            <div key={k}><strong>{k}:</strong> {v}</div>
          ))}
        </div>
      )}
    </div>
  );
}
