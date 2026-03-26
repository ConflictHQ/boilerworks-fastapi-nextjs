import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Boilerworks",
  description: "Boilerworks FastAPI + Next.js template",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <script src="https://cdn.tailwindcss.com" />
      </head>
      <body className="min-h-screen bg-gray-50">{children}</body>
    </html>
  );
}
