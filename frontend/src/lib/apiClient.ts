/**
 * API Client utility with automatic Authorization header injection
 * This utility should be used for all API calls to ensure proper auth token handling
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
}

/**
 * Fetch wrapper that automatically includes Authorization header if token exists
 * @param url - The API endpoint URL
 * @param options - Standard fetch options (method, body, etc.)
 * @returns Promise<Response>
 */
export async function apiFetch(url: string, options: FetchOptions = {}): Promise<Response> {
  const token = localStorage.getItem('auth_token');

  const headers: Record<string, string> = {
    ...options.headers,
  };

  // Only set Content-Type if not uploading files (FormData)
  // FormData automatically sets multipart/form-data with boundary
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  // Add Authorization header if token exists AND it's not a demo token
  // Demo tokens are used for UI testing without backend authentication
  if (token && !token.startsWith('demo-token-')) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Add X-Tenant-Id header if available (future tenant support)
  const tenantId = localStorage.getItem('tenant_id');
  if (tenantId) {
    headers['X-Tenant-Id'] = tenantId;
  }

  return fetch(url, {
    ...options,
    headers,
  });
}

/**
 * Helper to make authenticated API calls with automatic JSON parsing
 * @param url - The API endpoint URL
 * @param options - Standard fetch options
 * @returns Promise<any> - Parsed JSON response
 */
export async function apiCall<T = any>(url: string, options: FetchOptions = {}): Promise<T> {
  const response = await apiFetch(url, options);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'API Error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Helper for GET requests
 */
export async function apiGet<T = any>(url: string): Promise<T> {
  return apiCall<T>(url, { method: 'GET' });
}

/**
 * Helper for POST requests
 */
export async function apiPost<T = any>(url: string, body?: any): Promise<T> {
  return apiCall<T>(url, {
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined,
  });
}

/**
 * Helper for PUT requests
 */
export async function apiPut<T = any>(url: string, body?: any): Promise<T> {
  return apiCall<T>(url, {
    method: 'PUT',
    body: body ? JSON.stringify(body) : undefined,
  });
}

/**
 * Helper for DELETE requests
 */
export async function apiDelete<T = any>(url: string): Promise<T> {
  return apiCall<T>(url, { method: 'DELETE' });
}

/**
 * Helper for PATCH requests
 */
export async function apiPatch<T = any>(url: string, body?: any): Promise<T> {
  return apiCall<T>(url, {
    method: 'PATCH',
    body: body ? JSON.stringify(body) : undefined,
  });
}

export default apiFetch;
