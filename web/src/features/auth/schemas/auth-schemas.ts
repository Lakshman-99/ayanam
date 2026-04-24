import { z } from "zod";

const SLUG_RE = /^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$/;
const RESERVED_SLUGS = new Set(["www", "app", "api", "admin", "mail", "static", "assets", "cdn"]);

export const loginSchema = z.object({
  email: z.string().email("validation.email_invalid"),
  password: z.string().min(1, "validation.password_required"),
});

export const registerSchema = z.object({
  email: z.string().email("validation.email_invalid"),
  password: z
    .string()
    .min(8, "validation.password_min")
    .max(100, "validation.password_max")
    .refine((v) => /\d/.test(v), "validation.password_needs_digit")
    .refine((v) => /[a-zA-Z]/.test(v), "validation.password_needs_letter"),
  full_name: z.string().min(1, "validation.name_required").max(255),
  tenant_slug: z
    .string()
    .min(3, "validation.slug_min")
    .max(63, "validation.slug_max")
    .transform((v) => v.toLowerCase().trim())
    .refine((v) => SLUG_RE.test(v), "validation.slug_format")
    .refine((v) => !RESERVED_SLUGS.has(v), "validation.slug_reserved"),
  tenant_display_name: z.string().min(1, "validation.business_required").max(255),
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;