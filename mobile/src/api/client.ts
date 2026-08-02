import type { ApiErrorBody } from "../types";

const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  code?: string;
  fieldErrors: Record<string, string>;

  constructor(
    message: string,
    status: number,
    code?: string,
    fieldErrors: Record<string, string> = {}
  ) {
    super(message);
    this.status = status;
    this.code = code;
    this.fieldErrors = fieldErrors;
  }
}

function extractFieldErrors(detail: ApiErrorBody["detail"]): Record<string, string> {
  if (!Array.isArray(detail)) return {};
  const errors: Record<string, string> = {};
  for (const item of detail) {
    const field = item.loc[item.loc.length - 1];
    if (typeof field === "string") {
      errors[field] = item.msg;
    }
  }
  return errors;
}

function summarizeDetail(detail: ApiErrorBody["detail"]): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((d) => d.msg).join(" ");
  }
  return "Something went wrong.";
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch {
    throw new ApiError(
      "Could not reach the server. Check your connection and the API URL.",
      0
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    // no JSON body (e.g. some error pages) — fall through with body = null
  }

  if (!response.ok) {
    const errorBody = (body ?? {}) as Partial<ApiErrorBody>;
    const detail = errorBody.detail ?? "Something went wrong.";
    throw new ApiError(
      summarizeDetail(detail),
      response.status,
      errorBody.code,
      extractFieldErrors(detail)
    );
  }

  return body as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
};
