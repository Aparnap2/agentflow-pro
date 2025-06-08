import { Toaster } from 'sonner';
import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import { ThemeProvider } from '@/components/theme-provider';
import { cn } from '@/lib/utils';
import './globals.css';
import { auth } from '@/auth';
import { SessionProvider } from 'next-auth/react';
import { AgentProvider } from '@/contexts/AgentContext';

// Font configuration
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-sans',
});

export const metadata: Metadata = {
  title: {
    default: 'AgentFlow Pro',
    template: '%s | AgentFlow Pro',
  },
  description: 'AI Agent Automation Platform for SMBs and Niche Corporations',
  keywords: [
    'AI',
    'Automation',
    'Agents',
    'Business',
    'Productivity',
    'LLM',
    'Workflow',
  ],
  authors: [
    {
      name: 'AgentFlow Team',
      url: 'https://agentflow.pro',
    },
  ],
  creator: 'AgentFlow',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://agentflow.pro',
    title: 'AgentFlow Pro',
    description: 'AI Agent Automation Platform for SMBs and Niche Corporations',
    siteName: 'AgentFlow Pro',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AgentFlow Pro',
    description: 'AI Agent Automation Platform for SMBs and Niche Corporations',
    images: ['/og-image.jpg'],
    creator: '@agentflow',
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

// Theme color script for better mobile experience
const THEME_COLOR_SCRIPT = `\
(function() {
  function getThemeColor() {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return '#000000';
    }
    return '#ffffff';
  }
  
  function updateThemeColor() {
    const color = getThemeColor();
    document.querySelector('meta[name="theme-color"]')
      ?.setAttribute('content', color);
  }
  
  // Update on initial load
  updateThemeColor();
  
  // Update on theme change
  window.matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', updateThemeColor);
})();`;

interface RootLayoutProps {
  children: React.ReactNode;
  modal?: React.ReactNode;
}

export default async function RootLayout({
  children,
  modal,
}: RootLayoutProps) {
  const session = await auth();
  
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_COLOR_SCRIPT }} />
      </head>
      <body
        className={cn(
          'min-h-screen bg-background font-sans antialiased',
          inter.variable
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <SessionProvider session={session}>
            <AgentProvider>
              {children}
              {modal}
              <Toaster position="top-center" richColors />
            </AgentProvider>
          </SessionProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
