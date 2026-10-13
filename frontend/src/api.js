import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

export const scanFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API_BASE}/scan/file`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const getScanHistory = async (limit = 100, offset = 0) => {
  const response = await axios.get(`${API_BASE}/history`, { params: { limit, offset } });
  return response.data;
};

export const getScanReport = async (scanId) => {
  const response = await axios.get(`${API_BASE}/history/${scanId}`);
  return response.data;
};

export const getQuarantinedFiles = async () => {
  const response = await axios.get(`${API_BASE}/quarantine`);
  return response.data;
};

export const restoreQuarantinedFile = async (quarantineId) => {
  const response = await axios.post(`${API_BASE}/quarantine/${quarantineId}/restore`);
  return response.data;
};

export const deleteQuarantinedFile = async (quarantineId) => {
  const response = await axios.delete(`${API_BASE}/quarantine/${quarantineId}`);
  return response.data;
};

export const getMonitorStatus = async () => {
  const response = await axios.get(`${API_BASE}/monitor/status`);
  return response.data;
};

export const startMonitor = async () => {
  const response = await axios.post(`${API_BASE}/monitor/start`);
  return response.data;
};

export const stopMonitor = async () => {
  const response = await axios.post(`${API_BASE}/monitor/stop`);
  return response.data;
};

export const getAnalyticsMetrics = async () => {
  const response = await axios.get(`${API_BASE}/analytics`);
  return response.data;
};

export const runExperiments = async () => {
  const response = await axios.post(`${API_BASE}/analytics/run-experiments`);
  return response.data;
};

export const simulateFL = async (numRounds = 5, strategy = 'FedProx') => {
  const response = await axios.get(`${API_BASE}/fl/simulate`, {
    params: { num_rounds: numRounds, strategy }
  });
  return response.data;
};

export const getSystemSettings = async () => {
  const response = await axios.get(`${API_BASE}/settings`);
  return response.data;
};

export const updateRiskWeights = async (weights) => {
  const response = await axios.post(`${API_BASE}/settings/risk-weights`, weights);
  return response.data;
};
