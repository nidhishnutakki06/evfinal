/**
 * Generic transport-level types.
 * No SH-305 domain concepts are included here.
 */

export interface ApiError {
  status: number;
  message: string;
  code?: string;
  details?: unknown;
}

export interface ApiResponse<T = unknown> {
  data: T;
  error?: ApiError;
}
