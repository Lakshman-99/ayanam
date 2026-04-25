import type { ReactNode } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BrandMark } from "@/components/brand/brand-mark";

interface AuthCardProps {
  title: string;
  description: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function AuthCard({ title, description, children, footer }: AuthCardProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-indigo-50 p-4">
      <div className="w-full max-w-md">
        <div className="mb-6 flex justify-center">
          <BrandMark size={48} showWordmark />
        </div>
        <Card>
          <CardHeader className="space-y-2">
            <CardTitle className="text-2xl">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </CardHeader>
          <CardContent>
            {children}
            {footer && <div className="mt-6 text-center text-sm text-slate-600">{footer}</div>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}