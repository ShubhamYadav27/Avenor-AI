import Cookies from "js-cookie";
import type { TokenResponse, MeResponse } from "@/types/api";

const TOKEN_KEY = "avenor_token";
const WORKSPACE_KEY = "avenor_workspace_id";
const USER_KEY = "avenor_user";
const COOKIE_OPTS = { expires: 1, sameSite: "strict" as const }; // 1 day

export const auth = {
  setSession(data: TokenResponse) {
    Cookies.set(TOKEN_KEY, data.access_token, COOKIE_OPTS);
    Cookies.set(WORKSPACE_KEY, data.workspace_id, COOKIE_OPTS);
  },

  clearSession() {
    Cookies.remove(TOKEN_KEY);
    Cookies.remove(WORKSPACE_KEY);
    if (typeof sessionStorage !== "undefined") {
      sessionStorage.removeItem(USER_KEY);
    }
  },

  getToken(): string | undefined {
    return Cookies.get(TOKEN_KEY);
  },

  getWorkspaceId(): string | undefined {
    return Cookies.get(WORKSPACE_KEY);
  },

  isAuthenticated(): boolean {
    return Boolean(Cookies.get(TOKEN_KEY));
  },

  cacheUser(user: MeResponse) {
    if (typeof sessionStorage !== "undefined") {
      sessionStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  },

  getCachedUser(): MeResponse | null {
    if (typeof sessionStorage === "undefined") return null;
    try {
      const raw = sessionStorage.getItem(USER_KEY);
      return raw ? (JSON.parse(raw) as MeResponse) : null;
    } catch {
      return null;
    }
  },
};
