"use client";

import { useRouter } from "next/navigation";
import { FeatureGate } from "@/features/entitlements/components/feature-gate";
import { useLogout, useMe } from "@/features/auth/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { useTranslation } from "react-i18next";

export default function DashboardPage() {
  const { t } = useTranslation("common");
  const router = useRouter();
  const { data: user } = useMe();
  const logout = useLogout();

  const handleLogout = async () => {
    await logout.mutateAsync();
    router.replace("/login");
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-semibold">{t("app.name")}</h1>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-600">{user?.email}</span>
            <Button variant="outline" size="sm" onClick={handleLogout} disabled={logout.isPending}>
              {t("actions.sign_out")}
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        <h2 className="text-2xl font-semibold">Welcome, {user?.full_name}</h2>
        <p className="mt-2 text-slate-600">Role: {user?.role}</p>
        <p className="text-slate-600">Entitlements: {user?.entitlements?.join(", ") || "none"}</p>

        <div className="mt-8 rounded-lg border bg-white p-6">
          <p className="text-sm text-slate-500">
            Your workspace is empty. Modules drop in here in Phase 2.
          </p>
        </div>
        <FeatureGate 
          feature="astrology"
          fallback={
            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
              Astrology is locked on your plan
            </div>
          }
        >
          <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
            ✓ Astrology module would render here
          </div>
        </FeatureGate>

        <FeatureGate
          feature="numerology"
          fallback={
            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
              Numerology is locked on your plan
            </div>
          }
        >
          <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
            ✓ Numerology module would render here
          </div>
        </FeatureGate>
      </main>
    </div>
  );
}