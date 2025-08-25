import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if needed
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    
    if (import.meta.env.VITE_DEBUG) {
      console.log('API Request:', config);
    }
    
    return config;
  },
  (error) => {
    if (import.meta.env.VITE_DEBUG) {
      console.error('API Request Error:', error);
    }
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    if (import.meta.env.VITE_DEBUG) {
      console.log('API Response:', response);
    }
    return response;
  },
  (error) => {
    if (import.meta.env.VITE_DEBUG) {
      console.error('API Response Error:', error);
    }
    
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access');
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error');
    }
    
    return Promise.reject(error);
  }
);

export default api;
