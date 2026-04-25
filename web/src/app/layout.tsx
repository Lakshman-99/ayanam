import type { Metadata } from "next";
import { AppProviders } from "@/providers/app-providers";
import { brand } from "@/lib/config/brand";
import "./globals.css";

export const metadata: Metadata = {
  title: `${brand.name} — ${brand.tagline}`,
  description: "Enterprise KP Astrology platform for professional astrologers.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}