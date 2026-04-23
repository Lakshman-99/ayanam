const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function normalizeBase(url) {
  return String(url).replace(/\/+$/, "");
}

function buildUrl(path) {
  const normalizedBase = normalizeBase(BASE);
  const normalizedPath = String(path || "").startsWith("/")
    ? path
    : `/${path || ""}`;
  return `${normalizedBase}/api/v1${normalizedPath}`;
}

export async function apiRequest(path, options = {}) {
  const {
    method = "GET",
    token,
    tenantSlug,
    headers = {},
    body,
    signal,
  } = options;

  const requestHeaders = {
    "Content-Type": "application/json",
    ...headers,
  };

  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  if (tenantSlug) {
    requestHeaders["x-tenant-slug"] = tenantSlug;
  }

  const response = await fetch(buildUrl(path), {
    method,
    headers: requestHeaders,
    body: body ? JSON.stringify(body) : undefined,
    signal,
  });

  const isJson = response.headers
    .get("content-type")
    ?.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    if (payload?.detail && typeof payload.detail === "string") {
      message = payload.detail;
    }
    if (Array.isArray(payload?.detail)) {
      message = payload.detail
        .map((item) => {
          if (!item) {
            return null;
          }
          const location = Array.isArray(item.loc)
            ? item.loc.join(".")
            : "field";
          return `${location}: ${item.msg || "invalid"}`;
        })
        .filter(Boolean)
        .join("; ");
    }

    const error = new Error(message);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

export function getStoredAuth() {
  if (typeof window === "undefined") {
    return { accessToken: null, refreshToken: null, tenantSlug: null };
  }

  const raw = window.localStorage.getItem("ayanam.auth");
  if (!raw) {
    return { accessToken: null, refreshToken: null, tenantSlug: null };
  }

  try {
    const parsed = JSON.parse(raw);
    return {
      accessToken: parsed.accessToken || null,
      refreshToken: parsed.refreshToken || null,
      tenantSlug: parsed.tenantSlug || null,
    };
  } catch {
    return { accessToken: null, refreshToken: null, tenantSlug: null };
  }
}

export function setStoredAuth(auth) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(
    "ayanam.auth",
    JSON.stringify({
      accessToken: auth?.accessToken || null,
      refreshToken: auth?.refreshToken || null,
      tenantSlug: auth?.tenantSlug || null,
    }),
  );
}
