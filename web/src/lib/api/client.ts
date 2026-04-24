"use client";

import createClient, { type Middleware } from "openapi-fetch";
import { env } from "@/lib/config/env";
import { useAuthStore } from "@/features/auth/stores/auth-store";
import type { paths } from "./schema";

/**
 * Single API client used everywhere.
 *
 * - Auto-injects Bearer token from the auth store on every request
 * - Sends cookies (refresh token) cross-origin via credentials: "include"
 * - Auto-refreshes on 401 once, then retries the original request
 * - On refresh failure, clears auth and lets the caller handle redirect
 */

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise; // dedupe concurrent refreshes

  refreshPromise = (async () => {
    try {
      const res = await fetch(`${env.apiBaseUrl}/api/v1/auth/refresh`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (!res.ok) return null;
      const data = (await res.json()) as { access_token: string };
      useAuthStore.getState().setAccessToken(data.access_token);
      return data.access_token;
    } catch {
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

const authMiddleware: Middleware = {
  async onRequest({ request }) {
    const token = useAuthStore.getState().accessToken;
    if (token) request.headers.set("Authorization", `Bearer ${token}`);
    return request;
  },

  async onResponse({ request, response }) {
    if (response.status !== 401) return response;
    if (request.url.includes("/auth/refresh") || request.url.includes("/auth/login")) {
      return response;
    }

    const newToken = await refreshAccessToken();
    if (!newToken) {
      useAuthStore.getState().clear();
      return response;
    }

    const retried = await fetch(request.url, {
      method: request.method,
      headers: { ...Object.fromEntries(request.headers), Authorization: `Bearer ${newToken}` },
      body: request.body,
      credentials: "include",
    });
    return retried;
  },
};

export const api = createClient<paths>({
  baseUrl: env.apiBaseUrl,
  credentials: "include",
});

api.use(authMiddleware);