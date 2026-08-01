export interface NavItem {
  label: string;
  href: string;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Product", href: "#product" },
  { label: "Problem", href: "#problem" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Capabilities", href: "#capabilities" },
  { label: "Comparison", href: "#comparison" },
  { label: "Enterprise", href: "#enterprise" },
];

export interface SignalSample {
  id: string;
  company: string;
  logoUrl?: string;
  domain: string;
  signalType: "Hiring" | "Funding" | "Leadership" | "Tech Stack" | "Product Launch" | "CRM Activity";
  title: string;
  description: string;
  score: number;
  timeAgo: string;
  buyingStage: "Immediate Window" | "High Intent" | "Evaluating" | "Budget Approved";
}

export const HERO_SIGNALS: SignalSample[] = [
  {
    id: "sig-1",
    company: "Acme Corp",
    domain: "acme.io",
    signalType: "Hiring",
    title: "Expanded Sales Engineering Team (+6 Roles)",
    description: "Posted 6 senior enterprise SE roles in last 48 hours following Series B announcement.",
    score: 98,
    timeAgo: "12m ago",
    buyingStage: "Immediate Window"
  },
  {
    id: "sig-2",
    company: "ScaleFlow",
    domain: "scaleflow.dev",
    signalType: "Leadership",
    title: "New VP of Revenue Operations Appointed",
    description: "Former Stripe Director of RevOps joined to replace legacy GTM stack.",
    score: 95,
    timeAgo: "44m ago",
    buyingStage: "Budget Approved"
  },
  {
    id: "sig-3",
    company: "Vortex Analytics",
    domain: "vortex.ai",
    signalType: "Tech Stack",
    title: "Removed Competitor Script & Added Salesforce SDK",
    description: "DNS & web tracker shift signals active GTM tooling consolidation cycle.",
    score: 91,
    timeAgo: "2h ago",
    buyingStage: "High Intent"
  },
  {
    id: "sig-4",
    company: "HyperCloud",
    domain: "hypercloud.com",
    signalType: "Funding",
    title: "$45M Series B Led by Index Ventures",
    description: "Earmarked 40% of funds for GTM expansion & automated sales intelligence.",
    score: 96,
    timeAgo: "3h ago",
    buyingStage: "Immediate Window"
  }
];

export interface ProblemCard {
  title: string;
  subtitle: string;
  crmReality: string;
  avenorPrediction: string;
  impact: string;
  badge: string;
}

export const PROBLEM_CARDS: ProblemCard[] = [
  {
    title: "Historical Record vs. Future Prediction",
    subtitle: "CRMs store what happened yesterday. Avenor-AI predicts what will happen tomorrow.",
    crmReality: "Traditional CRMs wait for reps to manually log deal stages after meetings occur.",
    avenorPrediction: "Avenor-AI continuously scans external market signals to identify buying windows 3 weeks before competitors.",
    impact: "3.4x higher first-touch response rate",
    badge: "Timing Window"
  },
  {
    title: "Static Prospect Databases vs. Live Buying Signals",
    subtitle: "Static contacts decay fast. Live signals pinpoint exact buying intent.",
    crmReality: "Cold list providers dump static email addresses with zero context on budget or intent.",
    avenorPrediction: "Avenor-AI correlates hiring sprees, executive changes, tech stack shifts, and funding in real time.",
    impact: "82% reduction in wasted sales outreach",
    badge: "Intent Correlation"
  },
  {
    title: "Blind Sales Reps vs. Autonomous AI Research",
    subtitle: "Manual account research wastes 40% of AE time.",
    crmReality: "Reps spend hours scanning LinkedIn, news, and SEC filings to write basic outreach.",
    avenorPrediction: "Avenor-AI autonomously generates 1-page executive deal briefings with hyper-personalized value props.",
    impact: "12+ hours saved per AE weekly",
    badge: "AI Briefings"
  }
];

export interface HowItWorksStep {
  step: string;
  title: string;
  subtitle: string;
  description: string;
  details: string[];
  iconName: string;
}

export const HOW_IT_WORKS_STEPS: HowItWorksStep[] = [
  {
    step: "01",
    title: "Discover Signals",
    subtitle: "Continuous Market Scanning",
    description: "Avenor-AI monitors 40+ external intent indicators across millions of B2B companies globally 24/7.",
    details: [
      "Series A–D Funding Rounds & SEC Filings",
      "Key Executive & GTM Leadership Hires",
      "Tech Stack & Infrastructure Migrations",
      "Product Launches & Pricing Page Changes"
    ],
    iconName: "Radar"
  },
  {
    step: "02",
    title: "AI Research",
    subtitle: "Autonomous Account Profiling",
    description: "Our proprietary AI engine synthesizes raw signals into deep account intelligence and strategic context.",
    details: [
      "Identify decision makers & champion personas",
      "Map company pain points to your GTM playbooks",
      "Calculate predictive Revenue Opportunity Scores",
      "Filter out unqualified leads automatically"
    ],
    iconName: "Cpu"
  },
  {
    step: "03",
    title: "Revenue Intelligence",
    subtitle: "Actionable Pipeline Prioritization",
    description: "Transform chaotic market noise into a prioritized feed of high-intent accounts entering a buying window.",
    details: [
      "Real-time Buying Window notifications",
      "Automated account ranking by conversion probability",
      "Bi-directional CRM & HubSpot sync",
      "AI Executive Sales Briefings ready on demand"
    ],
    iconName: "TrendingUp"
  },
  {
    step: "04",
    title: "Close More Deals",
    subtitle: "AI Execution & Deal Coaching",
    description: "Empower AEs and SDRs to reach out with perfect timing, compelling messaging, and strategic playbooks.",
    details: [
      "Hyper-relevant AI Email drafts tailored to signals",
      "Objection handling & competitive positioning",
      "Continuous learning engine based on closed-won outcomes",
      "Expanded pipeline velocity across your entire revenue team"
    ],
    iconName: "Zap"
  }
];

export interface InteractiveTabItem {
  id: string;
  label: string;
  iconName: string;
  companyName: string;
  score: number;
  buyingWindow: string;
  signalSummary: string;
  aiBriefing: string;
  recommendedEmail: {
    subject: string;
    body: string;
  };
  coachAdvice: string;
}

export const INTERACTIVE_TABS: InteractiveTabItem[] = [
  {
    id: "account-feed",
    label: "Account Signal Feed",
    iconName: "Activity",
    companyName: "CloudScale Inc.",
    score: 97,
    buyingWindow: "Open — Next 14 Days",
    signalSummary: "Announced $35M Series B funding + Hiring 5 Senior Enterprise Account Executives + Switched CRM infrastructure.",
    aiBriefing: "CloudScale is rapidly scaling their GTM team post-funding. The incoming VP of Sales is replacing outdated sales enablement tools. Reaching out now aligns directly with their Q3 budget allocation.",
    recommendedEmail: {
      subject: "Scaling GTM intelligence for CloudScale's new AE team",
      body: "Hi Marcus,\n\nCongrats on the Series B funding and expanding the sales team! Noticed CloudScale is bringing on 5 new Enterprise AEs this month.\n\nMost fast-growing SaaS revenue teams face a challenge where new AEs take 4+ months to ramp on account research. Avenor-AI predicts buying intent across your target accounts so new AEs hit quota in week 3.\n\nWorth a 10-min brief next Tuesday?"
    },
    coachAdvice: "Focus on AE onboarding ramp time and automated signal alerts. Highlight integration with their existing tech stack."
  },
  {
    id: "buying-window",
    label: "Buying Intent Gauge",
    iconName: "Target",
    companyName: "DataFlow Systems",
    score: 94,
    buyingWindow: "Peak Intent Window",
    signalSummary: "New Chief Revenue Officer hired 12 days ago. Posted job openings for RevOps Manager & Sales Operations Director.",
    aiBriefing: "DataFlow's new CRO is actively evaluating modern revenue intelligence tools to replace legacy data providers. High probability of budget approval within 21 days.",
    recommendedEmail: {
      subject: "Streamlining GTM operations at DataFlow Systems",
      body: "Hi Sarah,\n\nWelcome to the CRO role at DataFlow! Seeing your team prioritize RevOps infrastructure expansion is exciting.\n\nInstead of burdening your reps with manual prospecting and outdated lists, Avenor-AI automates intent detection so your AEs only reach out when companies enter an active buying window.\n\nOpen to reviewing our 2-minute interactive workflow?"
    },
    coachAdvice: "Emphasize ROI on RevOps efficiency and elimination of manual rep research hours."
  },
  {
    id: "ai-briefing",
    label: "AI Sales Briefing",
    iconName: "FileText",
    companyName: "OmniTech Global",
    score: 92,
    buyingWindow: "Evaluating GTM Vendors",
    signalSummary: "Website traffic spiked + Tech stack scan detected removal of legacy ZoomInfo tracker.",
    aiBriefing: "OmniTech is actively seeking an AI-first alternative to traditional contact databases. Key pain points include low email deliverability and missing buying timing signals.",
    recommendedEmail: {
      subject: "AI intent prediction vs static databases for OmniTech",
      body: "Hi David,\n\nNoticed OmniTech is refining your outbound GTM tech stack this quarter.\n\nWhile legacy tools provide static contact lists, Avenor-AI predicts future buying opportunities using real-time market signals (hiring, funding, tech changes). Our customers see a 3.2x increase in meeting booked rates.\n\nWould love to show you a live comparison for 5 of your target accounts."
    },
    coachAdvice: "Position against legacy contact lists. Pitch live signal tracking + automated AI briefing capabilities."
  }
];

export interface CapabilityFeature {
  id: string;
  title: string;
  description: string;
  iconName: string;
  badge?: string;
  size: "normal" | "wide";
  gradient: string;
}

export const CAPABILITIES: CapabilityFeature[] = [
  {
    id: "ai-research",
    title: "Autonomous AI Research",
    description: "Deep-dive account intelligence gathered in seconds. Avenor-AI analyzes filings, job postings, news, and GTM shifts automatically.",
    iconName: "BrainCircuit",
    size: "wide",
    gradient: "from-blue-500/10 via-indigo-500/10 to-transparent"
  },
  {
    id: "predictive-signals",
    title: "Predictive Buying Signals",
    description: "Detect buying windows before competitors. Correlate hiring sprees, funding, tech stack changes, and leadership moves.",
    iconName: "Sparkles",
    size: "normal",
    gradient: "from-purple-500/10 via-pink-500/10 to-transparent"
  },
  {
    id: "revenue-feed",
    title: "Live Revenue Feed",
    description: "Real-time stream of high-priority revenue opportunities ranked by predictive conversion probability score.",
    iconName: "Radio",
    size: "normal",
    gradient: "from-cyan-500/10 via-blue-500/10 to-transparent"
  },
  {
    id: "ai-email",
    title: "AI Email Generator",
    description: "Draft hyper-personalized, signal-based outreach emails in seconds. Tailored to specific intent triggers and buyer personas.",
    iconName: "MailCheck",
    size: "normal",
    gradient: "from-emerald-500/10 via-teal-500/10 to-transparent"
  },
  {
    id: "ai-briefing",
    title: "AI Executive Sales Briefings",
    description: "Get 1-page deal strategy cheat sheets before every discovery call with talking points, pain points, and buyer context.",
    iconName: "FileSpreadsheet",
    size: "wide",
    gradient: "from-indigo-500/10 via-indigo-500/10 to-transparent"
  },
  {
    id: "ai-coach",
    title: "AI Sales Coach",
    description: "Real-time deal strategy guidance and objection handling tailored to company size, industry, and competitive dynamics.",
    iconName: "Compass",
    size: "normal",
    gradient: "from-amber-500/10 via-orange-500/10 to-transparent"
  },
  {
    id: "hubspot-integration",
    title: "HubSpot Integration",
    description: "Seamless native HubSpot integration. Push enriched accounts, buying signals, and intent scores directly to your CRM.",
    iconName: "Layers",
    size: "normal",
    gradient: "from-rose-500/10 via-pink-500/10 to-transparent"
  },
  {
    id: "crm-sync",
    title: "Bi-Directional CRM Sync",
    description: "Keep pipeline data consistent. Automatic bi-directional synchronization ensures your reps never enter duplicate data.",
    iconName: "RefreshCw",
    size: "normal",
    gradient: "from-blue-500/10 via-teal-500/10 to-transparent"
  },
  {
    id: "learning-engine",
    title: "Adaptive Learning Engine",
    description: "Avenor-AI gets smarter over time by analyzing closed-won deals and refining signal weights for your specific ICP.",
    iconName: "TrendingUp",
    size: "wide",
    gradient: "from-indigo-500/10 via-purple-500/10 to-transparent"
  },
  {
    id: "revenue-copilot",
    title: "Revenue Copilot",
    description: "Autonomous GTM agent executing background research, monitoring accounts, and recommending next best actions.",
    iconName: "Bot",
    badge: "Beta",
    size: "normal",
    gradient: "from-fuchsia-500/10 via-purple-500/10 to-transparent"
  }
];

export interface ComparisonRow {
  capability: string;
  crm: string | boolean;
  prospectingTools: string | boolean;
  intentTools: string | boolean;
  avenor: string | boolean;
  highlight: string;
}

export const COMPARISON_DATA: ComparisonRow[] = [
  {
    capability: "Primary Core Focus",
    crm: "Historical Logbook",
    prospectingTools: "Contact Directories",
    intentTools: "Isolated Web Surges",
    avenor: "Predictive Intent & Revenue Action",
    highlight: "Full GTM Revenue Intelligence"
  },
  {
    capability: "Predictive Buying Opportunity Scoring",
    crm: false,
    prospectingTools: false,
    intentTools: "Basic / Keyword",
    avenor: "AI Multi-Signal Intelligence",
    highlight: "98% Signal Accuracy"
  },
  {
    capability: "Autonomous Account Research & Briefings",
    crm: false,
    prospectingTools: false,
    intentTools: false,
    avenor: true,
    highlight: "Saved 12+ hrs/week per AE"
  },
  {
    capability: "Real-time Buying Signal Correlation",
    crm: false,
    prospectingTools: false,
    intentTools: "Limited",
    avenor: true,
    highlight: "40+ Signal Sources Monitored"
  },
  {
    capability: "Signal-Based AI Outreach Generator",
    crm: false,
    prospectingTools: "Generic Templates",
    intentTools: false,
    avenor: true,
    highlight: "3.4x Higher Response Rate"
  },
  {
    capability: "Adaptive ICP Learning Engine",
    crm: false,
    prospectingTools: false,
    intentTools: false,
    avenor: true,
    highlight: "Learns from Closed-Won Deals"
  }
];

export interface EnterpriseFeature {
  title: string;
  description: string;
  iconName: string;
}

export const ENTERPRISE_FEATURES: EnterpriseFeature[] = [
  {
    title: "Enterprise Ready Architecture",
    description: "Built from the ground up for high-velocity revenue organizations demanding enterprise-grade stability and reliability.",
    iconName: "ShieldCheck"
  },
  {
    title: "Encrypted Credentials & API Keys",
    description: "Bank-level AES-256 encryption for all CRM OAuth tokens, API secrets, and sensitive integration credentials.",
    iconName: "Lock"
  },
  {
    title: "Workspace Isolation",
    description: "Strict multi-tenant data boundaries ensuring absolute privacy, data governance, and strict tenant separation.",
    iconName: "Server"
  },
  {
    title: "Secure Authentication & RBAC",
    description: "Role-based access controls and enterprise session security tailored to SDRs, AEs, RevOps, and Executive leadership.",
    iconName: "UserCheck"
  },
  {
    title: "Scalable Microsecond Signal Pipeline",
    description: "Processes tens of millions of external intent signals daily with microsecond latency and high availability.",
    iconName: "Zap"
  },
  {
    title: "Production-Ready Infrastructure",
    description: "Resilient cloud deployment monitored 24/7 with zero downtime release pipelines and automated failovers.",
    iconName: "Cpu"
  }
];

export const FOOTER_LINKS = {
  product: [
    { label: "Signal Feed", href: "#product" },
    { label: "AI Research", href: "#capabilities" },
    { label: "Intent Scoring", href: "#product" },
    { label: "HubSpot Integration", href: "#capabilities" },
    { label: "Revenue Copilot", href: "#capabilities" },
  ],
  solutions: [
    { label: "Series A–C SaaS", href: "#problem" },
    { label: "B2B Sales Teams", href: "#problem" },
    { label: "Revenue Operations", href: "#problem" },
    { label: "GTM Leadership", href: "#problem" },
  ],
  resources: [
    { label: "Documentation", href: "/login" },
    { label: "API Reference", href: "/login" },
    { label: "Security & Trust", href: "#enterprise" },
    { label: "System Status", href: "/login" },
    { label: "Careers", href: "/login" },
  ],
  legal: [
    { label: "Privacy Policy", href: "/login" },
    { label: "Terms of Service", href: "/login" },
    { label: "Security Overview", href: "#enterprise" },
    { label: "Cookie Preferences", href: "/login" },
  ]
};

export const COMPANY_INFO = {
  primaryEmail: "avenor@avenorai.in",
  supportEmail: "support@avenorai.in",
  linkedInUrl: "https://www.linkedin.com/company/avnenor-ai",
};
