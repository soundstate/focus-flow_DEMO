import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Check, Clock, Coffee, Zap } from 'lucide-react';
import { RootState } from '../../store';
import { setTimerSettings, TimerStatus } from '../../store/slices/timerSlice';
import { Button, Card, CardHeader, CardContent, Input, Badge } from '../ui';

interface TimerSettingsProps {
  className?: string;
  onClose?: () => void;
}

const TimerSettings = ({ className = '', onClose }: TimerSettingsProps) => {
  const dispatch = useDispatch();
  const { settings, status } = useSelector((state: RootState) => state.timer);

  const [workDuration, setWorkDuration] = useState(Math.floor(settings.workDuration / 60));
  const [shortBreakDuration, setShortBreakDuration] = useState(Math.floor(settings.shortBreakDuration / 60));
  const [longBreakDuration, setLongBreakDuration] = useState(Math.floor(settings.longBreakDuration / 60));
  const [sessionsUntilLongBreak, setSessionsUntilLongBreak] = useState(settings.sessionsUntilLongBreak);
  const [autoStartBreaks, setAutoStartBreaks] = useState(settings.autoStartBreaks);
  const [autoStartWork, setAutoStartWork] = useState(settings.autoStartWork);

  const handleSaveSettings = () => {
    dispatch(setTimerSettings({
      workDuration: workDuration * 60,
      shortBreakDuration: shortBreakDuration * 60,
      longBreakDuration: longBreakDuration * 60,
      sessionsUntilLongBreak,
      autoStartBreaks,
      autoStartWork
    }));
    
    if (onClose) {
      onClose();
    }
  };

  const presetConfigs = [
    {
      name: 'Classic Pomodoro',
      work: 25,
      shortBreak: 5,
      longBreak: 15,
      sessions: 4,
      icon: <Clock size={20} />
    },
    {
      name: 'Extended Focus',
      work: 45,
      shortBreak: 10,
      longBreak: 30,
      sessions: 3,
      icon: <Zap size={20} />
    },
    {
      name: 'Quick Bursts',
      work: 15,
      shortBreak: 5,
      longBreak: 15,
      sessions: 6,
      icon: <Coffee size={20} />
    }
  ];

  const applyPreset = (preset: typeof presetConfigs[0]) => {
    setWorkDuration(preset.work);
    setShortBreakDuration(preset.shortBreak);
    setLongBreakDuration(preset.longBreak);
    setSessionsUntilLongBreak(preset.sessions);
  };

  const isTimerRunning = status === TimerStatus.RUNNING;

  return (
    <Card className={`w-full max-w-2xl ${className}`} variant="outlined">
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Timer Settings
          </h3>
          {isTimerRunning && (
            <Badge variant="warning" size="sm">
              Timer Running
            </Badge>
          )}
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Customize your focus session durations and preferences
        </p>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Preset Configurations */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Quick Presets
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {presetConfigs.map((preset) => (
              <button
                key={preset.name}
                onClick={() => applyPreset(preset)}
                className="p-3 text-left border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
                disabled={isTimerRunning}
              >
                <div className="flex items-center gap-2 mb-2">
                  {preset.icon}
                  <span className="font-medium text-gray-900 dark:text-white">
                    {preset.name}
                  </span>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  {preset.work}m work • {preset.shortBreak}m break
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Custom Duration Settings */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Work Duration"
            type="number"
            min="1"
            max="120"
            value={workDuration}
            onChange={(e) => setWorkDuration(parseInt(e.target.value) || 25)}
            helperText="Minutes per work session"
            disabled={isTimerRunning}
            leftIcon={<Clock size={16} />}
          />
          
          <Input
            label="Short Break"
            type="number"
            min="1"
            max="60"
            value={shortBreakDuration}
            onChange={(e) => setShortBreakDuration(parseInt(e.target.value) || 5)}
            helperText="Minutes for short breaks"
            disabled={isTimerRunning}
            leftIcon={<Coffee size={16} />}
          />
          
          <Input
            label="Long Break"
            type="number"
            min="1"
            max="120"
            value={longBreakDuration}
            onChange={(e) => setLongBreakDuration(parseInt(e.target.value) || 15)}
            helperText="Minutes for long breaks"
            disabled={isTimerRunning}
            leftIcon={<Zap size={16} />}
          />
        </div>

        {/* Sessions Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Sessions Until Long Break"
            type="number"
            min="2"
            max="10"
            value={sessionsUntilLongBreak}
            onChange={(e) => setSessionsUntilLongBreak(parseInt(e.target.value) || 4)}
            helperText="Work sessions before long break"
            disabled={isTimerRunning}
          />
        </div>

        {/* Auto-start Options */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Automation
          </h4>
          <div className="space-y-3">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={autoStartBreaks}
                onChange={(e) => setAutoStartBreaks(e.target.checked)}
                disabled={isTimerRunning}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Auto-start breaks
                </span>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Automatically start break timers when work sessions end
                </p>
              </div>
            </label>
            
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={autoStartWork}
                onChange={(e) => setAutoStartWork(e.target.checked)}
                disabled={isTimerRunning}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Auto-start work sessions
                </span>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Automatically start work timers when breaks end
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* Preview */}
        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Session Preview
          </h4>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {workDuration} minutes of focused work, followed by a {shortBreakDuration}-minute break. 
            After {sessionsUntilLongBreak} sessions, take a {longBreakDuration}-minute long break.
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          {onClose && (
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
          )}
          <Button 
            onClick={handleSaveSettings}
            icon={<Check size={16} />}
            disabled={isTimerRunning}
          >
            Save Settings
          </Button>
        </div>

        {isTimerRunning && (
          <div className="text-center text-sm text-yellow-600 dark:text-yellow-500">
            ⚠️ Stop the timer to modify settings
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TimerSettings;
