import { useSelector } from 'react-redux';
import { Clock, Coffee, Zap, CheckCircle, XCircle, Calendar } from 'lucide-react';
import { RootState } from '../../store';
import { Card, CardHeader, CardContent, Badge } from '../ui';

interface SessionHistoryProps {
  className?: string;
  maxSessions?: number;
}

const SessionHistory = ({ className = '', maxSessions = 10 }: SessionHistoryProps) => {
  const { history } = useSelector((state: RootState) => state.timer);

  // Get recent sessions (limited by maxSessions)
  const recentSessions = history.slice(0, maxSessions);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } else if (diffDays === 1) {
      return `Yesterday at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getSessionIcon = (type: string) => {
    switch (type) {
      case 'work':
        return <Clock size={16} className="text-blue-600 dark:text-blue-400" />;
      case 'shortBreak':
        return <Coffee size={16} className="text-green-600 dark:text-green-400" />;
      case 'longBreak':
        return <Zap size={16} className="text-yellow-600 dark:text-yellow-400" />;
      default:
        return <Clock size={16} className="text-gray-600 dark:text-gray-400" />;
    }
  };

  const getSessionLabel = (type: string) => {
    switch (type) {
      case 'work':
        return 'Focus Session';
      case 'shortBreak':
        return 'Short Break';
      case 'longBreak':
        return 'Long Break';
      default:
        return 'Session';
    }
  };

  const getCompletionBadge = (completed: boolean) => {
    return completed ? (
      <Badge variant="success" size="sm">
        <CheckCircle size={12} className="mr-1" />
        Completed
      </Badge>
    ) : (
      <Badge variant="danger" size="sm">
        <XCircle size={12} className="mr-1" />
        Interrupted
      </Badge>
    );
  };

  if (recentSessions.length === 0) {
    return (
      <Card className={className} variant="outlined">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Calendar size={20} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Session History
            </h3>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Clock size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              No sessions yet. Start your first timer to see your history here!
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className} variant="outlined">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar size={20} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Session History
            </h3>
          </div>
          <Badge variant="secondary" size="sm">
            {recentSessions.length} recent
          </Badge>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Your recent focus sessions and breaks
        </p>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          {recentSessions.map((session, index) => (
            <div
              key={`${session.startTime}-${index}`}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
            >
              <div className="flex items-center gap-3">
                {getSessionIcon(session.type)}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {getSessionLabel(session.type)}
                    </span>
                    {getCompletionBadge(session.completed)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {formatDate(session.startTime)}
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="font-mono text-sm font-medium text-gray-900 dark:text-white">
                  {formatTime(session.duration)}
                </div>
                {session.completed && (
                  <div className="text-xs text-green-600 dark:text-green-400">
                    Full session
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {history.length > maxSessions && (
          <div className="text-center mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {history.length - maxSessions} more sessions in your history
            </p>
          </div>
        )}

        {/* Quick Stats */}
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                {recentSessions.filter(s => s.completed).length}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Completed</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                {recentSessions.filter(s => s.type === 'work').length}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Work Sessions</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                {formatTime(recentSessions.reduce((total, s) => total + s.duration, 0))}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Total Time</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SessionHistory;
