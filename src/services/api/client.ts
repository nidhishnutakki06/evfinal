import { env } from "@/config/env";
import type { ApiError } from "@/types/api.types";

/**
 * Generic REST API client wrapper around native fetch.
 * Handles base URL, default headers, and JSON serialization.
 * Does NOT contain any domain-specific endpoints.
 */

class ApiClient {
  private baseURL = env.API_BASE_URL;

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers = new Headers(options.headers);
    if (!headers.has("Content-Type") && options.method !== "GET" && options.method !== "DELETE") {
      headers.set("Content-Type", "application/json");
    }

    if (env.IS_DEV_PREVIEW && options.method !== "GET") {
      console.warn(`[DEV PREVIEW] Blocked HTTP mutation to ${endpoint}`);
      const error: ApiError = {
        status: 403,
        message: "Preview mode — backend control disabled"
      };
      throw error;
    }

    try {
      const response = await fetch(url, { ...options, headers });
      
      if (!response.ok) {
        let errorMessage = "An error occurred";
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorMessage;
        } catch {
          // Response is not JSON
        }
        const error: ApiError = {
          status: response.status,
          message: errorMessage
        };
        throw error;
      }

      // Handle empty responses
      if (response.status === 204) {
        return {} as T;
      }

      return await response.json() as T;
    } catch (err) {
      if ((err as ApiError).status) {
        throw err;
      }
      const genericError: ApiError = {
        status: 0,
        message: err instanceof Error ? err.message : "Network error"
      };
      throw genericError;
    }
  }

  public get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  public post<T>(endpoint: string, data?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  public put<T>(endpoint: string, data?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  public delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }
}

export const apiClient = new ApiClient();
