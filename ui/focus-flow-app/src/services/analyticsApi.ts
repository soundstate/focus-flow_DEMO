import { api } from './api';
import { UserStats, DailyTrend } from '@/types';

// Analytics API endpoints
export const getUserStats = async (userId: string, days = 30): Promise<UserStats> => {
  const response = await api.get(`/analytics/users/${userId}/stats?days=${days}`);
  return response.data;
};

export const getDailyTrends = async (userId: string, days = 30): Promise<DailyTrend[]> => {
  const response = await api.get(`/analytics/users/${userId}/trends/daily?days=${days}`);
  return response.data;
};

export const getHourlyPatterns = async (userId: string, days = 30) => {
  const response = await api.get(`/analytics/users/${userId}/patterns/hourly?days=${days}`);
  return response.data;
};

export const getSessionTypePerformance = async (userId: string, days = 30) => {
  const response = await api.get(`/analytics/users/${userId}/performance/types?days=${days}`);
  return response.data;
};

export const getQualityInsights = async (userId: string, days = 30) => {
  const response = await api.get(`/analytics/users/${userId}/quality/insights?days=${days}`);
  return response.data;
};

export const getInsights = async (userId: string, days = 30) => {
  const response = await api.get(`/analytics/users/${userId}/insights?days=${days}`);
  return response.data;
};
