// Session types
export interface FocusSession {
  id: string;
  user_id: string;
  session_type: string;
  planned_duration: number;
  actual_duration?: number;
  start_time: string;
  end_time?: string;
  planned_end_time?: string;
  status: 'active' | 'paused' | 'completed' | 'cancelled';
  completion_reason?: string;
  productivity_score?: number;
  focus_quality?: 'high' | 'medium' | 'low';
  interruption_count: number;
  created_at: string;
  updated_at: string;
}

export interface SessionCreateRequest {
  user_id: string;
  session_type: string;
  planned_duration: number;
}

// Template types
export interface SessionTemplate {
  id: string;
  user_id?: string;
  name: string;
  description: string;
  category: TemplateCategory;
  difficulty: DifficultyLevel;
  session_type: string;
  duration_minutes: number;
  break_duration_minutes: number;
  is_favorite: boolean;
  is_system_template: boolean;
  usage_count: number;
  average_completion_rate: number;
  tags: string[];
  created_at?: string;
}

export type TemplateCategory = 
  | 'productivity' 
  | 'study' 
  | 'creative' 
  | 'wellness' 
  | 'work' 
  | 'personal' 
  | 'custom';

export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';

// Analytics types
export interface UserStats {
  period_days: number;
  total_sessions: number;
  completed_sessions: number;
  completion_rate: number;
  total_focus_time_minutes: number;
  completed_focus_time_minutes: number;
  average_planned_duration: number;
  average_actual_duration: number;
  average_productivity_score: number;
  total_interruptions: number;
  average_interruptions_per_session: number;
  focus_quality_distribution: Record<string, number>;
  session_type_distribution: Record<string, number>;
  current_streak_days: number;
  longest_streak_days: number;
  analysis_period: {
    start_date: string;
    end_date: string;
  };
}

export interface DailyTrend {
  date: string;
  total_sessions: number;
  completed_sessions: number;
  completion_rate: number;
  total_focus_time_minutes: number;
  average_productivity_score: number;
  total_interruptions: number;
}

// UI types
export interface NotificationMessage {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  duration?: number;
  actions?: Array<{
    label: string;
    action: () => void;
  }>;
}

export interface TimerState {
  isRunning: boolean;
  isPaused: boolean;
  timeRemaining: number; // in seconds
  totalTime: number; // in seconds
  currentSession?: FocusSession;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Error types
export interface ApiError {
  message: string;
  status: number;
  details?: any;
}
