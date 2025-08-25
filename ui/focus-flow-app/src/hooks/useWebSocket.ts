import { useEffect, useState, useCallback, useRef } from 'react';
import { webSocketService, WebSocketMessage } from '../services/websocketService';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnectOnClose?: boolean;
  url?: string;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  connectionState: string;
  connect: () => Promise<void>;
  disconnect: () => void;
  send: (message: Omit<WebSocketMessage, 'timestamp'>) => void;
  subscribe: (messageType: string, callback: Function) => () => void;
  lastMessage: WebSocketMessage | null;
  error: Error | null;
}

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    autoConnect = true,
    reconnectOnClose = true,
    url = 'ws://localhost:8000/ws'
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('DISCONNECTED');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const subscriptionsRef = useRef<Map<string, () => void>>(new Map());

  // Update connection state
  const updateConnectionState = useCallback(() => {
    const state = webSocketService.getConnectionState();
    setConnectionState(state);
    setIsConnected(webSocketService.isConnected());
  }, []);

  // Connect to WebSocket
  const connect = useCallback(async () => {
    try {
      setError(null);
      await webSocketService.connect(url);
      updateConnectionState();
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Connection failed'));
      updateConnectionState();
      throw err;
    }
  }, [url, updateConnectionState]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    webSocketService.disconnect();
    updateConnectionState();
  }, [updateConnectionState]);

  // Send message
  const send = useCallback((message: Omit<WebSocketMessage, 'timestamp'>) => {
    webSocketService.send(message);
  }, []);

  // Subscribe to message types
  const subscribe = useCallback((messageType: string, callback: Function) => {
    // Wrap callback to update lastMessage state
    const wrappedCallback = (payload: any, message: WebSocketMessage) => {
      setLastMessage(message);
      callback(payload, message);
    };

    const unsubscribe = webSocketService.subscribe(messageType, wrappedCallback);
    
    // Store unsubscribe function for cleanup
    const subscriptionKey = `${messageType}_${Date.now()}`;
    subscriptionsRef.current.set(subscriptionKey, unsubscribe);
    
    // Return unsubscribe function that also cleans up our ref
    return () => {
      unsubscribe();
      subscriptionsRef.current.delete(subscriptionKey);
    };
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect().catch(err => {
        console.error('Auto-connect failed:', err);
      });
    }

    // Update connection state periodically
    const interval = setInterval(updateConnectionState, 1000);

    // Cleanup on unmount
    return () => {
      clearInterval(interval);
      
      // Clean up all subscriptions
      subscriptionsRef.current.forEach(unsubscribe => unsubscribe());
      subscriptionsRef.current.clear();
      
      if (!reconnectOnClose) {
        disconnect();
      }
    };
  }, [autoConnect, connect, disconnect, reconnectOnClose, updateConnectionState]);

  // Update connection state when service state changes
  useEffect(() => {
    const checkConnection = () => updateConnectionState();
    const interval = setInterval(checkConnection, 1000);
    return () => clearInterval(interval);
  }, [updateConnectionState]);

  return {
    isConnected,
    connectionState,
    connect,
    disconnect,
    send,
    subscribe,
    lastMessage,
    error
  };
}

// Specialized hook for timer synchronization
export function useTimerSync() {
  const { isConnected, subscribe } = useWebSocket();

  const syncTimerState = useCallback(() => {
    webSocketService.syncTimerState();
  }, []);

  const notifySessionStart = useCallback(() => {
    webSocketService.notifySessionStart();
  }, []);

  const notifySessionPause = useCallback(() => {
    webSocketService.notifySessionPause();
  }, []);

  const notifySessionReset = useCallback(() => {
    webSocketService.notifySessionReset();
  }, []);

  const notifySessionComplete = useCallback(() => {
    webSocketService.notifySessionComplete();
  }, []);

  // Subscribe to timer updates
  const subscribeToTimerUpdates = useCallback((callback: Function) => {
    return subscribe('timer_update', callback);
  }, [subscribe]);

  // Subscribe to session completions
  const subscribeToSessionComplete = useCallback((callback: Function) => {
    return subscribe('session_complete', callback);
  }, [subscribe]);

  return {
    isConnected,
    syncTimerState,
    notifySessionStart,
    notifySessionPause,
    notifySessionReset,
    notifySessionComplete,
    subscribeToTimerUpdates,
    subscribeToSessionComplete
  };
}

export default useWebSocket;
