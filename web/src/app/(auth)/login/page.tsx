"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";

import { AuthCard } from "@/features/auth/components/auth-card";
import { useLogin } from "@/features/auth/hooks/use-auth";
import { loginSchema, type LoginInput } from "@/features/auth/schemas/auth-schemas";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const login = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = handleSubmit(async (values) => {
    try {
      await login.mutateAsync(values);
      router.push("/dashboard");
    } catch {
      // error rendered via login.error
    }
  });

  return (
    <AuthCard
      title={t("login.title")}
      description={t("login.description")}
      footer={
        <>
          {t("login.no_account")}{" "}
          <Link href="/register" className="font-medium text-slate-900 hover:underline">
            {t("login.create_one")}
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        <div className="space-y-2">
          <Label htmlFor="email">{t("login.email_label")}</Label>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
          {errors.email && <p className="text-sm text-red-600">{t(errors.email.message as never)}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">{t("login.password_label")}</Label>
          <Input id="password" type="password" autoComplete="current-password" {...register("password")} />
          {errors.password && <p className="text-sm text-red-600">{t(errors.password.message as never)}</p>}
        </div>

        {login.error && (
          <p className="text-sm text-red-600">
            {extractApiError(login.error) ?? t("login.failed")}
          </p>
        )}

        <Button type="submit" className="w-full" disabled={login.isPending}>
          {login.isPending ? t("login.submitting") : t("login.submit")}
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