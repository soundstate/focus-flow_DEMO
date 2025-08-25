const Timer = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center space-y-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Focus Timer
        </h1>
        
        {/* Timer Circle Placeholder */}
        <div className="flex justify-center">
          <div className="w-64 h-64 rounded-full border-8 border-gray-200 dark:border-gray-700 flex items-center justify-center bg-white dark:bg-gray-800 shadow-lg">
            <div className="text-center">
              <div className="text-4xl font-mono font-bold text-gray-900 dark:text-white">
                25:00
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Pomodoro Session
              </div>
            </div>
          </div>
        </div>
        
        {/* Controls */}
        <div className="flex justify-center space-x-4">
          <button className="px-8 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
            Start
          </button>
          <button className="px-8 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
            Pause
          </button>
          <button className="px-8 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
            Stop
          </button>
        </div>
        
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">
            Timer functionality will be implemented next
          </p>
        </div>
      </div>
    </div>
  );
};

export default Timer;
