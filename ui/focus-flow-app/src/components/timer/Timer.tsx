import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Play, Pause, Square, RotateCcw, Settings } from 'lucide-react';
import { RootState } from '../../store';
import { 
  startTimer, 
  pauseTimer, 
  resetTimer, 
  tick,
  TimerStatus 
} from '../../store/slices/timerSlice';
import { Button, Card, CardContent, Badge } from '../ui';
import { useTimerSync } from '../../hooks/useWebSocket';

interface TimerProps {
  className?: string;
}

const Timer = ({ className = '' }: TimerProps) => {
  const dispatch = useDispatch();
  const { 
    currentTime, 
    initialTime, 
    status, 
    sessionType,
    currentSession 
  } = useSelector((state: RootState) => state.timer);

  const [intervalId, setIntervalId] = useState<NodeJS.Timeout | null>(null);
  
  // WebSocket integration
  const {
    isConnected,
    notifySessionStart,
    notifySessionPause,
    notifySessionReset,
    notifySessionComplete
  } = useTimerSync();

  // Timer effect
  useEffect(() => {
    if (status === TimerStatus.RUNNING) {
      const id = setInterval(() => {
        dispatch(tick());
      }, 1000);
      setIntervalId(id);
    } else {
      if (intervalId) {
        clearInterval(intervalId);
        setIntervalId(null);
      }
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [status, dispatch]);

  // Detect session completion and notify via WebSocket
  useEffect(() => {
    if (status === TimerStatus.FINISHED && isConnected) {
      notifySessionComplete();
    }
  }, [status, isConnected, notifySessionComplete]);

  // Format time display
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Calculate progress percentage
  const progressPercentage = initialTime > 0 ? ((initialTime - currentTime) / initialTime) * 100 : 0;

  // Get session type display info
  const getSessionInfo = () => {
    switch (sessionType) {
      case 'work':
        return { label: 'Focus Time', color: 'bg-blue-500', badgeVariant: 'primary' as const };
      case 'shortBreak':
        return { label: 'Short Break', color: 'bg-green-500', badgeVariant: 'success' as const };
      case 'longBreak':
        return { label: 'Long Break', color: 'bg-yellow-500', badgeVariant: 'warning' as const };
      default:
        return { label: 'Session', color: 'bg-gray-500', badgeVariant: 'secondary' as const };
    }
  };

  const sessionInfo = getSessionInfo();

  const handleStart = () => {
    dispatch(startTimer());
    if (isConnected) {
      notifySessionStart();
    }
  };

  const handlePause = () => {
    dispatch(pauseTimer());
    if (isConnected) {
      notifySessionPause();
    }
  };

  const handleReset = () => {
    dispatch(resetTimer());
    if (isConnected) {
      notifySessionReset();
    }
  };

  const isRunning = status === TimerStatus.RUNNING;
  const isPaused = status === TimerStatus.PAUSED;
  const isFinished = status === TimerStatus.FINISHED;

  return (
    <Card className={`w-full max-w-2xl mx-auto ${className}`} variant="elevated">
      <CardContent className="p-8">
        {/* Session Type and Status */}
        <div className="flex justify-between items-center mb-8">
          <Badge variant={sessionInfo.badgeVariant} size="lg">
            {sessionInfo.label}
          </Badge>
          <div className="flex items-center gap-2">
            {currentSession && (
              <Badge variant="outline" size="sm">
                Session #{currentSession}
              </Badge>
            )}
            <Button variant="ghost" size="sm" className="text-gray-500">
              <Settings size={16} />
            </Button>
          </div>
        </div>

        {/* Timer Circle */}
        <div className="relative w-80 h-80 mx-auto mb-8">
          {/* Background Circle */}
          <div className="absolute inset-0 rounded-full border-8 border-gray-200 dark:border-gray-700"></div>
          
          {/* Progress Circle */}
          <svg 
            className="absolute inset-0 w-full h-full transform -rotate-90" 
            viewBox="0 0 320 320"
          >
            <circle
              cx="160"
              cy="160"
              r="144"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              className={`transition-all duration-1000 ease-out ${sessionInfo.color.replace('bg-', 'text-')}`}
              strokeDasharray={`${2 * Math.PI * 144}`}
              strokeDashoffset={`${2 * Math.PI * 144 * (1 - progressPercentage / 100)}`}
            />
          </svg>

          {/* Timer Display */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="text-6xl font-mono font-bold text-gray-900 dark:text-white mb-2">
              {formatTime(currentTime)}
            </div>
            <div className="text-lg text-gray-500 dark:text-gray-400">
              {isFinished ? 'Time\'s up!' : 
               isRunning ? 'Focus time' : 
               isPaused ? 'Paused' : 'Ready to start'}
            </div>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex justify-center gap-4">
          {!isRunning ? (
            <Button
              size="lg"
              onClick={handleStart}
              className="px-8"
              icon={<Play size={20} />}
              disabled={isFinished && currentTime === 0}
            >
              {isPaused ? 'Resume' : 'Start'}
            </Button>
          ) : (
            <Button
              size="lg"
              variant="secondary"
              onClick={handlePause}
              className="px-8"
              icon={<Pause size={20} />}
            >
              Pause
            </Button>
          )}

          <Button
            size="lg"
            variant="outline"
            onClick={handleReset}
            className="px-8"
            icon={<RotateCcw size={20} />}
          >
            Reset
          </Button>

          {isFinished && (
            <Button
              size="lg"
              variant="outline"
              onClick={handleReset}
              className="px-8"
              icon={<Square size={20} />}
            >
              New Session
            </Button>
          )}
        </div>

        {/* Progress Stats */}
        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {Math.round(progressPercentage)}%
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Progress</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {formatTime(initialTime - currentTime)}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Elapsed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {formatTime(currentTime)}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Remaining</div>
          </div>
        </div>

        {/* Session Info */}
        {isFinished && (
          <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg text-center">
            <p className="text-green-800 dark:text-green-200 font-medium">
              🎉 Great job! You completed a {sessionInfo.label.toLowerCase()} session.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default Timer;
