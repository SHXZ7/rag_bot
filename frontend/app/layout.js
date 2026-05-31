import "./globals.css";

export const metadata = {
  title: "Creator Lens",
  description: "Compare creator videos with transcript RAG"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
