/**
 * Single source of truth for all feature keys the app knows about.
 *
 * The backend's Plan.features dict uses these same keys. When you add
 * a new feature module:
 *   1. Add the key here
 *   2. Add it to backend's plan seeds (true for plans that should have it)
 *   3. Re-run the seed updater script
 *
 * Keep this in sync with backend `app/scripts/update_plan_features.py`.
 */
export const FEATURE_KEYS = [
  "astrology",
  "numerology",
  "vastu",
  "panchang",
  "horary",
  "matching",
  "api_access",
  "white_label",
] as const;

export type FeatureKey = (typeof FEATURE_KEYS)[number];