import { AgentFactory } from './agent-factory';
import { toolRegistry } from './tools/tool-registry';
import { SupportAgent } from './agents/support-agent';
// Import other agents as they are created
// import { SalesAgent } from './agents/sales-agent';
// import { ContentAgent } from './agents/content-agent';

// Initialize the agent factory with supported agents
export function initializeAgents() {
  const agentFactory = AgentFactory.getInstance();
  
  // Register agent types
  agentFactory.registerAgent('support', SupportAgent);
  // agentFactory.registerAgent('sales', SalesAgent);
  // agentFactory.registerAgent('content', ContentAgent);
  
  console.log('AI Agents initialized with types:', agentFactory.listRegisteredAgents());
}

// Initialize tools
export function initializeTools() {
  // Tools are auto-registered when imported
  // Import tools here to ensure they're registered
  import('./tools/web-search-tool');
  
  console.log('AI Tools initialized:', toolRegistry.listTools());
}

// Initialize everything
export function initializeAI() {
  initializeTools();
  initializeAgents();
  
  console.log('AI system initialized successfully');
}

// Run initialization if this module is imported directly
if (require.main === module) {
  initializeAI();
}
