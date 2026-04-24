"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { useAuthStore } from "@/features/auth/stores/auth-store";
import type { LoginInput, RegisterInput } from "@/features/auth/schemas/auth-schemas";

const ME_QUERY_KEY = ["auth", "me"] as const;

export function useMe() {
  const accessToken = useAuthStore((s) => s.accessToken);

  return useQuery({
    queryKey: ME_QUERY_KEY,
    queryFn: async () => {
      const { data, error } = await api.GET("/api/v1/auth/me");
      if (error) throw error;
      return data;
    },
    enabled: !!accessToken,  // don't hit /me until we have a token
    staleTime: 5 * 60 * 1000,
  });
}

export function useLogin() {
  const setAccessToken = useAuthStore((s) => s.setAccessToken);
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async (input: LoginInput) => {
      const { data, error } = await api.POST("/api/v1/auth/login", {
        body: input,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: (data) => {
      setAccessToken(data.access_token);
      qc.invalidateQueries({ queryKey: ME_QUERY_KEY });
    },
  });
}

export function useRegister() {
  const setAccessToken = useAuthStore((s) => s.setAccessToken);
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async (input: RegisterInput) => {
      const { data, error } = await api.POST("/api/v1/auth/register", {
        body: input,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: (data) => {
      setAccessToken(data.access_token);
      qc.invalidateQueries({ queryKey: ME_QUERY_KEY });
    },
  });
}

export function useLogout() {
  const clear = useAuthStore((s) => s.clear);
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      // Backend logout is best-effort; we clear local state regardless
      await api.POST("/api/v1/auth/logout", { body: {} }).catch(() => undefined);
    },
    onSettled: () => {
      clear();
      qc.clear();  // nuke all cached data; the next user's data should not leak
    },
  });
}