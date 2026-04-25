"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuthStore } from "@/features/auth/stores/auth-store";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const isBooting = useAuthStore((s) => s.isBooting);

  useEffect(() => {
    if (!isBooting && !accessToken) {
      router.replace("/login");
    }
  }, [isBooting, accessToken, router]);

  if (isBooting || !accessToken) {
    return <FullScreenLoader />;
  }

  return <>{children}</>;
}

function FullScreenLoader() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="size-6 animate-spin rounded-full border-2 border-slate-300 border-t-slate-700" />
    </div>
  );
}