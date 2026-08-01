import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layout/DashboardLayout';
import AuthGuard from './components/AuthGuard';
import ErrorBoundary from './components/ErrorBoundary';

// Dynamic Module Imports
import AdminCenter from './modules/administration/pages/AdminCenter';
import AIGovernanceCenter from './modules/ai_governance/pages/AIGovernanceCenter';
import BillingCenter from './modules/billing/pages/BillingCenter';
import ComplianceCenter from './modules/compliance_cloud/pages/ComplianceCenter';
import FeatureStoreCenter from './modules/feature_store/pages/FeatureStoreCenter';
import FoundationModelsCenter from './modules/foundation_models/pages/FoundationModelsCenter';
import PromptEditor from './modules/prompt_studio/pages/PromptEditor';
import AgentCanvas from './modules/agent_builder/pages/AgentCanvas';
import DevPortalHome from './modules/public_api/pages/DevPortalHome';
import RevenueOS from './modules/revenue_os/pages/RevenueOS';

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard/revenue-os" replace />} />
          
          <Route path="/dashboard" element={<AuthGuard><DashboardLayout /></AuthGuard>}>
            <Route path="revenue-os" element={<RevenueOS />} />
            <Route path="admin" element={<AdminCenter />} />
            <Route path="ai-governance" element={<AIGovernanceCenter />} />
            <Route path="billing" element={<BillingCenter />} />
            <Route path="compliance" element={<ComplianceCenter />} />
            <Route path="feature-store" element={<FeatureStoreCenter />} />
            <Route path="foundation-models" element={<FoundationModelsCenter />} />
            <Route path="prompt-studio" element={<PromptEditor />} />
            <Route path="agents" element={<AgentCanvas />} />
            <Route path="developer-portal" element={<DevPortalHome />} />
          </Route>

          <Route path="*" element={<div className="flex h-screen items-center justify-center">404 - Not Found</div>} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
