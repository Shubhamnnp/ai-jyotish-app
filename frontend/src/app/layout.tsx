import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'JyotishOS — Premium Vedic Astrology & Ephemeris Platform',
  description: 'Enterprise-grade classical Vedic astrology computation platform benchmarked against Parashara’s Light and Shri Jyoti Star.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="hi" className={`${inter.variable} dark`}>
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased font-sans selection:bg-amber-500/30 selection:text-amber-200">
        {children}
      </body>
    </html>
  );
}
