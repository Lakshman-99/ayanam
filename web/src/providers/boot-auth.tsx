"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/features/auth/stores/auth-store";
import { env } from "@/lib/config/env";

/**
 * Runs once on app mount.
 *
 * The refresh token lives in an httpOnly cookie that survives page reloads.
 * We exchange it for a fresh access token so the user stays logged in.
 *
 * If the cookie is missing or expired, we just mark booting=false and the
 * user lands on the login page as expected.
 */
export function BootAuth({ children }: { children: React.ReactNode }) {
  const setAccessToken = useAuthStore((s) => s.setAccessToken);
  const setBooted = useAuthStore((s) => s.setBooted);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const res = await fetch(`${env.apiBaseUrl}/api/v1/auth/refresh`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
        if (!cancelled && res.ok) {
          const data = (await res.json()) as { access_token: string };
          setAccessToken(data.access_token);
        }
      } catch {
        // network error or no refresh cookie — treat as logged out
      } finally {
        if (!cancelled) setBooted();
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [setAccessToken, setBooted]);

  return <>{children}</>;
}