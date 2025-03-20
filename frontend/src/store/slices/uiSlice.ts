import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../index';

interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: Notification[];
  loading: {
    [key: string]: boolean;
  };
  errors: {
    [key: string]: string | null;
  };
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  read: boolean;
}

const initialState: UIState = {
  sidebarOpen: true,
  theme: 'light',
  notifications: [],
  loading: {},
  errors: {},
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id'>>) => {
      const id = Date.now().toString();
      state.notifications.push({ ...action.payload, id });
    },
    markNotificationAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification) {
        notification.read = true;
      }
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    setLoading: (state, action: PayloadAction<{ key: string; value: boolean }>) => {
      state.loading[action.payload.key] = action.payload.value;
    },
    setError: (state, action: PayloadAction<{ key: string; value: string | null }>) => {
      state.errors[action.payload.key] = action.payload.value;
    },
    clearErrors: (state) => {
      state.errors = {};
    },
  },
});

export const {
  toggleSidebar,
  setTheme,
  addNotification,
  markNotificationAsRead,
  clearNotifications,
  setLoading,
  setError,
  clearErrors,
} = uiSlice.actions;

export const selectSidebarOpen = (state: RootState) => state.ui.sidebarOpen;
export const selectTheme = (state: RootState) => state.ui.theme;
export const selectNotifications = (state: RootState) => state.ui.notifications;
export const selectLoading = (key: string) => (state: RootState) => state.ui.loading[key];
export const selectError = (key: string) => (state: RootState) => state.ui.errors[key];

export default uiSlice.reducer; 