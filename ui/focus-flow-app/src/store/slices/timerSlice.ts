import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { TimerState } from '@/types';

const initialState: TimerState = {
  isRunning: false,
  isPaused: false,
  timeRemaining: 0,
  totalTime: 0,
  currentSession: undefined,
};

const timerSlice = createSlice({
  name: 'timer',
  initialState,
  reducers: {
    startTimer: (state, action: PayloadAction<{ duration: number; session?: any }>) => {
      state.isRunning = true;
      state.isPaused = false;
      state.totalTime = action.payload.duration * 60; // Convert to seconds
      state.timeRemaining = state.totalTime;
      state.currentSession = action.payload.session;
    },
    
    pauseTimer: (state) => {
      state.isRunning = false;
      state.isPaused = true;
    },
    
    resumeTimer: (state) => {
      state.isRunning = true;
      state.isPaused = false;
    },
    
    stopTimer: (state) => {
      state.isRunning = false;
      state.isPaused = false;
      state.timeRemaining = 0;
      state.totalTime = 0;
      state.currentSession = undefined;
    },
    
    tick: (state) => {
      if (state.isRunning && state.timeRemaining > 0) {
        state.timeRemaining -= 1;
        
        // Auto-complete when timer reaches 0
        if (state.timeRemaining <= 0) {
          state.isRunning = false;
          state.isPaused = false;
        }
      }
    },
    
    setTimeRemaining: (state, action: PayloadAction<number>) => {
      state.timeRemaining = action.payload;
    },
    
    resetTimer: (state) => {
      state.timeRemaining = state.totalTime;
      state.isRunning = false;
      state.isPaused = false;
    },
  },
});

export const {
  startTimer,
  pauseTimer,
  resumeTimer,
  stopTimer,
  tick,
  setTimeRemaining,
  resetTimer,
} = timerSlice.actions;

export default timerSlice.reducer;
