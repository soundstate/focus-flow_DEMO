import { useState } from 'react';
import { Search, Download, Settings, Heart, Star, AlertCircle } from 'lucide-react';
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  Modal,
  LoadingSpinner,
  Badge
} from '../components/ui';

const UIDemo = () => {
  const [showModal, setShowModal] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [inputError, setInputError] = useState('');

  const handleValidateInput = () => {
    if (!inputValue.trim()) {
      setInputError('This field is required');
    } else if (inputValue.length < 3) {
      setInputError('Must be at least 3 characters');
    } else {
      setInputError('');
    }
  };

  return (
    <div className="p-6 space-y-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          UI Components Demo
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Showcase of all available UI components in the Focus Flow component library.
        </p>
      </div>

      {/* Buttons Section */}
      <Card variant="outlined">
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Buttons</h2>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Variants</h3>
              <div className="flex flex-wrap gap-2">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="danger">Danger</Button>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sizes</h3>
              <div className="flex items-center gap-2">
                <Button size="sm">Small</Button>
                <Button size="md">Medium</Button>
                <Button size="lg">Large</Button>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">With Icons</h3>
              <div className="flex flex-wrap gap-2">
                <Button icon={<Download size={16} />}>Download</Button>
                <Button variant="outline" icon={<Settings size={16} />}>Settings</Button>
                <Button variant="ghost" icon={<Heart size={16} />}>Like</Button>
                <Button loading>Loading</Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Inputs Section */}
      <Card variant="outlined">
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Input Fields</h2>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Basic Input"
              placeholder="Enter some text..."
            />
            
            <Input
              label="Input with Left Icon"
              placeholder="Search..."
              leftIcon={<Search size={16} />}
            />
            
            <Input
              label="Validated Input"
              placeholder="Type something..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onBlur={handleValidateInput}
              error={inputError}
            />
            
            <Input
              label="Input with Helper Text"
              placeholder="example@email.com"
              helperText="We'll never share your email"
              type="email"
            />
            
            <Input
              label="Disabled Input"
              placeholder="This is disabled"
              disabled
            />
            
            <Input
              label="Password Input"
              placeholder="Enter password"
              type="password"
            />
          </div>
        </CardContent>
      </Card>

      {/* Cards Section */}
      <Card variant="outlined">
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Cards</h2>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card variant="default">
              <CardHeader>
                <h3 className="font-semibold">Default Card</h3>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 dark:text-gray-400">
                  This is a default card with basic styling.
                </p>
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardHeader>
                <h3 className="font-semibold">Outlined Card</h3>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 dark:text-gray-400">
                  This card has a visible border.
                </p>
              </CardContent>
              <CardFooter>
                <Button size="sm">Action</Button>
              </CardFooter>
            </Card>

            <Card variant="elevated">
              <CardHeader>
                <h3 className="font-semibold">Elevated Card</h3>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 dark:text-gray-400">
                  This card has a shadow for elevation.
                </p>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      {/* Badges Section */}
      <Card variant="outlined">
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Badges</h2>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Variants</h3>
              <div className="flex flex-wrap gap-2">
                <Badge variant="primary">Primary</Badge>
                <Badge variant="secondary">Secondary</Badge>
                <Badge variant="success">Success</Badge>
                <Badge variant="warning">Warning</Badge>
                <Badge variant="danger">Danger</Badge>
                <Badge variant="outline">Outline</Badge>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sizes</h3>
              <div className="flex items-center gap-2">
                <Badge size="sm">Small</Badge>
                <Badge size="md">Medium</Badge>
                <Badge size="lg">Large</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading Spinners Section */}
      <Card variant="outlined">
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Loading Spinners</h2>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sizes</h3>
              <div className="flex items-center gap-8">
                <LoadingSpinner size="sm" />
                <LoadingSpinner size="md" />
                <LoadingSpinner size="lg" />
                <LoadingSpinner size="xl" />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">With Text</h3>
              <div className="flex justify-center">
                <LoadingSpinner size="lg" text="Loading your data..." />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Modal Section */}
      <Card variant="outlined">
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Modal</h2>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Click the button below to see a modal in action.
          </p>
          <Button onClick={() => setShowModal(true)} icon={<Star size={16} />}>
            Open Modal
          </Button>
        </CardContent>
      </Card>

      {/* Demo Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Demo Modal"
        size="lg"
      >
        <div className="space-y-4">
          <div className="flex items-start space-x-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                Modal Demo
              </h3>
              <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                This is an example modal with various content including icons, text, and interactive elements.
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <Input 
              label="Modal Input Example"
              placeholder="You can interact with elements in modals..."
            />
            
            <div className="flex items-center space-x-2">
              <Badge variant="success">Feature</Badge>
              <Badge variant="warning">Demo</Badge>
              <Badge variant="outline">Interactive</Badge>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button variant="outline" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
            <Button onClick={() => setShowModal(false)}>
              Got it!
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default UIDemo;
