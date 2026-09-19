export const env = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  WS_BASE_URL: import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/ws/state',
  IS_DEV_PREVIEW: import.meta.env.DEV && import.meta.env.VITE_DEV_PREVIEW === 'true',
} as const;
