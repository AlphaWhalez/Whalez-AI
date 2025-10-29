import axios from "axios";

export const API_BASE = (import.meta.env.VITE_API_BASE || "http://127.0.0.1:5050");
export const endpoints = {
  health: `${API_BASE}/api/health`,
  agents: `${API_BASE}/api/agents/status`,
  payrollPreview: `${API_BASE}/api/payroll/preview`,
  version: `${API_BASE}/api/version`,
  governanceSummary: `${API_BASE}/api/governance/summary`,
  governanceAudit: `${API_BASE}/api/governance/audit`,
};

export async function getHealth() {
  const { data } = await axios.get(endpoints.health);
  return data;
}

export async function getAgents() {
  const { data } = await axios.get(endpoints.agents);
  return data;
}

export async function postPayrollPreview(payload) {
  const { data } = await axios.post(endpoints.payrollPreview, payload);
  return data;
}

export async function getGovernanceSummary() {
  const { data } = await axios.get(endpoints.governanceSummary);
  return data;
}

export async function getGovernanceAudit() {
  const { data } = await axios.get(endpoints.governanceAudit);
  return data;
}
