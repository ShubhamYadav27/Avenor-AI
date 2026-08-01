import React, { useState } from 'react';

interface InstallWizardProps {
  appId: string;
  appName: string;
  isOpen: boolean;
  onClose: () => void;
  onComplete: (installId: string) => void;
}

type WizardStep = 'Overview' | 'Permissions' | 'Dependencies' | 'Configuration' | 'Confirmation' | 'Progress' | 'Completed';

const STEPS: WizardStep[] = [
  'Overview', 'Permissions', 'Dependencies', 'Configuration', 'Confirmation', 'Progress', 'Completed'
];

export const InstallWizard: React.FC<InstallWizardProps> = ({ appId, appName, isOpen, onClose, onComplete }) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [installId, setInstallId] = useState<string | null>(null);
  
  if (!isOpen) return null;
  
  const step = STEPS[currentStepIndex];

  const handleNext = async () => {
    if (step === 'Confirmation') {
      // Simulate API call to POST /marketplace/installations
      setCurrentStepIndex(STEPS.indexOf('Progress'));
      setTimeout(() => {
        setInstallId(`inst-${Math.random().toString(36).substr(2, 9)}`);
        setCurrentStepIndex(STEPS.indexOf('Completed'));
      }, 3000);
    } else if (currentStepIndex < STEPS.length - 1) {
      setCurrentStepIndex(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) setCurrentStepIndex(prev => prev - 1);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="glass-modal w-full max-w-3xl bg-[#111]/90 border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-300">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-white/5">
          <h2 className="text-xl font-semibold text-white">Install {appName}</h2>
          {step !== 'Progress' && step !== 'Completed' && (
            <button onClick={onClose} className="text-white/50 hover:text-white transition-colors">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-white/5 h-1">
          <div 
            className="bg-blue-500 h-1 transition-all duration-500 ease-out" 
            style={{ width: `${((currentStepIndex + 1) / STEPS.length) * 100}%` }}
          />
        </div>

        {/* Content Body */}
        <div className="p-8 min-h-[400px] flex flex-col relative">
          
          {step === 'Overview' && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-300">
              <h3 className="text-2xl text-white font-medium mb-4">You are about to install {appName}</h3>
              <p className="text-white/60 mb-6 leading-relaxed">
                This integration will connect to your core Revenue OS. It requires specific capabilities to operate.
                Please follow the wizard to securely authorize and configure this application within your workspace.
              </p>
              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-200">
                <strong>Note:</strong> You must be a Workspace Administrator to complete this installation.
              </div>
            </div>
          )}

          {step === 'Permissions' && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-300">
              <h3 className="text-xl text-white font-medium mb-4">Required Permissions</h3>
              <p className="text-white/60 mb-4">This application is requesting the following granular access to your workspace data:</p>
              
              <div className="space-y-3">
                {['read:companies', 'write:companies', 'read:opportunities', 'execute:ai'].map((perm) => (
                  <div key={perm} className="flex items-start gap-3 p-3 rounded-lg bg-white/5 border border-white/5">
                    <div className="mt-0.5 text-green-400">
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-white font-medium font-mono text-sm">{perm}</p>
                      <p className="text-white/50 text-xs mt-1">Allows the application to {perm.split(':')[0]} {perm.split(':')[1]} data.</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {step === 'Dependencies' && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-300">
              <h3 className="text-xl text-white font-medium mb-4">System Dependencies</h3>
              <p className="text-white/60 mb-6">Validation check across the Enterprise Intelligence Cloud:</p>
              
              <ul className="space-y-4">
                <li className="flex items-center justify-between p-4 bg-green-500/5 border border-green-500/20 rounded-xl">
                  <span className="text-white/80">Identity Resolution Engine</span>
                  <span className="text-green-400 font-medium text-sm flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Active
                  </span>
                </li>
                <li className="flex items-center justify-between p-4 bg-green-500/5 border border-green-500/20 rounded-xl">
                  <span className="text-white/80">Enterprise Integration Hub v2</span>
                  <span className="text-green-400 font-medium text-sm flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Compatible
                  </span>
                </li>
              </ul>
            </div>
          )}

          {step === 'Configuration' && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-300">
              <h3 className="text-xl text-white font-medium mb-4">App Configuration</h3>
              <p className="text-white/60 mb-6">Configure runtime settings for {appName}:</p>
              
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-2">Sync Frequency</label>
                  <select className="w-full bg-black/40 border border-white/10 rounded-lg py-2.5 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none">
                    <option>Real-time (Webhooks)</option>
                    <option>Every 15 Minutes</option>
                    <option>Hourly</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-2 flex items-center gap-2">
                    Enable AI Auto-Resolution
                    <span className="bg-purple-500/20 text-purple-300 text-[10px] px-2 py-0.5 rounded uppercase font-bold tracking-wider">Beta</span>
                  </label>
                  <div className="flex items-center gap-3">
                    <input type="checkbox" className="w-5 h-5 rounded border-white/20 bg-black/40 text-blue-500 focus:ring-blue-500 focus:ring-offset-black" />
                    <span className="text-white/50 text-sm">Automatically resolve identity conflicts using the Context Engine.</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {step === 'Confirmation' && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-300 h-full flex flex-col justify-center items-center text-center">
              <div className="w-20 h-20 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-6">
                <svg className="w-10 h-10 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-2xl text-white font-medium mb-2">Ready to Install</h3>
              <p className="text-white/60 mb-2 max-w-md">By clicking authorize, {appName} will be installed to your workspace and immediately begin operating based on your configuration.</p>
            </div>
          )}

          {step === 'Progress' && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 h-full flex flex-col justify-center items-center text-center">
              <div className="relative w-24 h-24 mb-6">
                <div className="absolute inset-0 border-4 border-white/10 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
              </div>
              <h3 className="text-xl text-white font-medium mb-2">Installing App...</h3>
              <p className="text-white/50 text-sm font-mono animate-pulse">Running capabilities check, propagating permissions...</p>
            </div>
          )}

          {step === 'Completed' && (
            <div className="animate-in zoom-in-90 duration-500 h-full flex flex-col justify-center items-center text-center">
              {/* Confetti simulation wrapper */}
              <div className="w-24 h-24 rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center mb-6 relative group">
                <div className="absolute inset-0 bg-green-400 blur-xl opacity-20 group-hover:opacity-40 transition-opacity"></div>
                <svg className="w-12 h-12 text-green-400 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-3xl text-white font-bold mb-3">Installation Complete!</h3>
              <p className="text-white/60 mb-6">{appName} is now successfully integrated into your workspace.</p>
              
              <button 
                onClick={() => onComplete(installId!)}
                className="px-8 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium transition-colors border border-white/10"
              >
                Go to Dashboard
              </button>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        {step !== 'Progress' && step !== 'Completed' && (
          <div className="px-8 py-5 border-t border-white/10 bg-black/40 flex items-center justify-between">
            <button
              onClick={handleBack}
              disabled={currentStepIndex === 0}
              className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                currentStepIndex === 0 
                  ? 'text-white/20 cursor-not-allowed' 
                  : 'text-white/70 hover:bg-white/10 hover:text-white border border-transparent hover:border-white/10'
              }`}
            >
              Back
            </button>

            <button
              onClick={handleNext}
              className="px-6 py-2.5 rounded-lg text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white transition-colors shadow-lg shadow-blue-500/20"
            >
              {step === 'Confirmation' ? 'Authorize & Install' : 'Continue'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
