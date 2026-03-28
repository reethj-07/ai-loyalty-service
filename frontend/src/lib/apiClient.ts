/**
 * API Client utility with automatic Authorization header injection
 * This utility should be used for all API calls to ensure proper auth token handling
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const AUTH_TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const TOKEN_EXPIRES_AT_KEY = 'token_expires_at';

export interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
}

function clearAuthState() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRES_AT_KEY);
  window.dispatchEvent(new CustomEvent('auth:unauthorized'));
}

function persistSession(session: any) {
  const accessToken = session?.access_token;
  const refreshToken = session?.refresh_token;
  const expiresIn = Number(session?.expires_in ?? 0);

  if (accessToken) {
    localStorage.setItem(AUTH_TOKEN_KEY, accessToken);
  }
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
  if (Number.isFinite(expiresIn) && expiresIn > 0) {
    localStorage.setItem(TOKEN_EXPIRES_AT_KEY, String(Date.now() + expiresIn * 1000));
  }
}

/**
 * Fetch wrapper that automatically includes Authorization header if token exists
 * @param url - The API endpoint URL
 * @param options - Standard fetch options (method, body, etc.)
 * @returns Promise<Response>
 */
export async function apiFetch(url: string, options: FetchOptions = {}): Promise<Response> {
  const requestOnce = async (accessTokenOverride?: string) => {
    const token = accessTokenOverride || localStorage.getItem(AUTH_TOKEN_KEY);

    const headers: Record<string, string> = {
      ...options.headers,
    };

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = headers['Content-Type'] || 'application/json';
    }

    if (token && !token.startsWith('demo-token-')) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const tenantId = localStorage.getItem('tenant_id');
    if (tenantId) {
      headers['X-Tenant-Id'] = tenantId;
    }

    return fetch(url, {
      ...options,
      credentials: 'include',
      headers,
    });
  };

  let response = await requestOnce();

  const isAuthEndpoint = /\/api\/v1\/auth\/(signin|signup|refresh|forgot-password)/.test(url);
  if (response.status === 401 && !isAuthEndpoint) {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

    if (refreshToken) {
      const refreshResponse = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ refresh_token: refreshToken || undefined }),
      });

      if (refreshResponse.ok) {
        const refreshData = await refreshResponse.json().catch(() => ({}));
        persistSession(refreshData?.session);

        const newToken = refreshData?.session?.access_token;
        if (newToken) {
          response = await requestOnce(newToken);
        }
      }
    }

    if (response.status === 401) {
      clearAuthState();
    }
  }

  return response;
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
