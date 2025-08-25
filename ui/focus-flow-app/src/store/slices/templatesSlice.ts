import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { SessionTemplate } from '@/types';
import * as templatesApi from '@/services/templatesApi';

interface TemplatesState {
  templates: SessionTemplate[];
  recommendations: SessionTemplate[];
  categories: string[];
  difficulties: string[];
  loading: boolean;
  error: string | null;
}

const initialState: TemplatesState = {
  templates: [],
  recommendations: [],
  categories: [],
  difficulties: [],
  loading: false,
  error: null,
};

// Async thunks
export const fetchUserTemplates = createAsyncThunk(
  'templates/fetchUserTemplates',
  async ({ userId, category, difficulty }: { 
    userId: string; 
    category?: string; 
    difficulty?: string; 
  }) => {
    const response = await templatesApi.getUserTemplates(userId, category, difficulty);
    return response.templates;
  }
);

export const fetchTemplateRecommendations = createAsyncThunk(
  'templates/fetchRecommendations',
  async ({ userId, count = 5 }: { userId: string; count?: number }) => {
    const response = await templatesApi.getRecommendations(userId, count);
    return response.recommendations;
  }
);

export const fetchCategories = createAsyncThunk(
  'templates/fetchCategories',
  async () => {
    const response = await templatesApi.getCategories();
    return response.categories;
  }
);

const templatesSlice = createSlice({
  name: 'templates',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch user templates
      .addCase(fetchUserTemplates.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserTemplates.fulfilled, (state, action) => {
        state.loading = false;
        state.templates = action.payload;
      })
      .addCase(fetchUserTemplates.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch templates';
      })
      
      // Fetch recommendations
      .addCase(fetchTemplateRecommendations.fulfilled, (state, action) => {
        state.recommendations = action.payload;
      })
      
      // Fetch categories
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload;
      });
  },
});

export const { clearError } = templatesSlice.actions;

export default templatesSlice.reducer;
