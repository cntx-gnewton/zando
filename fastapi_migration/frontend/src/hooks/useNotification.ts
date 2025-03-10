import { useContext } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { NotificationContext } from '../contexts/NotificationContext';
import { Notification } from '../types';

/**
 * Hook for showing notifications to the user.
 */
export const useNotification = () => {
  const context = useContext(NotificationContext);
  
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  
  const { notifications, setNotifications } = context;
  
  /**
   * Show a notification
   */
  const showNotification = (notification: Omit<Notification, 'id'>) => {
    const id = uuidv4();
    const newNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration || 5000, // Default 5 seconds
    };
    
    setNotifications((prev) => [...prev, newNotification]);
    
    // Auto-remove after duration
    setTimeout(() => {
      removeNotification(id);
    }, newNotification.duration);
    
    return id;
  };
  
  /**
   * Remove a notification by id
   */
  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id));
  };
  
  return {
    notifications,
    showNotification,
    removeNotification,
  };
};

export default useNotification;