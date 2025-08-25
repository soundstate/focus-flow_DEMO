import { api } from './api';
import { SessionTemplate } from '@/types';

// Templates API endpoints
export const getUserTemplates = async (
  userId: string,
  category?: string,
  difficulty?: string
): Promise<{ templates: SessionTemplate[]; total_count: number }> => {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (difficulty) params.append('difficulty', difficulty);
  
  const response = await api.get(`/templates/users/${userId}/templates?${params.toString()}`);
  return response.data;
};

export const getTemplate = async (userId: string, templateId: string): Promise<SessionTemplate> => {
  const response = await api.get(`/templates/users/${userId}/templates/${templateId}`);
  return response.data;
};

export const createTemplate = async (userId: string, templateData: any): Promise<SessionTemplate> => {
  const response = await api.post(`/templates/users/${userId}/templates`, templateData);
  return response.data;
};

export const updateTemplate = async (
  userId: string,
  templateId: string,
  updates: any
): Promise<SessionTemplate> => {
  const response = await api.put(`/templates/users/${userId}/templates/${templateId}`, updates);
  return response.data;
};

export const deleteTemplate = async (userId: string, templateId: string): Promise<void> => {
  await api.delete(`/templates/users/${userId}/templates/${templateId}`);
};

export const getRecommendations = async (
  userId: string,
  count = 5
): Promise<{ recommendations: SessionTemplate[] }> => {
  const response = await api.get(`/templates/users/${userId}/templates/recommendations?count=${count}`);
  return response.data;
};

export const getPresets = async (userId: string) => {
  const response = await api.get(`/templates/users/${userId}/presets`);
  return response.data;
};

export const getPreset = async (userId: string, presetId: string) => {
  const response = await api.get(`/templates/users/${userId}/presets/${presetId}`);
  return response.data;
};

export const getCategories = async (): Promise<{ categories: any[] }> => {
  const response = await api.get('/templates/categories');
  return response.data;
};

export const getDifficulties = async (): Promise<{ difficulties: any[] }> => {
  const response = await api.get('/templates/difficulties');
  return response.data;
};
