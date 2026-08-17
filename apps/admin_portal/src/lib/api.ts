import axios from 'axios';

// The reverse proxy (Nginx or Next.js rewrites) will handle routing /api to the right microservice.
// For now, we will configure Next.js to rewrite /api to the respective backend services or use absolute URLs.
// Assuming local development uses different ports: Auth (8000), Tenant Config (8002), Knowledge (8001), Engine (8003).
// To keep it simple, we'll assume a local dev proxy or rely on Next.js rewrites.

const api = axios.create({
  baseURL: '/api', // Will be rewritten in next.config.mjs
});

api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
