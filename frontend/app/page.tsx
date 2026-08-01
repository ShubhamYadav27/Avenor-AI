"use client";

import { useState } from "react";
import Script from "next/script";
import { Navbar } from "@/components/landing/Navbar";
import { HeroSection } from "@/components/landing/HeroSection";
import { SocialProofSection } from "@/components/landing/SocialProofSection";
import { ProblemSection } from "@/components/landing/ProblemSection";
import { HowItWorksSection } from "@/components/landing/HowItWorksSection";
import { InteractiveProductSection } from "@/components/landing/InteractiveProductSection";
import { FeaturesSection } from "@/components/landing/FeaturesSection";
import { EnterpriseSection } from "@/components/landing/EnterpriseSection";
import { ComparisonSection } from "@/components/landing/ComparisonSection";
import { CtaSection } from "@/components/landing/CtaSection";
import { Footer } from "@/components/landing/Footer";
import { DemoModal } from "@/components/landing/DemoModal";

export default function LandingPage() {
  const [isDemoOpen, setIsDemoOpen] = useState(false);

  const handleOpenDemo = () => setIsDemoOpen(true);
  const handleCloseDemo = () => setIsDemoOpen(false);

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": "https://avenor.ai/#organization",
        "name": "Avenor-AI",
        "url": "https://avenor.ai",
        "logo": "https://avenor.ai/favicon.ico",
        "description": "AI Powered Predictive Revenue Intelligence Platform for B2B sales and revenue teams.",
        "sameAs": [
          "https://www.linkedin.com/company/avnenor-ai"
        ]
      },
      {
        "@type": "SoftwareApplication",
        "@id": "https://avenor.ai/#software",
        "name": "Avenor Predictive Revenue Engine",
        "operatingSystem": "Web Browser",
        "applicationCategory": "BusinessApplication",
        "offers": {
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "USD"
        },
        "description": "Predicts future B2B buying opportunities using real-time market intent signals such as hiring, funding, leadership shifts, and tech stack adoption."
      }
    ]
  };

  return (
    <div className="relative min-h-screen bg-[#F5F7FB] dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans antialiased overflow-x-hidden transition-colors">
      {/* JSON-LD Structured Data for Production SEO */}
      <Script
        id="json-ld-schema"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Sticky Floating Navbar */}
      <Navbar onOpenDemo={handleOpenDemo} />

      {/* 1. Hero Section */}
      <main id="main-content">
        <HeroSection onOpenDemo={handleOpenDemo} />

        {/* Social Proof Audience Banner */}
        <SocialProofSection />

        {/* 2 & 3. The Problem & Why CRMs Are No Longer Enough */}
        <ProblemSection />

        {/* 4. How Avenor-AI Works */}
        <HowItWorksSection />

        {/* 5. Interactive Product Experience */}
        <InteractiveProductSection />

        {/* 6. Core Features Bento Grid */}
        <FeaturesSection />

        {/* 7. Enterprise Security & Architecture */}
        <EnterpriseSection />

        {/* 8. Why Avenor-AI (Comparison Matrix) */}
        <ComparisonSection />

        {/* 9. Final CTA */}
        <CtaSection onOpenDemo={handleOpenDemo} />
      </main>

      {/* 10. Enterprise Footer */}
      <Footer />

      {/* Interactive Demo Scheduling Modal */}
      <DemoModal isOpen={isDemoOpen} onClose={handleCloseDemo} />
    </div>
  );
}
