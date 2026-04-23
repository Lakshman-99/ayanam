import "./globals.css";

export const metadata = {
  title: "Ayanam Astrology",
  description:
    "Professional astrology workspace for client chart management and analysis.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
