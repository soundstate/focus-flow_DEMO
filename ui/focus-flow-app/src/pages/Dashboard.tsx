const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Placeholder cards */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Total Sessions
          </h3>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            42
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Focus Time
          </h3>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            24h 15m
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Current Streak
          </h3>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            7 days
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Average Score
          </h3>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            8.4
          </p>
        </div>
      </div>
      
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">
          Dashboard components will be implemented in the next phase
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
