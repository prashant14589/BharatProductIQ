import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BharatProductIQ — Product Discovery",
  description: "AI-powered ecommerce product discovery for the Indian market",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-slate-50 text-slate-900">
        {children}
      </body>
    </html>
  );
}
