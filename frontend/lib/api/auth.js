import { apiRequest } from "@/lib/api/client";

export async function loginWithPassword({ email, password, tenantSlug }) {
  return apiRequest("/auth/login", {
    method: "POST",
    tenantSlug,
    body: {
      email: String(email || "")
        .trim()
        .toLowerCase(),
      password,
    },
  });
}

export async function getMe({ accessToken, tenantSlug }) {
  return apiRequest("/auth/me", {
    method: "GET",
    token: accessToken,
    tenantSlug,
  });
}
