import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "Goalkeep · KC-2 Workspace",
  description: "Protected local synthetic IDS preview",
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
