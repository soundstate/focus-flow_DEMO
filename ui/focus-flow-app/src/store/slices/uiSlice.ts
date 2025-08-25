import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { NotificationMessage } from '@/types';

interface UIState {
  notifications: NotificationMessage[];
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'system';
  currentUser: string; // Demo user ID
}

const initialState: UIState = {
  notifications: [],
  sidebarOpen: false,
  theme: 'system',
  currentUser: 'demo_user_1',
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    addNotification: (state, action: PayloadAction<Omit<NotificationMessage, 'id'>>) => {
      const notification: NotificationMessage = {
        id: Date.now().toString(),
        ...action.payload,
      };
      state.notifications.push(notification);
    },
    
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter((n) => n.id !== action.payload);
    },
    
    clearNotifications: (state) => {
      state.notifications = [];
    },
    
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'system'>) => {
      state.theme = action.payload;
    },
    
    setCurrentUser: (state, action: PayloadAction<string>) => {
      state.currentUser = action.payload;
    },
  },
});

export const {
  addNotification,
  removeNotification,
  clearNotifications,
  toggleSidebar,
  setSidebarOpen,
  setTheme,
  setCurrentUser,
} = uiSlice.actions;

export default uiSlice.reducer;
