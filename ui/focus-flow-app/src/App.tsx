import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@/store';

// Layout components
import Layout from '@/components/layout/Layout';

// Page components (we'll create these)
import Dashboard from '@/pages/Dashboard';
import Timer from '@/pages/Timer';
import Analytics from '@/pages/Analytics';
import Templates from '@/pages/Templates';
import Settings from '@/pages/Settings';

// Global styles and providers
import './App.css';

function App() {
  return (
    <Provider store={store}>
      <Router>
        <div className="App min-h-screen bg-gray-50 dark:bg-gray-900">
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Navigate to="/timer" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="timer" element={<Timer />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="templates" element={<Templates />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Routes>
        </div>
      </Router>
    </Provider>
  );
}

export default App;
