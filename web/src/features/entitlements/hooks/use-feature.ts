"use client";

import { useMe } from "@/features/auth/hooks/use-auth";
import type { FeatureKey } from "../feature-keys";

/**
 * Returns whether the current tenant has a given feature enabled.
 * Returns false while user data loads — components stay hidden until
 * we know for sure (fail-closed).
 */
export function useFeature(feature: FeatureKey): boolean {
  const { data: user } = useMe();
  return user?.entitlements?.includes(feature) ?? false;
}

/**
 * Returns whether the current tenant has ALL of the given features.
 */
export function useFeatures(...features: FeatureKey[]): boolean {
  const { data: user } = useMe();
  if (!user) return false;
  return features.every((f) => user.entitlements?.includes(f));
}