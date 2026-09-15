import type { Metadata } from "next";
import "./styles.css";
import "./release.css";

export const metadata: Metadata = {
  title: "ClearSpend",
  description: "Evidence-first reimbursement review",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
