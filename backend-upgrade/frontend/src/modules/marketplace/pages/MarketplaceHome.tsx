import React, { useState, useEffect } from 'react';
import { AppCard } from '../components/AppCard';
import { InstallWizard } from '../components/InstallWizard';

// Define the shape of our API response (matching backend Phase 8.2)
interface AppResponse {
  id: string;
  name: string;
  description: string;
  developer_name: string;
  category: string;
  app_type: 'Official' | 'Partner' | 'Private';
  version: string;
}

export const MarketplaceHome: React.FC = () => {
  const [apps, setApps] = useState<AppResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedApp, setSelectedApp] = useState<AppResponse | null>(null);
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  useEffect(() => {
    // Simulate fetching from the Phase 8.2 API
    const fetchApps = async () => {
      setLoading(true);
      try {
        // In reality, this would be an API call to /marketplace/apps
        // Using mock data structurally matching the backend models
        const mockApps: AppResponse[] = [
          {
            id: 'app-salesforce',
            name: 'Salesforce Sync',
            description: 'Native Integration Hub provider for Salesforce. Sync Accounts, Opportunities, and Contacts in real-time.',
            developer_name: 'AVENOR',
            category: 'CRM',
            app_type: 'Official',
            version: '2.0.0'
          },
          {
            id: 'app-hubspot',
            name: 'HubSpot OS',
            description: 'Complete HubSpot synchronization platform. Bi-directional pipeline syncing.',
            developer_name: 'AVENOR',
            category: 'CRM',
            app_type: 'Official',
            version: '2.1.0'
          },
          {
            id: 'app-gong',
            name: 'Gong Intelligence',
            description: 'Ingest Gong conversational intelligence directly into the AVENOR Context Engine.',
            developer_name: 'Gong.io',
            category: 'Revenue Intelligence',
            app_type: 'Partner',
            version: '1.4.0'
          },
          {
            id: 'app-clearbit',
            name: 'Clearbit Enrichment',
            description: 'Automatically enrich CanonicalCompanies with Clearbit firmographic data.',
            developer_name: 'Clearbit',
            category: 'Marketing',
            app_type: 'Partner',
            version: '1.0.0'
          }
        ];
        
        // Simulate network delay
        setTimeout(() => {
          setApps(mockApps);
          setLoading(false);
        }, 800);
      } catch (e) {
        console.error("Failed to load marketplace apps", e);
        setLoading(false);
      }
    };

    fetchApps();
  }, []);

  const handleAppClick = (id: string) => {
    const app = apps.find(a => a.id === id);
    if (app) {
      setSelectedApp(app);
      setIsWizardOpen(true);
    }
  };

  const filteredApps = apps.filter(app => 
    app.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    app.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      {/* Header & Search */}
      <div className="max-w-7xl mx-auto mb-12 flex flex-col md:flex-row justify-between items-center gap-6">
        <div>
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            Enterprise Marketplace
          </h1>
          <p className="text-white/60 mt-2 text-lg">Extend AVENOR-AI with powerful apps, integrations, and agents.</p>
        </div>
        
        <div className="relative w-full md:w-96">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input 
            type="text" 
            placeholder="Search apps, integrations, publishers..." 
            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all glass-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Featured Section */}
      <div className="max-w-7xl mx-auto mb-16">
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
          <span className="text-yellow-400">★</span> Featured Integrations
        </h2>
        
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="glass-card h-64 animate-pulse bg-white/5 border border-white/10 rounded-xl"></div>
            ))}
          </div>
        ) : filteredApps.length === 0 ? (
          <div className="glass-card p-12 text-center rounded-2xl border border-white/10 bg-white/5 flex flex-col items-center justify-center">
            <svg className="w-16 h-16 text-white/20 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            <h3 className="text-xl font-medium text-white/80">No apps found</h3>
            <p className="text-white/50 mt-2">Try adjusting your search query.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredApps.map(app => (
              <AppCard 
                key={app.id}
                id={app.id}
                name={app.name}
                description={app.description}
                developerName={app.developer_name}
                category={app.category}
                appType={app.app_type}
                rating={4.8} // Mock
                onClick={handleAppClick}
              />
            ))}
          </div>
        )}
      </div>

      {/* Installation Wizard Modal */}
      {selectedApp && (
        <InstallWizard 
          appId={selectedApp.id}
          appName={selectedApp.name}
          isOpen={isWizardOpen}
          onClose={() => setIsWizardOpen(false)}
          onComplete={(installId) => {
            setIsWizardOpen(false);
            console.log("Installation Complete. ID:", installId);
            // Navigate to installed apps page in real app
          }}
        />
      )}
    </div>
  );
};
