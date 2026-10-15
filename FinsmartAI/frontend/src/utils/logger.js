/**
 * FinSmart AI - Centralized Network & API Logger
 * Automatically logs all Input (requests) and Output (responses) across Axios and Fetch in the frontend.
 */
import axios from 'axios';

export function initializeFrontendLogger() {
  if (typeof window === 'undefined') return;

  console.log(
    '%c[FinSmart Logger]%c Global network logging active (logging all Inputs & Outputs)',
    'background: #2563eb; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: bold;',
    'color: #94a3b8; font-style: italic;'
  );

  // 1. Axios Request Interceptor (INPUT LOGGING)
  axios.interceptors.request.use(
    (config) => {
      config._startTime = Date.now();
      const method = (config.method || 'GET').toUpperCase();
      const url = config.url;

      console.groupCollapsed(
        `%c📤 [API INPUT] ${method} ${url}`,
        'color: #3b82f6; font-weight: bold;'
      );
      console.log('Endpoint:', url);
      console.log('Method:', method);
      if (config.params) {
        console.log('Query Params (Input):', config.params);
      }
      if (config.data) {
        console.log('Payload Body (Input):', config.data);
      }
      console.log('Headers:', config.headers);
      console.groupEnd();

      return config;
    },
    (error) => {
      console.error('❌ [API REQUEST ERROR]', error);
      return Promise.reject(error);
    }
  );

  // 2. Axios Response Interceptor (OUTPUT LOGGING)
  axios.interceptors.response.use(
    (response) => {
      const duration = response.config?._startTime ? Date.now() - response.config._startTime : 0;
      const method = (response.config?.method || 'GET').toUpperCase();
      const url = response.config?.url;
      const status = response.status;

      console.groupCollapsed(
        `%c📥 [API OUTPUT] ${method} ${url} -> ${status} (${duration}ms)`,
        'color: #10b981; font-weight: bold;'
      );
      console.log('Status Code:', status);
      console.log('Duration:', `${duration}ms`);
      console.log('Response Data (Output):', response.data);
      console.groupEnd();

      return response;
    },
    (error) => {
      const method = (error.config?.method || 'GET').toUpperCase();
      const url = error.config?.url;
      const status = error.response?.status || 'NETWORK_ERROR';

      console.group(
        `%c❌ [API ERROR] ${method} ${url} -> ${status}`,
        'color: #ef4444; font-weight: bold;'
      );
      console.error('Error Details:', error.message);
      if (error.response?.data) {
        console.log('Error Response Data (Output):', error.response.data);
      }
      console.groupEnd();

      return Promise.reject(error);
    }
  );

  // 3. Native Fetch Interceptor (INPUT & OUTPUT LOGGING)
  const originalFetch = window.fetch;
  window.fetch = async function (...args) {
    const [resource, config] = args;
    const url = typeof resource === 'string' ? resource : resource?.url || 'unknown';
    const method = (config?.method || 'GET').toUpperCase();
    const startTime = Date.now();

    // Log Fetch Input
    console.groupCollapsed(
      `%c📤 [FETCH INPUT] ${method} ${url}`,
      'color: #06b6d4; font-weight: bold;'
    );
    console.log('URL:', url);
    console.log('Method:', method);
    if (config?.body) {
      try {
        console.log('Payload Body (Input):', JSON.parse(config.body));
      } catch {
        console.log('Payload Body (Input):', config.body);
      }
    }
    console.groupEnd();

    try {
      const response = await originalFetch.apply(this, args);
      const duration = Date.now() - startTime;
      const status = response.status;

      // Clone response to read body without consuming it for caller
      const clone = response.clone();
      const isStream = clone.headers.get('content-type')?.includes('event-stream');

      if (isStream) {
        console.log(
          `%c📥 [FETCH STREAM] ${method} ${url} -> ${status} (${duration}ms)`,
          'color: #8b5cf6; font-weight: bold;'
        );
      } else {
        clone.text().then((text) => {
          let parsed;
          try {
            parsed = JSON.parse(text);
          } catch {
            parsed = text;
          }
          console.groupCollapsed(
            `%c📥 [FETCH OUTPUT] ${method} ${url} -> ${status} (${duration}ms)`,
            'color: #10b981; font-weight: bold;'
          );
          console.log('Status Code:', status);
          console.log('Response Body (Output):', parsed);
          console.groupEnd();
        }).catch(() => {});
      }

      return response;
    } catch (err) {
      const duration = Date.now() - startTime;
      console.error(
        `%c❌ [FETCH FAILED] ${method} ${url} (${duration}ms):`,
        'color: #ef4444; font-weight: bold;',
        err
      );
      throw err;
    }
  };
}
