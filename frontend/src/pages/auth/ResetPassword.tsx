import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';

interface ResetPasswordFormData {
  password: string;
  confirm_password: string;
}

const ResetPassword: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tokenValid, setTokenValid] = useState<boolean | null>(null);
  const [formData, setFormData] = useState<ResetPasswordFormData>({
    password: '',
    confirm_password: '',
  });

  useEffect(() => {
    const validateToken = async () => {
      const token = searchParams.get('token');
      if (!token) {
        setTokenValid(false);
        setError('Invalid or missing reset token');
        return;
      }

      try {
        // TODO: Implement token validation logic
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulated API call
        setTokenValid(true);
      } catch (err) {
        setTokenValid(false);
        setError('Invalid or expired reset token');
      }
    };

    validateToken();
  }, [searchParams]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = (): string | null => {
    if (formData.password !== formData.confirm_password) {
      return 'Passwords do not match';
    }
    if (formData.password.length < 8) {
      return 'Password must be at least 8 characters long';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      const token = searchParams.get('token');
      // TODO: Implement password reset logic
      await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulated API call
      navigate('/login', { state: { message: 'Password reset successful. Please login with your new password.' } });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while resetting your password');
    } finally {
      setLoading(false);
    }
  };

  if (tokenValid === null) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.default',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!tokenValid) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.default',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: '100%',
            maxWidth: 400,
          }}
        >
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Invalid Reset Link
          </Typography>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Typography variant="body1" align="center" sx={{ mb: 3 }}>
            This password reset link is invalid or has expired. Please request a new password reset link.
          </Typography>
          <Button
            fullWidth
            variant="contained"
            color="primary"
            onClick={() => navigate('/forgot-password')}
          >
            Request New Reset Link
          </Button>
        </Paper>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          width: '100%',
          maxWidth: 400,
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Reset Password
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
          Please enter your new password
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="New Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleInputChange}
            margin="normal"
            required
            autoComplete="new-password"
            helperText="Password must be at least 8 characters long"
          />
          <TextField
            fullWidth
            label="Confirm New Password"
            name="confirm_password"
            type="password"
            value={formData.confirm_password}
            onChange={handleInputChange}
            margin="normal"
            required
            autoComplete="new-password"
            helperText="Re-enter your new password"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            size="large"
            disabled={loading}
            sx={{ mt: 3 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Reset Password'}
          </Button>
        </form>
      </Paper>
    </Box>
  );
};

export default ResetPassword; 