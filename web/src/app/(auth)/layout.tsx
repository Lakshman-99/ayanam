import { PublicRoute } from "@/features/auth/components/public-route";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return <PublicRoute>{children}</PublicRoute>;
}