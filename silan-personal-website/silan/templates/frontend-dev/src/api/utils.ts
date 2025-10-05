import { API_CONFIG, type Language } from './config';

// Error types
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Build URL that prefers same-origin for '/api' endpoints to leverage dev proxy and avoid CORS
const buildUrl = (endpoint: string, params?: Record<string, any>): string => {
  let url: URL;
  if (/^https?:\/\//i.test(endpoint)) {
    url = new URL(endpoint);
  } else if (endpoint.startsWith('/')) {
    // Same-origin for dev proxy and production
    const base = (typeof window !== 'undefined' && window.location?.origin) ? window.location.origin : API_CONFIG.BASE_URL;
    url = new URL(endpoint, base);
  } else {
    // Fallback to configured base
    url = new URL(endpoint, API_CONFIG.BASE_URL);
  }
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  return url.toString();
};

// GET request helper using native fetch to avoid CORS preflight
export const get = <T = any>(endpoint: string, params?: Record<string, any>): Promise<T> => {
  const urlStr = buildUrl(endpoint, params);
  const urlObj = new URL(urlStr);
  console.log(`📡 GET Request: ${urlStr}`);

  return fetch(urlStr, {
    method: 'GET',
  }).then(async (response) => {
    console.log(`✅ GET Response: ${response.status} ${urlObj.pathname}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ GET Error: ${response.status} ${urlObj.pathname} - ${errorText}`);
      throw new ApiError(`API request failed: ${response.status}`, response.status);
    }

    return response.json();
  });
};

// POST request helper using native fetch to avoid CORS preflight
export const post = <T = any>(endpoint: string, data?: any): Promise<T> => {
  const urlStr = buildUrl(endpoint);
  const urlObj = new URL(urlStr);
  console.log(`📡 POST Request: ${urlStr}`);

  return fetch(urlStr, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
  }).then(async (response) => {
    console.log(`✅ POST Response: ${response.status} ${urlObj.pathname}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ POST Error: ${response.status} ${urlObj.pathname} - ${errorText}`);
      throw new ApiError(`API request failed: ${response.status}`, response.status);
    }

    return response.json();
  });
};

// DELETE request helper using native fetch to avoid CORS preflight
export const del = <T = any>(endpoint: string, data?: any): Promise<T> => {
  const urlStr = buildUrl(endpoint);
  const urlObj = new URL(urlStr);
  console.log(`📡 DELETE Request: ${urlStr}`);

  return fetch(urlStr, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
  }).then(async (response) => {
    console.log(`✅ DELETE Response: ${response.status} ${urlObj.pathname}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ DELETE Error: ${response.status} ${urlObj.pathname} - ${errorText}`);
      throw new ApiError(`API request failed: ${response.status}`, response.status);
    }

    // DELETE might return empty response
    const text = await response.text();
    return text ? JSON.parse(text) : null;
  });
};

// PUT request helper using native fetch to avoid CORS preflight
export const put = <T = any>(endpoint: string, data?: any): Promise<T> => {
  const urlStr = buildUrl(endpoint);
  const urlObj = new URL(urlStr);
  console.log(`📡 PUT Request: ${urlStr}`);

  return fetch(urlStr, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
  }).then(async (response) => {
    console.log(`✅ PUT Response: ${response.status} ${urlObj.pathname}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ PUT Error: ${response.status} ${urlObj.pathname} - ${errorText}`);
      throw new ApiError(`API request failed: ${response.status}`, response.status);
    }

    return response.json();
  });
};

// Language formatting helper
export const formatLanguage = (lang: Language): string => {
  return lang === 'zh' ? 'zh' : 'en';
};

// Legacy compatibility - these were the old axios-based functions
export const apiRequest = async <T = any>(endpoint: string, options: any = {}): Promise<T> => {
  const method = options.method?.toUpperCase() || 'GET';

  switch (method) {
    case 'GET':
      return get<T>(endpoint, options.params);
    case 'POST':
      return post<T>(endpoint, options.data);
    case 'PUT':
      return put<T>(endpoint, options.data);
    case 'DELETE':
      return del<T>(endpoint, options.data);
    default:
      throw new ApiError(`Unsupported method: ${method}`);
  }
};