import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

import sessionSlice from './slices/sessionSlice';
import timerSlice from './slices/timerSlice';
import analyticsSlice from './slices/analyticsSlice';
import templatesSlice from './slices/templatesSlice';
import uiSlice from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    session: sessionSlice,
    timer: timerSlice,
    analytics: analyticsSlice,
    templates: templatesSlice,
    ui: uiSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
  devTools: import.meta.env.DEV,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
