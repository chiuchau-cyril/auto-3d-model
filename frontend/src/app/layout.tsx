import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "鼓風機入口法蘭產生器",
  description: "業務用：依規格產生 DWG / PDF 法蘭工程圖",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-Hant">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
