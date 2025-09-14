import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Running Coach",
  description: "Your personal AI-powered running coach and training plan builder",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-GB">
      <body style={{ 
        margin: 0, 
        padding: 0, 
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        backgroundColor: "#f9fafb",
        minHeight: "100vh"
      }}>
        <main style={{ 
          minHeight: "100vh",
          backgroundColor: "#f9fafb"
        }}>
          {children}
        </main>
      </body>
    </html>
  );
} 