import api from './config';

export interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  email?: string;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
}

export interface UserSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  dark_mode: boolean;
  language: string;
  timezone: string;
  articles_per_page: number;
  auto_refresh_interval: number;
}

const userService = {
  updateProfile: async (data: UpdateProfileData): Promise<UserProfile> => {
    const response = await api.put<UserProfile>('/users/profile', data);
    return response.data;
  },

  changePassword: async (data: ChangePasswordData): Promise<void> => {
    await api.put('/users/password', data);
  },

  getSettings: async (): Promise<UserSettings> => {
    const response = await api.get<UserSettings>('/users/settings');
    return response.data;
  },

  updateSettings: async (data: Partial<UserSettings>): Promise<UserSettings> => {
    const response = await api.put<UserSettings>('/users/settings', data);
    return response.data;
  },

  deleteAccount: async (): Promise<void> => {
    await api.delete('/users/account');
  },
};

export default userService; 