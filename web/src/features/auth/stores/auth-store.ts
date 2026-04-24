"use client";

import { create } from "zustand";

interface AuthState {
  accessToken: string | null;
  isBooting: boolean;
  setAccessToken: (token: string | null) => void;
  setBooted: () => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  isBooting: true,
  setAccessToken: (token) => set({ accessToken: token }),
  setBooted: () => set({ isBooting: false }),
  clear: () => set({ accessToken: null }),
}));