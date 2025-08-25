import { store } from '../store';
import { 
  startTimer, 
  pauseTimer, 
  resetTimer,
  TimerStatus,
  SessionType
} from '../store/slices/timerSlice';
import { addNotification } from '../store/slices/uiSlice';

export interface WebSocketMessage {
  type: 'timer_update' | 'session_complete' | 'session_start' | 'session_pause' | 'session_reset' | 'notification' | 'ping';
  payload: any;
  timestamp: string;
  userId?: string | null;
}

export interface TimerSyncData {
  currentTime: number;
  initialTime: number;
  status: TimerStatus;
  sessionType: SessionType;
  currentSession: number | null;
  completedSessions: number;
  lastUpdate: string;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000; // Start with 1 second
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private isConnecting = false;
  private userId: string | null = null;
  private callbacks: Map<string, Function[]> = new Map();

  constructor() {
    this.userId = this.generateUserId();
  }

  private generateUserId(): string {
    return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  public connect(url: string = 'ws://localhost:8000/ws'): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      try {
        this.isConnecting = true;
        const wsUrl = `${url}?userId=${this.userId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = (event) => {
          console.log('WebSocket connected:', event);
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.reconnectInterval = 1000;
          this.startHeartbeat();
          
          // Send initial timer state sync
          this.syncTimerState();
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event);
          this.isConnecting = false;
          this.stopHeartbeat();
          
          // Attempt to reconnect if not a normal closure
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (event) => {
          console.error('WebSocket error:', event);
          this.isConnecting = false;
          reject(event);
        };

        // Connection timeout
        setTimeout(() => {
          if (this.isConnecting) {
            this.ws?.close();
            reject(new Error('WebSocket connection timeout'));
          }
        }, 5000);

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  private scheduleReconnect(): void {
    setTimeout(() => {
      this.reconnectAttempts++;
      this.reconnectInterval = Math.min(this.reconnectInterval * 2, 30000); // Max 30 seconds
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
      });
    }, this.reconnectInterval);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          payload: {}
        });
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    const { type, payload } = message;

    switch (type) {
      case 'timer_update':
        this.handleTimerUpdate(payload);
        break;
      
      case 'session_complete':
        this.handleSessionComplete(payload);
        break;
      
      case 'session_start':
        store.dispatch(startTimer());
        this.showNotification('Session started!', 'success');
        break;
      
      case 'session_pause':
        store.dispatch(pauseTimer());
        this.showNotification('Session paused', 'warning');
        break;
      
      case 'session_reset':
        store.dispatch(resetTimer());
        this.showNotification('Session reset', 'info');
        break;
      
      case 'notification':
        this.handleNotification(payload);
        break;
      
      default:
        console.log('Unhandled WebSocket message type:', type);
    }

    // Trigger registered callbacks
    const callbacks = this.callbacks.get(type);
    if (callbacks) {
      callbacks.forEach(callback => callback(payload, message));
    }
  }

  private handleTimerUpdate(payload: TimerSyncData): void {
    const state = store.getState();
    const currentTimerState = state.timer;

    // Only sync if the remote state is more recent
    // const remoteUpdate = new Date(payload.lastUpdate);
    // const localUpdate = new Date(); // We'll assume local is current

    // For now, we'll sync if there's a significant difference
    // In a real app, we'd have more sophisticated conflict resolution
    if (Math.abs(currentTimerState.currentTime - payload.currentTime) > 2) {
      // Significant difference detected, sync with server
      console.log('Syncing timer state from server', payload);
      
      // This would require additional actions in the timer slice
      // For now, we'll just log the sync
    }
  }

  private handleSessionComplete(payload: any): void {
    this.showNotification(
      `🎉 ${payload.sessionType} session completed!`,
      'success'
    );
    
    // Play completion sound or show visual feedback
    this.triggerCompletionEffects();
  }

  private handleNotification(payload: { message: string; type: string }): void {
    this.showNotification(payload.message, payload.type as any);
  }

  private showNotification(message: string, type: 'success' | 'error' | 'warning' | 'info'): void {
    store.dispatch(addNotification({
      title: 'Timer Sync',
      message,
      type,
      duration: 5000
    }));
  }

  private triggerCompletionEffects(): void {
    // Play a subtle completion sound
    try {
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmYdBjiK1vnSeSwGJG7A7+OZSA0PVqzn4bBbFgdHnd7qwmkfBSuAxvLXeiMFLIHG9N2NOQoUXrTp3K5VFApGnt/xxxkfBDBF2/PVeCEEL4fK7tqJNQkZdM/l5Z5Daw'); 
      audio.volume = 0.3;
      audio.play().catch(() => {}); // Ignore errors if audio can't play
    } catch (error) {
      // Ignore audio errors
    }
  }

  public send(message: Omit<WebSocketMessage, 'timestamp'>): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const fullMessage: WebSocketMessage = {
        ...message,
        timestamp: new Date().toISOString(),
        userId: this.userId
      };
      
      this.ws.send(JSON.stringify(fullMessage));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }

  public syncTimerState(): void {
    const state = store.getState();
    const timerState = state.timer;

    const syncData: TimerSyncData = {
      currentTime: timerState.currentTime,
      initialTime: timerState.initialTime,
      status: timerState.status,
      sessionType: timerState.sessionType,
      currentSession: timerState.currentSession,
      completedSessions: timerState.completedSessions,
      lastUpdate: new Date().toISOString()
    };

    this.send({
      type: 'timer_update',
      payload: syncData
    });
  }

  public notifySessionStart(): void {
    this.send({
      type: 'session_start',
      payload: {
        sessionType: store.getState().timer.sessionType,
        duration: store.getState().timer.initialTime
      }
    });
  }

  public notifySessionPause(): void {
    this.send({
      type: 'session_pause',
      payload: {
        remainingTime: store.getState().timer.currentTime
      }
    });
  }

  public notifySessionReset(): void {
    this.send({
      type: 'session_reset',
      payload: {
        sessionType: store.getState().timer.sessionType
      }
    });
  }

  public notifySessionComplete(): void {
    const timerState = store.getState().timer;
    this.send({
      type: 'session_complete',
      payload: {
        sessionType: timerState.sessionType,
        duration: timerState.initialTime,
        completedSessions: timerState.completedSessions
      }
    });
  }

  public subscribe(messageType: string, callback: Function): () => void {
    if (!this.callbacks.has(messageType)) {
      this.callbacks.set(messageType, []);
    }
    
    this.callbacks.get(messageType)!.push(callback);
    
    // Return unsubscribe function
    return () => {
      const callbacks = this.callbacks.get(messageType);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  public disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
    }
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  public getConnectionState(): string {
    if (!this.ws) return 'DISCONNECTED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING';
      case WebSocket.OPEN: return 'CONNECTED';
      case WebSocket.CLOSING: return 'CLOSING';
      case WebSocket.CLOSED: return 'DISCONNECTED';
      default: return 'UNKNOWN';
    }
  }
}

// Create a singleton instance
export const webSocketService = new WebSocketService();

export default webSocketService;
