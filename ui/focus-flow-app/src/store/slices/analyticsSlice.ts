import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { UserStats, DailyTrend } from '@/types';
import * as analyticsApi from '@/services/analyticsApi';

interface AnalyticsState {
  userStats: UserStats | null;
  dailyTrends: DailyTrend[];
  insights: any | null;
  loading: boolean;
  error: string | null;
}

const initialState: AnalyticsState = {
  userStats: null,
  dailyTrends: [],
  insights: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchUserStats = createAsyncThunk(
  'analytics/fetchUserStats',
  async ({ userId, days = 30 }: { userId: string; days?: number }) => {
    const response = await analyticsApi.getUserStats(userId, days);
    return response;
  }
);

export const fetchDailyTrends = createAsyncThunk(
  'analytics/fetchDailyTrends',
  async ({ userId, days = 30 }: { userId: string; days?: number }) => {
    const response = await analyticsApi.getDailyTrends(userId, days);
    return response;
  }
);

export const fetchInsights = createAsyncThunk(
  'analytics/fetchInsights',
  async ({ userId, days = 30 }: { userId: string; days?: number }) => {
    const response = await analyticsApi.getInsights(userId, days);
    return response;
  }
);

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch user stats
      .addCase(fetchUserStats.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserStats.fulfilled, (state, action) => {
        state.loading = false;
        state.userStats = action.payload;
      })
      .addCase(fetchUserStats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch user stats';
      })
      
      // Fetch daily trends
      .addCase(fetchDailyTrends.fulfilled, (state, action) => {
        state.dailyTrends = action.payload;
      })
      
      // Fetch insights
      .addCase(fetchInsights.fulfilled, (state, action) => {
        state.insights = action.payload;
      });
  },
});

export const { clearError } = analyticsSlice.actions;

export default analyticsSlice.reducer;
