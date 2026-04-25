"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuthStore } from "@/features/auth/stores/auth-store";


export function PublicRoute({ children }: { children: ReactNode }) {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const isBooting = useAuthStore((s) => s.isBooting);

  useEffect(() => {
    if (!isBooting && accessToken) {
      router.replace("/dashboard");
    }
  }, [isBooting, accessToken, router]);

  return <>{children}</>;
}