import type { Metadata } from "next";
import "./globals.css";
import { A2UIProvider } from "@/lib/a2ui/a2ui-provider";

export const metadata: Metadata = {
  title: "AI Car Matchmaker",
  description: "AI-powered car matching by conversation — Amulate Summer Hackathon 2026",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <A2UIProvider>{children}</A2UIProvider>
      </body>
    </html>
  );
}
