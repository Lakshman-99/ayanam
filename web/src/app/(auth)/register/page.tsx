"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation, Trans } from "react-i18next";

import { AuthCard } from "@/features/auth/components/auth-card";
import { useRegister } from "@/features/auth/hooks/use-auth";
import { registerSchema, type RegisterInput } from "@/features/auth/schemas/auth-schemas";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { env } from "@/lib/config/env";

export default function RegisterPage() {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const register_ = useRegister();

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
  });

  const slug = useWatch({ control, name: "tenant_slug" });

  const onSubmit = handleSubmit(async (values) => {
    try {
      await register_.mutateAsync(values);
      router.push("/dashboard");
    } catch {
      // shown below
    }
  });

  return (
    <AuthCard
      title={t("register.title")}
      description={t("register.description")}
      footer={
        <>
          {t("register.have_account")}{" "}
          <Link href="/login" className="font-medium text-slate-900 hover:underline">
            {t("register.sign_in")}
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        <div className="space-y-2">
          <Label htmlFor="full_name">{t("register.name_label")}</Label>
          <Input id="full_name" autoComplete="name" {...register("full_name")} />
          {errors.full_name && (
            <p className="text-sm text-red-600">{t(errors.full_name.message as never)}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="tenant_display_name">{t("register.business_label")}</Label>
          <Input id="tenant_display_name" {...register("tenant_display_name")} />
          {errors.tenant_display_name && (
            <p className="text-sm text-red-600">{t(errors.tenant_display_name.message as never)}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="tenant_slug">{t("register.slug_label")}</Label>
          <div className="flex items-center rounded-md border border-slate-200 bg-white focus-within:ring-2 focus-within:ring-slate-300">
            <Input
              id="tenant_slug"
              className="border-0 focus-visible:ring-0"
              placeholder={t("register.slug_placeholder")}
              {...register("tenant_slug")}
            />
            <span className="pr-3 text-sm text-slate-500">.{env.appDomain}</span>
          </div>
          {slug && !errors.tenant_slug && (
            <p className="text-xs text-slate-500">
              <Trans
                ns="auth"
                i18nKey="register.slug_preview"
                values={{ slug, domain: env.appDomain }}
                components={{ strong: <strong /> }}
              />
            </p>
          )}
          {errors.tenant_slug && (
            <p className="text-sm text-red-600">{t(errors.tenant_slug.message as never)}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">{t("register.email_label")}</Label>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
          {errors.email && (
            <p className="text-sm text-red-600">{t(errors.email.message as never)}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">{t("register.password_label")}</Label>
          <Input id="password" type="password" autoComplete="new-password" {...register("password")} />
          {errors.password && (
            <p className="text-sm text-red-600">{t(errors.password.message as never)}</p>
          )}
        </div>

        {register_.error && (
          <p className="text-sm text-red-600">
            {extractApiError(register_.error) ?? t("register.failed")}
          </p>
        )}

        <Button type="submit" className="w-full" disabled={register_.isPending}>
          {register_.isPending ? t("register.submitting") : t("register.submit")}
        </Button>
      </form>
    </AuthCard>
  );
}

function extractApiError(err: unknown): string | null {
  if (err && typeof err === "object" && "error" in err) {
    const e = (err as { error: { message?: string } }).error;
    return e?.message ?? null;
  }
  return null;
}