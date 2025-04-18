import React from 'react';
import { 
  FaCheckCircle, 
  FaExclamationTriangle, 
  FaInfoCircle, 
  FaTimes
} from 'react-icons/fa';
import { useNotification } from '../../hooks/useNotification';
import { Notification } from '../../types';

const NotificationItem: React.FC<{
  notification: Notification;
  onClose: (id: string) => void;
}> = ({ notification, onClose }) => {
  const { id, type, message, details } = notification;
  
  // Define color schemes for different notification types
  const notificationStyles = {
    success: {
      container: 'bg-green-50 border-green-300',
      icon: <FaCheckCircle className="text-green-500 flex-shrink-0" />,
      title: 'text-green-800',
      message: 'text-green-700',
      closeButton: 'text-green-500 hover:bg-green-100'
    },
    error: {
      container: 'bg-red-50 border-red-300',
      icon: <FaExclamationTriangle className="text-red-500 flex-shrink-0" />,
      title: 'text-red-800',
      message: 'text-red-700',
      closeButton: 'text-red-500 hover:bg-red-100'
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-300',
      icon: <FaExclamationTriangle className="text-yellow-600 flex-shrink-0" />,
      title: 'text-yellow-800',
      message: 'text-yellow-700',
      closeButton: 'text-yellow-500 hover:bg-yellow-100'
    },
    info: {
      container: 'bg-blue-50 border-blue-300',
      icon: <FaInfoCircle className="text-blue-500 flex-shrink-0" />,
      title: 'text-blue-800',
      message: 'text-blue-700',
      closeButton: 'text-blue-500 hover:bg-blue-100'
    }
  };
  
  const style = notificationStyles[type];
  
  return (
    <div className={`max-w-sm w-full shadow-lg rounded-lg pointer-events-auto border ${style.container}`}>
      <div className="p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            {style.icon}
          </div>
          <div className="ml-3 w-0 flex-1 pt-0.5">
            <p className={`text-sm font-medium ${style.title}`}>{message}</p>
            {details && (
              <p className={`mt-1 text-sm ${style.message}`}>{details}</p>
            )}
          </div>
          <div className="ml-4 flex-shrink-0 flex">
            <button
              className={`bg-transparent rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none ${style.closeButton}`}
              onClick={() => onClose(id)}
            >
              <span className="sr-only">Close</span>
              <FaTimes className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const Notifications: React.FC = () => {
  const { notifications, removeNotification } = useNotification();
  
  if (notifications.length === 0) {
    return null;
  }
  
  return (
    <div className="fixed top-0 right-0 p-4 w-full sm:w-auto z-50 pointer-events-none">
      <div className="space-y-4">
        {notifications.map(notification => (
          <div key={notification.id} className="transition transform duration-300 ease-in-out pointer-events-auto">
            <NotificationItem
              notification={notification}
              onClose={removeNotification}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Notifications;