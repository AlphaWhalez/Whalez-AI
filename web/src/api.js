export const API_BASE = (import.meta.env.VITE_API_BASE || "http://127.0.0.1:5050");
export const endpoints = {
  health: `${API_BASE}/api/health`,
  agents: `${API_BASE}/api/agents/status`,
  payrollPreview: `${API_BASE}/api/payroll/preview`,
  version: `${API_BASE}/api/version`,
};
