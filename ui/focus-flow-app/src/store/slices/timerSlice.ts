import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Types
export const TimerStatus = {
  IDLE: 'idle',
  RUNNING: 'running',
  PAUSED: 'paused',
  FINISHED: 'finished'
} as const;

export type TimerStatus = (typeof TimerStatus)[keyof typeof TimerStatus];

export type SessionType = 'work' | 'shortBreak' | 'longBreak';

export interface TimerSettings {
  workDuration: number; // in seconds
  shortBreakDuration: number; // in seconds
  longBreakDuration: number; // in seconds
  sessionsUntilLongBreak: number;
  autoStartBreaks: boolean;
  autoStartWork: boolean;
}

export interface SessionRecord {
  type: SessionType;
  duration: number; // actual time spent in seconds
  completed: boolean;
  startTime: string; // ISO string
  endTime?: string; // ISO string
}

export interface TimerState {
  currentTime: number; // seconds remaining
  initialTime: number; // original duration in seconds
  status: TimerStatus;
  sessionType: SessionType;
  currentSession: number | null;
  completedSessions: number;
  settings: TimerSettings;
  history: SessionRecord[];
  sessionStartTime?: string;
}

const defaultSettings: TimerSettings = {
  workDuration: 25 * 60, // 25 minutes
  shortBreakDuration: 5 * 60, // 5 minutes
  longBreakDuration: 15 * 60, // 15 minutes
  sessionsUntilLongBreak: 4,
  autoStartBreaks: false,
  autoStartWork: false,
};

const initialState: TimerState = {
  currentTime: defaultSettings.workDuration,
  initialTime: defaultSettings.workDuration,
  status: TimerStatus.IDLE,
  sessionType: 'work',
  currentSession: null,
  completedSessions: 0,
  settings: defaultSettings,
  history: [],
};

const timerSlice = createSlice({
  name: 'timer',
  initialState,
  reducers: {
    startTimer: (state) => {
      const wasIdle = state.status === TimerStatus.IDLE;
      state.status = TimerStatus.RUNNING;
      
      // Initialize session if starting fresh
      if (wasIdle || state.currentTime === state.initialTime) {
        state.currentSession = (state.currentSession || 0) + 1;
        state.sessionStartTime = new Date().toISOString();
      }
    },
    
    pauseTimer: (state) => {
      state.status = TimerStatus.PAUSED;
    },
    
    resetTimer: (state) => {
      // Save session to history if it was started
      if (state.sessionStartTime && state.currentTime !== state.initialTime) {
        const actualDuration = state.initialTime - state.currentTime;
        const sessionRecord: SessionRecord = {
          type: state.sessionType,
          duration: actualDuration,
          completed: false,
          startTime: state.sessionStartTime,
          endTime: new Date().toISOString(),
        };
        state.history.unshift(sessionRecord);
      }
      
      state.status = TimerStatus.IDLE;
      state.currentTime = state.initialTime;
      state.sessionStartTime = undefined;
    },
    
    tick: (state) => {
      if (state.status === TimerStatus.RUNNING && state.currentTime > 0) {
        state.currentTime -= 1;
        
        // Session completed
        if (state.currentTime <= 0) {
          state.status = TimerStatus.FINISHED;
          
          // Save completed session to history
          if (state.sessionStartTime) {
            const sessionRecord: SessionRecord = {
              type: state.sessionType,
              duration: state.initialTime,
              completed: true,
              startTime: state.sessionStartTime,
              endTime: new Date().toISOString(),
            };
            state.history.unshift(sessionRecord);
          }
          
          // Increment completed sessions counter for work sessions
          if (state.sessionType === 'work') {
            state.completedSessions += 1;
          }
        }
      }
    },
    
    setSessionType: (state, action: PayloadAction<SessionType>) => {
      const sessionType = action.payload;
      state.sessionType = sessionType;
      
      // Set appropriate duration
      switch (sessionType) {
        case 'work':
          state.initialTime = state.settings.workDuration;
          break;
        case 'shortBreak':
          state.initialTime = state.settings.shortBreakDuration;
          break;
        case 'longBreak':
          state.initialTime = state.settings.longBreakDuration;
          break;
      }
      
      state.currentTime = state.initialTime;
      state.status = TimerStatus.IDLE;
      state.sessionStartTime = undefined;
    },
    
    setTimerSettings: (state, action: PayloadAction<Partial<TimerSettings>>) => {
      state.settings = { ...state.settings, ...action.payload };
      
      // Update current timer if idle
      if (state.status === TimerStatus.IDLE) {
        switch (state.sessionType) {
          case 'work':
            state.initialTime = state.settings.workDuration;
            break;
          case 'shortBreak':
            state.initialTime = state.settings.shortBreakDuration;
            break;
          case 'longBreak':
            state.initialTime = state.settings.longBreakDuration;
            break;
        }
        state.currentTime = state.initialTime;
      }
    },
    
    nextSession: (state) => {
      // Determine next session type based on completed sessions
      const shouldTakeLongBreak = state.completedSessions > 0 && 
        state.completedSessions % state.settings.sessionsUntilLongBreak === 0;
      
      if (state.sessionType === 'work') {
        state.sessionType = shouldTakeLongBreak ? 'longBreak' : 'shortBreak';
        state.initialTime = shouldTakeLongBreak ? 
          state.settings.longBreakDuration : 
          state.settings.shortBreakDuration;
      } else {
        state.sessionType = 'work';
        state.initialTime = state.settings.workDuration;
      }
      
      state.currentTime = state.initialTime;
      state.status = TimerStatus.IDLE;
      state.sessionStartTime = undefined;
    },
    
    clearHistory: (state) => {
      state.history = [];
    },
  },
});

export const {
  startTimer,
  pauseTimer,
  resetTimer,
  tick,
  setSessionType,
  setTimerSettings,
  nextSession,
  clearHistory,
} = timerSlice.actions;

export default timerSlice.reducer;
