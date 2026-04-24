"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useLogout, useMe } from "@/features/auth/hooks/use-auth";
import { useAuthStore } from "@/features/auth/stores/auth-store";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const isBooting = useAuthStore((s) => s.isBooting);
  const { data: user, isLoading } = useMe();
  const logout = useLogout();

  // Wait for boot to finish before deciding the user is unauthenticated
  useEffect(() => {
    if (!isBooting && !accessToken) router.replace("/login");
  }, [isBooting, accessToken, router]);

  const handleLogout = async () => {
    await logout.mutateAsync();
    router.replace("/login");
  };

  if (isBooting || !accessToken || isLoading) {
    return <div className="p-8 text-slate-500">Loading…</div>;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-semibold">Aynam</h1>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-600">{user?.email}</span>
            <Button variant="outline" size="sm" onClick={handleLogout} disabled={logout.isPending}>
              Sign out
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
            Your workspace is empty. We&apos;ll add modules here in the next phases.
          </p>
        </div>
      </main>
    </div>
  );
}