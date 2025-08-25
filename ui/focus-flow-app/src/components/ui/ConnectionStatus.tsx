import { useState, useEffect } from 'react';
import { Wifi, WifiOff, AlertCircle, CheckCircle } from 'lucide-react';
import Badge from './Badge';
import useWebSocket from '../../hooks/useWebSocket';

interface ConnectionStatusProps {
  className?: string;
  showDetails?: boolean;
}

const ConnectionStatus = ({ className = '', showDetails = false }: ConnectionStatusProps) => {
  const { isConnected, connectionState, error, connect } = useWebSocket({ autoConnect: false });
  const [showRetry, setShowRetry] = useState(false);

  useEffect(() => {
    if (error) {
      setShowRetry(true);
    } else if (isConnected) {
      setShowRetry(false);
    }
  }, [error, isConnected]);

  const getStatusInfo = () => {
    switch (connectionState) {
      case 'CONNECTED':
        return {
          icon: <CheckCircle size={16} />,
          text: 'Connected',
          variant: 'success' as const,
          color: 'text-green-600 dark:text-green-400'
        };
      case 'CONNECTING':
        return {
          icon: <Wifi size={16} className="animate-pulse" />,
          text: 'Connecting...',
          variant: 'warning' as const,
          color: 'text-yellow-600 dark:text-yellow-400'
        };
      case 'DISCONNECTED':
        return {
          icon: <WifiOff size={16} />,
          text: 'Disconnected',
          variant: 'secondary' as const,
          color: 'text-gray-600 dark:text-gray-400'
        };
      case 'CLOSING':
        return {
          icon: <WifiOff size={16} />,
          text: 'Disconnecting...',
          variant: 'warning' as const,
          color: 'text-yellow-600 dark:text-yellow-400'
        };
      default:
        return {
          icon: <AlertCircle size={16} />,
          text: 'Unknown',
          variant: 'danger' as const,
          color: 'text-red-600 dark:text-red-400'
        };
    }
  };

  const handleRetryConnection = async () => {
    try {
      await connect();
    } catch (err) {
      console.error('Retry connection failed:', err);
    }
  };

  const statusInfo = getStatusInfo();

  if (!showDetails) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className={statusInfo.color}>
          {statusInfo.icon}
        </div>
        <Badge variant={statusInfo.variant} size="sm">
          {statusInfo.text}
        </Badge>
      </div>
    );
  }

  return (
    <div className={`flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg ${className}`}>
      <div className="flex items-center gap-3">
        <div className={statusInfo.color}>
          {statusInfo.icon}
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              Real-time Sync
            </span>
            <Badge variant={statusInfo.variant} size="sm">
              {statusInfo.text}
            </Badge>
          </div>
          {error && (
            <p className="text-xs text-red-600 dark:text-red-400 mt-1">
              {error.message}
            </p>
          )}
          {isConnected && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Timer sessions sync across devices
            </p>
          )}
        </div>
      </div>

      {showRetry && (
        <button
          onClick={handleRetryConnection}
          className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
};

export default ConnectionStatus;
