import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Snackbar,
} from '@mui/material';
import { RootState } from '../store';
import {
  selectTheme,
  setTheme,
  selectNotifications,
  setNotifications,
} from '../store/slices/uiSlice';

interface SettingsFormData {
  email_notifications: boolean;
  push_notifications: boolean;
  dark_mode: boolean;
  language: string;
  timezone: string;
  articles_per_page: number;
  auto_refresh_interval: number;
}

const Settings: React.FC = () => {
  const dispatch = useDispatch();
  const currentTheme = useSelector(selectTheme);
  const notifications = useSelector(selectNotifications);
  const [showSuccess, setShowSuccess] = useState(false);
  const [formData, setFormData] = useState<SettingsFormData>({
    email_notifications: true,
    push_notifications: true,
    dark_mode: currentTheme === 'dark',
    language: 'en',
    timezone: 'UTC',
    articles_per_page: 10,
    auto_refresh_interval: 5,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: e.target.type === 'checkbox' ? checked : value,
    }));
  };

  const handleThemeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTheme = e.target.checked ? 'dark' : 'light';
    dispatch(setTheme(newTheme));
    setFormData((prev) => ({
      ...prev,
      dark_mode: e.target.checked,
    }));
  };

  const handleNotificationChange = (type: 'email' | 'push') => {
    dispatch(setNotifications({ ...notifications, [type]: !notifications[type] }));
    setFormData((prev) => ({
      ...prev,
      [`${type}_notifications`]: !notifications[type],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement settings update logic
    console.log('Update settings:', formData);
    setShowSuccess(true);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Appearance
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.dark_mode}
                  onChange={handleThemeChange}
                  name="dark_mode"
                />
              }
              label="Dark Mode"
            />
            <Divider sx={{ my: 2 }} />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Language</InputLabel>
              <Select
                value={formData.language}
                label="Language"
                name="language"
                onChange={handleInputChange}
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="es">Spanish</MenuItem>
                <MenuItem value="fr">French</MenuItem>
                <MenuItem value="de">German</MenuItem>
                <MenuItem value="it">Italian</MenuItem>
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Notifications
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.email_notifications}
                  onChange={() => handleNotificationChange('email')}
                  name="email_notifications"
                />
              }
              label="Email Notifications"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={formData.push_notifications}
                  onChange={() => handleNotificationChange('push')}
                  name="push_notifications"
                />
              }
              label="Push Notifications"
            />
            <Divider sx={{ my: 2 }} />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Timezone</InputLabel>
              <Select
                value={formData.timezone}
                label="Timezone"
                name="timezone"
                onChange={handleInputChange}
              >
                <MenuItem value="UTC">UTC</MenuItem>
                <MenuItem value="EST">Eastern Time</MenuItem>
                <MenuItem value="CST">Central Time</MenuItem>
                <MenuItem value="PST">Pacific Time</MenuItem>
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Display Settings
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Articles per Page"
                  name="articles_per_page"
                  value={formData.articles_per_page}
                  onChange={handleInputChange}
                  inputProps={{ min: 5, max: 50 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Auto-refresh Interval (minutes)"
                  name="auto_refresh_interval"
                  value={formData.auto_refresh_interval}
                  onChange={handleInputChange}
                  inputProps={{ min: 1, max: 60 }}
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            fullWidth
          >
            Save Settings
          </Button>
        </Grid>
      </Grid>

      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={() => setShowSuccess(false)}
      >
        <Alert
          onClose={() => setShowSuccess(false)}
          severity="success"
          sx={{ width: '100%' }}
        >
          Settings updated successfully!
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings; 