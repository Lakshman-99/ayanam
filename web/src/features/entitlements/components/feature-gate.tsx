"use client";

import type { ReactNode } from "react";
import { useFeature } from "../hooks/use-feature";
import type { FeatureKey } from "../feature-keys";

interface FeatureGateProps {
  feature: FeatureKey;
  children: ReactNode;
  /** Optional fallback shown when the feature is locked */
  fallback?: ReactNode;
}

/**
 * Conditionally renders children based on whether the tenant has the feature.
 *
 * <FeatureGate feature="numerology">
 *   <NumerologyDashboard />
 * </FeatureGate>
 *
 * <FeatureGate feature="numerology" fallback={<UpgradePrompt feature="numerology" />}>
 *   <NumerologyDashboard />
 * </FeatureGate>
 */
export function FeatureGate({ feature, children, fallback = null }: FeatureGateProps) {
  const enabled = useFeature(feature);
  return <>{enabled ? children : fallback}</>;
}