// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  auth: {
    signin: `${API_BASE_URL}/api/v1/auth/signin`,
    signup: `${API_BASE_URL}/api/v1/auth/signup`,
    signout: `${API_BASE_URL}/api/v1/auth/signout`,
    refresh: `${API_BASE_URL}/api/v1/auth/refresh`,
    forgotPassword: `${API_BASE_URL}/api/v1/auth/forgot-password`,
    me: `${API_BASE_URL}/api/v1/auth/me`,
  },
  members: `${API_BASE_URL}/api/v1/members`,
  transactions: `${API_BASE_URL}/api/v1/transactions`,
  campaigns: `${API_BASE_URL}/api/v1/campaigns`,
  ai: {
    recommendations: `${API_BASE_URL}/api/v1/ai/recommendations`,
    launch: `${API_BASE_URL}/api/v1/ai/launch`,
    estimate: `${API_BASE_URL}/api/v1/ai/campaign/estimate`,
    messageGenerate: `${API_BASE_URL}/api/v1/ai/message/generate`,
    segmentation: `${API_BASE_URL}/api/v1/ai/segmentation/run`,
    behaviorAnalyze: `${API_BASE_URL}/api/v1/ai/behavior/analyze`,
    behaviorAlerts: `${API_BASE_URL}/api/v1/ai/behavior/alerts`,
    campaignMetrics: (id: string) => `${API_BASE_URL}/api/v1/ai/campaign/${id}/metrics`,
    campaignStatus: (id: string) => `${API_BASE_URL}/api/v1/ai/campaign/${id}/status`,
  },
  analytics: {
    campaigns: `${API_BASE_URL}/api/v1/analytics/campaigns`,
  },
};

export { API_BASE_URL };
