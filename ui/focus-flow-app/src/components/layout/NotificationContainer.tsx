import { useAppSelector, useAppDispatch } from '@/store';
import { removeNotification } from '@/store/slices/uiSlice';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';
import { useEffect } from 'react';

const NotificationContainer = () => {
  const dispatch = useAppDispatch();
  const notifications = useAppSelector((state) => state.ui.notifications);

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      default:
        return <Info className="w-5 h-5 text-blue-400" />;
    }
  };

  const getBgColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 dark:bg-green-900 dark:border-green-700';
      case 'error':
        return 'bg-red-50 border-red-200 dark:bg-red-900 dark:border-red-700';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900 dark:border-yellow-700';
      default:
        return 'bg-blue-50 border-blue-200 dark:bg-blue-900 dark:border-blue-700';
    }
  };

  // Auto-dismiss notifications
  useEffect(() => {
    notifications.forEach((notification) => {
      if (notification.duration && notification.duration > 0) {
        setTimeout(() => {
          dispatch(removeNotification(notification.id));
        }, notification.duration);
      }
    });
  }, [notifications, dispatch]);

  if (notifications.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm w-full">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={clsx(
            'p-4 rounded-lg border shadow-lg transition-all duration-300 ease-in-out',
            getBgColor(notification.type)
          )}
        >
          <div className="flex items-start">
            <div className="flex-shrink-0">
              {getIcon(notification.type)}
            </div>
            <div className="ml-3 w-0 flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {notification.title}
              </p>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-300">
                {notification.message}
              </p>
              {notification.actions && (
                <div className="mt-2 flex space-x-2">
                  {notification.actions.map((action, index) => (
                    <button
                      key={index}
                      className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 font-medium"
                      onClick={() => {
                        action.action();
                        dispatch(removeNotification(notification.id));
                      }}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div className="ml-4 flex-shrink-0 flex">
              <button
                className="rounded-md inline-flex text-gray-400 hover:text-gray-500 dark:text-gray-300 dark:hover:text-gray-400"
                onClick={() => dispatch(removeNotification(notification.id))}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default NotificationContainer;
