import axios, { AxiosInstance, AxiosError } from 'axios';
import toast from 'react-hot-toast';

// Create API client
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const message = 
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      'Une erreur est survenue';

    // Don't show toast for 401 on login
    if (error.response?.status === 401 && !error.config?.url?.includes('/login')) {
      toast.error('Session expirée. Veuillez vous reconnecter.');
      // Redirect to login or refresh token
    } else if (error.response?.status === 422) {
      toast.error(`Erreur de validation: ${message}`);
    } else if (error.response?.status >= 500) {
      toast.error('Erreur serveur. Veuillez réessayer plus tard.');
    }

    return Promise.reject(error);
  }
);

export default api;
