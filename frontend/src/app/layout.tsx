import type { Metadata } from "next";
import "./globals.css";
import { CopilotKitProvider } from "@/components/CopilotKitProvider";

export const metadata: Metadata = {
  title: "AI Car Matchmaker",
  description: "AI-powered car matching by conversation — Amulate Summer Hackathon 2026",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <CopilotKitProvider>{children}</CopilotKitProvider>
      </body>
    </html>
  );
}
