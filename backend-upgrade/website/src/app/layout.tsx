import './globals.css'
import { Inter } from 'next/font/google'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'AVENOR-AI | Predictive Revenue Intelligence',
  description: 'The Intelligence Layer for Modern Revenue Teams.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body className={`${inter.className} min-h-screen flex flex-col bg-[#050505]`}>
        {/* Sticky Navigation */}
        <header className="fixed top-0 w-full z-50 glass-card border-b border-white/10 transition-all">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-white">A</div>
              <span className="font-bold text-xl tracking-tight text-white">AVENOR-AI</span>
            </Link>
            <nav className="hidden lg:flex items-center gap-6 text-sm font-medium text-white/70">
              <Link href="/platform" className="hover:text-white transition">Platform</Link>
              <Link href="/intelligence-cloud" className="hover:text-white transition">Intelligence</Link>
              <Link href="/developers" className="hover:text-white transition">Developers</Link>
              <Link href="/security" className="hover:text-white transition">Security</Link>
              <Link href="/pricing" className="hover:text-white transition">Pricing</Link>
            </nav>
            <div className="flex items-center gap-4">
              <Link href="/contact" className="text-sm font-medium text-white/70 hover:text-white">Sign In</Link>
              <Link href="/contact" className="px-4 py-2 rounded-lg bg-white text-black font-bold text-sm hover:bg-white/90 transition shadow-[0_0_15px_rgba(255,255,255,0.3)]">Book Demo</Link>
            </div>
          </div>
        </header>

        <main className="flex-1 pt-16 relative">
          {children}
        </main>

        {/* Global Footer */}
        <footer className="border-t border-white/10 bg-[#020202] pt-20 pb-10">
          <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 mb-16">
            <div className="col-span-2 lg:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 rounded bg-gradient-to-br from-indigo-500 to-purple-600"></div>
                <span className="font-bold text-lg text-white">AVENOR-AI</span>
              </div>
              <p className="text-sm text-white/50 mb-6 max-w-xs">The world's AI operating system for B2B Revenue Intelligence. Know who will buy, when, and why.</p>
            </div>
            
            <div>
              <h4 className="font-bold text-white mb-4">Platform</h4>
              <ul className="space-y-2 text-sm text-white/60">
                <li><Link href="/revenue-os" className="hover:text-white">Revenue OS</Link></li>
                <li><Link href="/ai" className="hover:text-white">Copilot</Link></li>
                <li><Link href="/knowledge-graph" className="hover:text-white">Knowledge Graph</Link></li>
                <li><Link href="/agents" className="hover:text-white">Agents</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-white/60">
                <li><Link href="/company" className="hover:text-white">About</Link></li>
                <li><Link href="/careers" className="hover:text-white">Careers</Link></li>
                <li><Link href="/blog" className="hover:text-white">Blog</Link></li>
                <li><Link href="/contact" className="hover:text-white">Contact</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Developers</h4>
              <ul className="space-y-2 text-sm text-white/60">
                <li><Link href="/docs" className="hover:text-white">Documentation</Link></li>
                <li><Link href="/architecture" className="hover:text-white">Architecture</Link></li>
                <li><Link href="/roadmap" className="hover:text-white">Roadmap</Link></li>
                <li><Link href="/integrations" className="hover:text-white">Integrations</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Trust</h4>
              <ul className="space-y-2 text-sm text-white/60">
                <li><Link href="/security" className="hover:text-white">Security</Link></li>
                <li><Link href="/compliance" className="hover:text-white">Compliance</Link></li>
                <li><Link href="#" className="hover:text-white">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>
          <div className="max-w-7xl mx-auto px-6 border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between text-sm text-white/40">
            <p>© 2026 AVENOR-AI. All rights reserved.</p>
            <div className="flex gap-4 mt-4 md:mt-0">
              <span>System Status: All Systems Operational</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
