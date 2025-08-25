import { useState } from 'react';
import { Settings as SettingsIcon } from 'lucide-react';
import { Timer as TimerComponent, TimerSettings, SessionHistory } from '../components/timer';
import { Button, Modal, ConnectionStatus } from '../components/ui';

const Timer = () => {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Focus Timer
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Stay focused with the Pomodoro Technique
          </p>
        </div>
        <Button 
          variant="outline" 
          onClick={() => setShowSettings(true)}
          icon={<SettingsIcon size={16} />}
        >
          Settings
        </Button>
      </div>

      {/* Main Timer */}
      <div className="flex justify-center">
        <TimerComponent />
      </div>

      {/* Connection Status */}
      <div className="max-w-2xl mx-auto">
        <ConnectionStatus showDetails={true} />
      </div>

      {/* Session History */}
      <div className="max-w-2xl mx-auto">
        <SessionHistory maxSessions={5} />
      </div>

      {/* Settings Modal */}
      <Modal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        title="Timer Settings"
        size="xl"
      >
        <TimerSettings onClose={() => setShowSettings(false)} />
      </Modal>
    </div>
  );
};

export default Timer;
