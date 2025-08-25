import { api } from './api';
import { FocusSession, SessionCreateRequest } from '@/types';

// Session API endpoints
export const createSession = async (sessionData: SessionCreateRequest): Promise<FocusSession> => {
  const response = await api.post('/sessions/', sessionData);
  return response.data;
};

export const pauseSession = async (sessionId: string): Promise<FocusSession> => {
  const response = await api.post(`/sessions/${sessionId}/pause`);
  return response.data;
};

export const resumeSession = async (sessionId: string): Promise<FocusSession> => {
  const response = await api.post(`/sessions/${sessionId}/resume`);
  return response.data;
};

export const completeSession = async (
  sessionId: string,
  completionReason = 'completed'
): Promise<FocusSession> => {
  const response = await api.post(`/sessions/${sessionId}/complete?completion_reason=${completionReason}`);
  return response.data;
};

export const getSession = async (sessionId: string): Promise<FocusSession> => {
  const response = await api.get(`/sessions/${sessionId}`);
  return response.data;
};

export const getUserSessions = async (
  userId: string,
  limit = 10
): Promise<{ sessions: FocusSession[] }> => {
  const response = await api.get(`/sessions/user/${userId}?limit=${limit}`);
  return response.data;
};

export const getActiveSession = async (userId: string): Promise<FocusSession> => {
  const response = await api.get(`/sessions/user/${userId}/active`);
  return response.data;
};

export const deleteSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/sessions/${sessionId}`);
};
