import type { Metadata } from "next";

import { AppShell } from "@/components/app-shell";
import { Providers } from "@/app/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "iGate OS POC",
  description: "Programmable enterprise operating system prototype"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
