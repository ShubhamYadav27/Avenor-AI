import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  metadataBase: new URL("https://avenor.ai"),
  title: "Avenor-AI | Predictive Revenue Intelligence Platform",
  description: "Know who will buy before your competitors do. Avenor-AI continuously monitors market intent signals (hiring, funding, tech stack shifts) to predict active buying windows for B2B sales teams.",
  keywords: [
    "Predictive Revenue Intelligence",
    "AI GTM Platform",
    "Buying Intent Signals",
    "B2B Sales Intelligence",
    "Revenue Intelligence Engine",
    "Account Intelligence",
    "Salesforce HubSpot AI Sync"
  ],
  authors: [{ name: "Avenor-AI Team" }],
  creator: "Avenor-AI",
  icons: {
    icon: [
      { url: "/favicon.ico?v=2" },
      { url: "/favicon-16x16.png?v=2", sizes: "16x16", type: "image/png" },
      { url: "/favicon-32x32.png?v=2", sizes: "32x32", type: "image/png" }
    ],
    apple: [
      { url: "/apple-touch-icon.png?v=2", sizes: "180x180", type: "image/png" }
    ],
    other: [
      { rel: "manifest", url: "/site.webmanifest?v=2" }
    ]
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://avenor.ai",
    title: "Avenor-AI | Predictive Revenue Intelligence Platform",
    description: "Know who will buy before your competitors do. Predict B2B buying intent using real-time market signals.",
    siteName: "Avenor-AI",
    images: [{ url: "/android-chrome-512x512.png?v=2", width: 512, height: 512, alt: "Avenor-AI Logo" }]
  },
  twitter: {
    card: "summary_large_image",
    title: "Avenor-AI | Predictive Revenue Intelligence Platform",
    description: "Predict B2B buying windows before competitors using AI intent signals.",
    creator: "@avenor_ai",
    images: ["/android-chrome-512x512.png?v=2"]
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

const themeInitializerScript = `
  (function() {
    try {
      var saved = localStorage.getItem('avenor-theme');
      if (saved === 'dark') {
        document.documentElement.classList.add('dark');
        document.documentElement.style.colorScheme = 'dark';
      } else if (saved === 'system') {
        var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
          document.documentElement.classList.add('dark');
          document.documentElement.style.colorScheme = 'dark';
        } else {
          document.documentElement.classList.add('light');
          document.documentElement.style.colorScheme = 'light';
        }
      } else {
        document.documentElement.classList.add('light');
        document.documentElement.style.colorScheme = 'light';
      }
    } catch (e) {}
  })();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased scroll-smooth" data-scroll-behavior="smooth" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico?v=2" sizes="any" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png?v=2" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png?v=2" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png?v=2" />
        <link rel="manifest" href="/site.webmanifest?v=2" />
        <script dangerouslySetInnerHTML={{ __html: themeInitializerScript }} />
      </head>
      <body className="h-full font-sans antialiased transition-colors duration-300">
        <a href="#main-content" className="skip-link">Skip to main content</a>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

