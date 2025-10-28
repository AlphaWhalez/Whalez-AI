import axios from "axios";

const api = axios.create({
  // In dev, Vite proxy forwards /api → backend:5050
  baseURL: "/api",
  timeout: 10000
});

export const getHealth = () => api.get("/health").then(r => r.data);
export const getAgents = () => api.get("/agents/status").then(r => r.data);
export const postPayrollPreview = (payload) => api.post("/payroll/preview", payload).then(r => r.data);
export default api;
