/**
 * Centralized, type-safe access to environment variables.
 * Fail loudly at boot if any required var is missing.
 */
const required = (name: string, value: string | undefined): string => {
  if (!value) {
    throw new Error(`Missing required env var: ${name}`);
  }
  return value;
};

export const env = {
  apiBaseUrl: required("NEXT_PUBLIC_API_BASE_URL", process.env.NEXT_PUBLIC_API_BASE_URL),
  appDomain: required("NEXT_PUBLIC_APP_DOMAIN", process.env.NEXT_PUBLIC_APP_DOMAIN),
};