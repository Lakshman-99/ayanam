"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import BrandMark from "@/shared/ui/brand-mark";
import ConstellationBg from "@/shared/ui/constellation-bg";
import Starfield from "@/shared/ui/starfield";
import { getMe, loginWithPassword } from "@/lib/api/auth";
import { setStoredAuth } from "@/lib/api/client";
import { t } from "@/shared/utils/i18n";

function MandalaSeal() {
  return (
    <svg
      viewBox="0 0 360 360"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-full"
      aria-hidden="true"
    >
      <circle cx="180" cy="180" r="170" stroke="var(--line-bright)" />
      <circle cx="180" cy="180" r="148" stroke="var(--line)" />
      <circle cx="180" cy="180" r="120" stroke="var(--line-bright)" />
      <polygon
        points="180,70 268,220 92,220"
        stroke="var(--line-bright)"
        fill="color-mix(in srgb, var(--glass) 85%, transparent)"
      />
      <polygon
        points="180,290 92,140 268,140"
        stroke="var(--line-bright)"
        fill="color-mix(in srgb, var(--glass) 85%, transparent)"
      />
      <circle cx="180" cy="180" r="58" stroke="var(--line-bright)" />
      <circle cx="180" cy="180" r="8" fill="var(--color-gold)" />
      {Array.from({ length: 12 }).map((_, index) => {
        const angle = (index * 2 * Math.PI) / 12;
        const x = 180 + Math.cos(angle) * 135;
        const y = 180 + Math.sin(angle) * 135;
        return (
          <circle key={index} cx={x} cy={y} r="4" fill="var(--color-gold)" />
        );
      })}
    </svg>
  );
}

export default function LoginView({ dict, lang }) {
  const router = useRouter();
  const [form, setForm] = useState(() => ({
    email: "",
    password: "",
    tenantSlug:
      typeof window === "undefined"
        ? ""
        : window.localStorage.getItem("ayanam.tenantSlug") || "",
  }));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const update = (field, value) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");

    try {
      const response = await loginWithPassword({
        email: form.email,
        password: form.password,
        tenantSlug: form.tenantSlug || undefined,
      });

      const accessToken = response?.access_token || "";
      const refreshToken = response?.refresh_token || "";

      if (!accessToken || !refreshToken) {
        throw new Error("Login succeeded but tokens were missing in response.");
      }

      setStoredAuth({
        accessToken,
        refreshToken,
        tenantSlug: form.tenantSlug || null,
      });

      if (form.tenantSlug) {
        window.localStorage.setItem("ayanam.tenantSlug", form.tenantSlug);
      }

      let profileName = form.email.split("@")[0] || "Astro User";
      let profileEmail = form.email;
      try {
        const me = await getMe({
          accessToken,
          tenantSlug: form.tenantSlug || undefined,
        });
        profileName = me?.full_name || profileName;
        profileEmail = me?.email || profileEmail;
      } catch {
        // Keep login successful even when profile fetch fails.
      }

      window.localStorage.setItem(
        "ayanam.user",
        JSON.stringify({ name: profileName, email: profileEmail }),
      );

      router.push(`/${lang}`);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to sign in. Please verify your credentials.",
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="cosmic-bg min-h-screen relative">
      <ConstellationBg />
      <Starfield />

      <div className="relative z-10 min-h-screen grid grid-cols-1 lg:grid-cols-[1.25fr_1fr]">
        <section className="px-6 py-10 md:px-12 lg:px-16 flex flex-col items-center justify-center border-b lg:border-b-0 lg:border-r border-amber-200/10">
          <div className="w-full max-w-[560px] space-y-7">
            <div className="flex items-center gap-3">
              <BrandMark size={42} />
              <div>
                <div className="font-display tracking-[0.18em] text-amber-200 text-sm">
                  {t(dict, "app.brand")}
                </div>
                <div className="font-sans text-amber-100/65 text-sm">
                  {t(dict, "login.tagline")}
                </div>
              </div>
            </div>

            <h1 className="font-display text-4xl md:text-5xl gold-text leading-tight">
              Divine Access Portal
            </h1>
            <p className="font-serif text-lg text-amber-100/85 leading-relaxed">
              Enter the sacred workspace where charts, timing systems, and
              client insight converge.
            </p>

            <div className="mx-auto w-[260px] h-[260px] md:w-[320px] md:h-[320px] opacity-95">
              <MandalaSeal />
            </div>
          </div>
        </section>

        <section className="px-5 py-10 md:px-8 flex items-center justify-center">
          <div className="w-full max-w-md glass-card corner-ornament p-8 relative">
            <h2 className="font-display gold-text text-3xl mb-1">
              {t(dict, "login.title")}
            </h2>
            <p className="font-sans text-amber-100/70 mb-6">
              {t(dict, "login.subtitle")}
            </p>

            <form onSubmit={submit} className="space-y-4">
              <div>
                <label className="label-divine">Tenant Slug</label>
                <input
                  className="input-divine"
                  type="text"
                  value={form.tenantSlug}
                  onChange={(e) => update("tenantSlug", e.target.value.trim())}
                  placeholder="optional: your workspace slug"
                />
              </div>
              <div>
                <label className="label-divine">
                  {t(dict, "login.fields.email")}
                </label>
                <input
                  className="input-divine"
                  type="email"
                  value={form.email}
                  onChange={(e) => update("email", e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="label-divine">
                  {t(dict, "login.fields.password")}
                </label>
                <input
                  className="input-divine"
                  type="password"
                  value={form.password}
                  onChange={(e) => update("password", e.target.value)}
                  required
                />
              </div>

              {error && (
                <div className="text-sm text-red-300 border border-red-400/40 bg-red-950/20 px-3 py-2">
                  {error}
                </div>
              )}

              <button
                className="btn-primary w-full justify-center mt-2"
                type="submit"
                disabled={busy}
              >
                {busy ? "Signing in..." : t(dict, "login.actions.signIn")}
              </button>
              <button
                className="btn-ghost w-full justify-center"
                type="button"
                onClick={() => router.push(`/${lang}`)}
                disabled={busy}
              >
                {t(dict, "login.actions.back")}
              </button>
            </form>
          </div>
        </section>
      </div>
    </div>
  );
}
