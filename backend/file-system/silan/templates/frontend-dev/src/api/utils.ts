import axios, { AxiosResponse, AxiosError, AxiosRequestConfig } from 'axios';
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

// Create axios instance with default configuration
const axiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.DEFAULT_HEADERS,
  // Enable CORS
  withCredentials: false,
});

// Request interceptor for logging
axiosInstance.interceptors.request.use(
  (config) => {
    console.log(`📡 API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request error:', error.message);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error(`❌ API Error: ${error.code} ${error.config?.url}`);
    return Promise.reject(error);
  }
);

// API request helper with error handling
export const apiRequest = async <T = any>(
  endpoint: string,
  options: AxiosRequestConfig = {}
): Promise<T> => {
  try {
    const response = await axiosInstance.request<T>({
      url: endpoint,
      ...options,
    });
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      const status = axiosError.response?.status;
      const responseData = axiosError.response?.data;
      
      if (axiosError.code === 'ECONNABORTED') {
        throw new ApiError('Request timeout');
      }
      
      if (axiosError.code === 'ERR_NETWORK') {
        throw new ApiError('Network error - please check if the server is running');
      }
      
      throw new ApiError(
        (responseData as any)?.message || axiosError.message || `API request failed: ${status}`,
        status,
        responseData
      );
    }
    
    if (error instanceof Error) {
      throw new ApiError(
        error.message || 'Network error occurred',
        undefined,
        error
      );
    }
    
    throw new ApiError('Unknown error occurred');
  }
};

// GET request helper
export const get = <T = any>(endpoint: string, params?: Record<string, any>): Promise<T> => {
  return apiRequest<T>(endpoint, {
    method: 'GET',
    params,
  });
};

// POST request helper
export const post = <T = any>(endpoint: string, data?: any): Promise<T> => {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    data,
  });
};

// PUT request helper
export const put = <T = any>(endpoint: string, data?: any): Promise<T> => {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    data,
  });
};

// DELETE request helper
export const del = <T = any>(endpoint: string): Promise<T> => {
  return apiRequest<T>(endpoint, {
    method: 'DELETE',
  });
};

// Helper function to build query parameters
export const buildQueryParams = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        value.forEach(item => searchParams.append(key, String(item)));
      } else {
        searchParams.append(key, String(value));
      }
    }
  });
  
  return searchParams.toString();
};

// Helper function to format language parameter
export const formatLanguage = (language: Language): string => {
  return language === 'zh' ? 'zh' : 'en';
};

// Helper function to simulate delay (for development/testing)
export const delay = (ms: number): Promise<void> => 
  new Promise(resolve => setTimeout(resolve, ms));

// Helper function to retry API calls
export const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> => {
  let lastError: Error = new Error('All retry attempts failed');
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error occurred');
      if (i < maxRetries - 1) {
        await delay(delayMs * (i + 1)); // Exponential backoff
      }
    }
  }
  
  throw lastError;
};

// Export axios instance for direct use if needed
export { axiosInstance };