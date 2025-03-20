import React, { useState } from 'react';
import {
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
} from '@mui/material';
import { Notifications as NotificationsIcon } from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store';
import {
  selectNotifications,
  markNotificationAsRead,
} from '../../store/slices/uiSlice';

const NotificationMenu: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const notifications = useSelector(selectNotifications);
  const dispatch = useDispatch();

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = (id: string) => {
    dispatch(markNotificationAsRead(id));
    handleClose();
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <>
      <IconButton color="inherit" onClick={handleClick}>
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            maxHeight: 400,
            width: 360,
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6">Notifications</Typography>
        </Box>
        <Divider />
        {notifications.length === 0 ? (
          <MenuItem disabled>
            <Typography variant="body2">No notifications</Typography>
          </MenuItem>
        ) : (
          notifications.map((notification) => (
            <MenuItem
              key={notification.id}
              onClick={() => handleNotificationClick(notification.id)}
              sx={{
                backgroundColor: notification.read ? 'inherit' : 'action.hover',
              }}
            >
              <Box sx={{ width: '100%' }}>
                <Typography variant="body2" color="text.secondary">
                  {new Date(notification.timestamp).toLocaleString()}
                </Typography>
                <Typography variant="body1">{notification.message}</Typography>
              </Box>
            </MenuItem>
          ))
        )}
        <Divider />
        <MenuItem onClick={handleClose}>
          <Typography variant="body2" color="primary">
            Close
          </Typography>
        </MenuItem>
      </Menu>
    </>
  );
};

export default NotificationMenu; 