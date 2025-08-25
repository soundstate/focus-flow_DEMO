import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { FocusSession, SessionCreateRequest } from '@/types';
import * as sessionApi from '@/services/sessionApi';

interface SessionState {
  sessions: FocusSession[];
  currentSession: FocusSession | null;
  activeSession: FocusSession | null;
  loading: boolean;
  error: string | null;
}

const initialState: SessionState = {
  sessions: [],
  currentSession: null,
  activeSession: null,
  loading: false,
  error: null,
};

// Async thunks
export const createSession = createAsyncThunk(
  'session/create',
  async (sessionData: SessionCreateRequest) => {
    const response = await sessionApi.createSession(sessionData);
    return response;
  }
);

export const pauseSession = createAsyncThunk(
  'session/pause',
  async (sessionId: string) => {
    const response = await sessionApi.pauseSession(sessionId);
    return response;
  }
);

export const resumeSession = createAsyncThunk(
  'session/resume',
  async (sessionId: string) => {
    const response = await sessionApi.resumeSession(sessionId);
    return response;
  }
);

export const completeSession = createAsyncThunk(
  'session/complete',
  async ({ sessionId, completionReason }: { sessionId: string; completionReason?: string }) => {
    const response = await sessionApi.completeSession(sessionId, completionReason);
    return response;
  }
);

export const fetchUserSessions = createAsyncThunk(
  'session/fetchUserSessions',
  async ({ userId, limit = 10 }: { userId: string; limit?: number }) => {
    const response = await sessionApi.getUserSessions(userId, limit);
    return response.sessions;
  }
);

export const fetchActiveSession = createAsyncThunk(
  'session/fetchActive',
  async (userId: string) => {
    const response = await sessionApi.getActiveSession(userId);
    return response;
  }
);

const sessionSlice = createSlice({
  name: 'session',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentSession: (state, action: PayloadAction<FocusSession | null>) => {
      state.currentSession = action.payload;
    },
    updateSessionLocally: (state, action: PayloadAction<Partial<FocusSession> & { id: string }>) => {
      const { id, ...updates } = action.payload;
      
      // Update in sessions array
      const sessionIndex = state.sessions.findIndex((s) => s.id === id);
      if (sessionIndex !== -1) {
        state.sessions[sessionIndex] = { ...state.sessions[sessionIndex], ...updates };
      }
      
      // Update current session if it matches
      if (state.currentSession?.id === id) {
        state.currentSession = { ...state.currentSession, ...updates };
      }
      
      // Update active session if it matches
      if (state.activeSession?.id === id) {
        state.activeSession = { ...state.activeSession, ...updates };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Create session
      .addCase(createSession.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createSession.fulfilled, (state, action) => {
        state.loading = false;
        state.currentSession = action.payload;
        state.activeSession = action.payload;
        state.sessions.unshift(action.payload);
      })
      .addCase(createSession.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create session';
      })
      
      // Pause session
      .addCase(pauseSession.fulfilled, (state, action) => {
        const updatedSession = action.payload;
        const sessionIndex = state.sessions.findIndex((s) => s.id === updatedSession.id);
        
        if (sessionIndex !== -1) {
          state.sessions[sessionIndex] = updatedSession;
        }
        
        if (state.currentSession?.id === updatedSession.id) {
          state.currentSession = updatedSession;
        }
        
        if (state.activeSession?.id === updatedSession.id) {
          state.activeSession = updatedSession;
        }
      })
      
      // Resume session
      .addCase(resumeSession.fulfilled, (state, action) => {
        const updatedSession = action.payload;
        const sessionIndex = state.sessions.findIndex((s) => s.id === updatedSession.id);
        
        if (sessionIndex !== -1) {
          state.sessions[sessionIndex] = updatedSession;
        }
        
        if (state.currentSession?.id === updatedSession.id) {
          state.currentSession = updatedSession;
        }
        
        if (state.activeSession?.id === updatedSession.id) {
          state.activeSession = updatedSession;
        }
      })
      
      // Complete session
      .addCase(completeSession.fulfilled, (state, action) => {
        const updatedSession = action.payload;
        const sessionIndex = state.sessions.findIndex((s) => s.id === updatedSession.id);
        
        if (sessionIndex !== -1) {
          state.sessions[sessionIndex] = updatedSession;
        }
        
        if (state.currentSession?.id === updatedSession.id) {
          state.currentSession = updatedSession;
        }
        
        // Clear active session when completed
        if (state.activeSession?.id === updatedSession.id) {
          state.activeSession = null;
        }
      })
      
      // Fetch user sessions
      .addCase(fetchUserSessions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserSessions.fulfilled, (state, action) => {
        state.loading = false;
        state.sessions = action.payload;
      })
      .addCase(fetchUserSessions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch sessions';
      })
      
      // Fetch active session
      .addCase(fetchActiveSession.fulfilled, (state, action) => {
        state.activeSession = action.payload;
      })
      .addCase(fetchActiveSession.rejected, (state) => {
        state.activeSession = null; // No active session found
      });
  },
});

export const { clearError, setCurrentSession, updateSessionLocally } = sessionSlice.actions;

export default sessionSlice.reducer;
