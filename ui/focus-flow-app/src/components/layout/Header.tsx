import { Menu, Bell, Moon, Sun } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '@/store';
import { toggleSidebar, setTheme } from '@/store/slices/uiSlice';

const Header = () => {
  const dispatch = useAppDispatch();
  const { theme, notifications } = useAppSelector((state) => state.ui);

  const unreadCount = notifications.length;

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    dispatch(setTheme(newTheme));
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between h-16 px-6">
        {/* Left side - Mobile menu button */}
        <div className="flex items-center">
          <button
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={() => dispatch(toggleSidebar())}
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>

        {/* Right side - Theme toggle and notifications */}
        <div className="flex items-center space-x-4">
          {/* Theme toggle */}
          <button
            className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={toggleTheme}
          >
            {theme === 'light' ? (
              <Moon className="w-5 h-5" />
            ) : (
              <Sun className="w-5 h-5" />
            )}
          </button>

          {/* Notifications */}
          <div className="relative">
            <button className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700">
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white dark:ring-gray-800" />
              )}
            </button>
          </div>

          {/* User avatar placeholder */}
          <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-white">U</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
