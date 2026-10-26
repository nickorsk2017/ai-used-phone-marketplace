import type { z } from "zod";
import { API_BASE_URL } from "@/config/api";

export const NETWORK_ERROR_STATUS = 0;

interface RequestOptions<TData> {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  signal?: AbortSignal;
  schema?: z.ZodType<TData>;
}

export function successResponse<TData>(data: TData): Api.SuccessResponse<TData> {
  return { success: true, data, errorText: "" };
}

export function errorResponse(status: number, errorText: string): Api.ErrorResponse {
  return { success: false, errorText, status };
}

async function readErrorText(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (body && typeof body === "object" && "detail" in body && typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    return `Request failed with status ${response.status}`;
  }
  return `Request failed with status ${response.status}`;
}

function buildHeaders(hasBody: boolean): Record<string, string> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (hasBody) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

export async function apiRequest<TData = void>(
  path: string,
  options: RequestOptions<TData> = {},
): Promise<Api.Response<TData>> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method ?? "GET",
      headers: buildHeaders(options.body !== undefined),
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: options.signal,
      // The session is an HttpOnly cookie set by the Backend: docs/backend/AUTH.md#session-flow.
      credentials: "include",
    });
  } catch (error) {
    const isAborted = error instanceof DOMException && error.name === "AbortError";
    return errorResponse(NETWORK_ERROR_STATUS, isAborted ? "Request aborted" : "Network error");
  }

  if (!response.ok) {
    return errorResponse(response.status, await readErrorText(response));
  }

  if (!options.schema || response.status === 204) {
    return successResponse(undefined as TData);
  }

  let body: unknown;
  try {
    body = await response.json();
  } catch {
    return errorResponse(response.status, "Invalid response");
  }

  const parsed = options.schema.safeParse(body);
  return parsed.success ? successResponse(parsed.data) : errorResponse(response.status, "Invalid response");
}
