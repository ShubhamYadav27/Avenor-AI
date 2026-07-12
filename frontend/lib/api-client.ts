import axios, { AxiosError } from "axios";
import Cookies from "js-cookie";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

// Inject auth token from cookie on every request
apiClient.interceptors.request.use((config) => {
  const token = Cookies.get("avenor_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalise error shape for UI consumption
apiClient.interceptors.response.use(
  (res) => res,
  (error: AxiosError<{ detail?: string }>) => {
    if (error.response?.status === 401) {
      // Token expired — clear auth and redirect
      Cookies.remove("avenor_token");
      Cookies.remove("avenor_workspace_id");
      if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

/** Human-readable error message from an Axios error */
export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string })?.detail;
    if (detail) return detail;
    if (err.message) return err.message;
  }
  if (err instanceof Error) return err.message;
  return "An unexpected error occurred";
}
