// Core routing
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// Layout
import Layout from './components/Layout';
// Page components
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import AgentStudio from './pages/AgentStudio';
import Analytics from './pages/Analytics';
import Integrations from './pages/Integrations';
import Monitoring from './pages/Monitoring';
import AgentFactory from './pages/AgentFactory';
import WorkflowOrchestrator from './pages/WorkflowOrchestrator';
import AdminPanel from './pages/AdminPanel';
import Billing from './pages/Billing';
import MemoryHub from './pages/MemoryHub';

/**
 * Main application component with routing configuration
 */
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
        <Route path="/agents" element={<Layout><AgentStudio /></Layout>} />
        <Route path="/factory" element={<Layout><AgentFactory /></Layout>} />
        <Route 
          path="/orchestrator" 
          element={
            <Layout>
              <WorkflowOrchestrator />
            </Layout>
          } 
        />
        <Route path="/analytics" element={<Layout><Analytics /></Layout>} />
        <Route path="/monitoring" element={<Layout><Monitoring /></Layout>} />
        <Route path="/integrations" element={<Layout><Integrations /></Layout>} />
        <Route path="/admin" element={<Layout><AdminPanel /></Layout>} />
        <Route path="/billing" element={<Layout><Billing /></Layout>} />
        <Route path="/memory" element={<Layout><MemoryHub /></Layout>} />
      </Routes>
    </Router>
  );
}

export default App;