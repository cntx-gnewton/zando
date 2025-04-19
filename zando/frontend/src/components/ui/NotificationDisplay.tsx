import React from 'react';
import { FaCheckCircle, FaExclamationTriangle, FaInfoCircle, FaTimes } from 'react-icons/fa';
import { useNotification } from '../../hooks/useNotification';
import { Notification } from '../../types';

const getNotificationColor = (type: Notification['type']) => {
  switch (type) {
    case 'success':
      return 'bg-green-100 border-green-500 text-green-800';
    case 'error':
      return 'bg-red-100 border-red-500 text-red-800';
    case 'warning':
      return 'bg-yellow-100 border-yellow-500 text-yellow-800';
    case 'info':
    default:
      return 'bg-blue-100 border-blue-500 text-blue-800';
  }
};

const getNotificationIcon = (type: Notification['type']) => {
  switch (type) {
    case 'success':
      return <FaCheckCircle className="text-green-500" />;
    case 'error':
      return <FaExclamationTriangle className="text-red-500" />;
    case 'warning':
      return <FaExclamationTriangle className="text-yellow-500" />;
    case 'info':
    default:
      return <FaInfoCircle className="text-blue-500" />;
  }
};

const NotificationDisplay: React.FC = () => {
  const { notifications, removeNotification } = useNotification();
  
  if (notifications.length === 0) {
    return null;
  }
  
  return (
    <div className="fixed top-4 right-4 z-50 w-80 space-y-2 max-h-screen overflow-y-auto p-2">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`flex items-start p-4 mb-2 border-l-4 rounded shadow-md ${getNotificationColor(notification.type)}`}
        >
          <div className="flex-shrink-0 mt-1 mr-3">
            {getNotificationIcon(notification.type)}
          </div>
          <div className="flex-1">
            <h3 className="font-medium">{notification.message}</h3>
            {notification.details && (
              <p className="mt-1 text-sm opacity-90">{notification.details}</p>
            )}
          </div>
          <button
            onClick={() => removeNotification(notification.id)}
            className="flex-shrink-0 ml-2 p-1 rounded-full hover:bg-gray-200 transition-colors"
          >
            <FaTimes />
          </button>
        </div>
      ))}
    </div>
  );
};

export default NotificationDisplay;