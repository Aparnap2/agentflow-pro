import { AgentConfig } from './types';
import { BaseAgent } from './base-agent';

// Import agent implementations as they are created
// import { SupportAgent } from './agents/support-agent';
// import { SalesAgent } from './agents/sales-agent';
// import { ContentAgent } from './agents/content-agent';

type AgentType = 'support' | 'sales' | 'content' | 'analyst' | 'general';

export class AgentFactory {
  private static instance: AgentFactory;
  private agentRegistry: Map<AgentType, new (config: AgentConfig) => BaseAgent>;

  private constructor() {
    this.agentRegistry = new Map();
    this.initializeDefaultAgents();
  }

  public static getInstance(): AgentFactory {
    if (!AgentFactory.instance) {
      AgentFactory.instance = new AgentFactory();
    }
    return AgentFactory.instance;
  }

  private initializeDefaultAgents(): void {
    // Register default agent implementations
    // this.registerAgent('support', SupportAgent);
    // this.registerAgent('sales', SalesAgent);
    // this.registerAgent('content', ContentAgent);
  }

  public registerAgent(type: AgentType, agentClass: new (config: AgentConfig) => BaseAgent): void {
    if (this.agentRegistry.has(type)) {
      console.warn(`Agent type '${type}' is already registered and will be overwritten`);
    }
    this.agentRegistry.set(type, agentClass);
  }

  public createAgent(type: AgentType, config: AgentConfig): BaseAgent {
    const AgentClass = this.agentRegistry.get(type);
    
    if (!AgentClass) {
      throw new Error(`No agent registered for type: ${type}`);
    }

    try {
      return new AgentClass({
        ...config,
        id: config.id || `agent-${Date.now()}`,
        verbose: config.verbose ?? false,
      });
    } catch (error) {
      console.error(`Failed to create agent of type ${type}:`, error);
      throw new Error(`Agent creation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  public listRegisteredAgents(): AgentType[] {
    return Array.from(this.agentRegistry.keys());
  }

  public async createAgentFromConfig(config: AgentConfig & { type: AgentType }): Promise<BaseAgent> {
    const agent = this.createAgent(config.type, config);
    await agent.initialize();
    return agent;
  }

  // Helper method to create a basic agent configuration
  public static createBasicConfig(
    type: AgentType,
    name: string,
    role: string,
    goal: string,
    overrides: Partial<AgentConfig> = {}
  ): AgentConfig & { type: AgentType } {
    return {
      type,
      id: overrides.id || `${type}-${Date.now()}`,
      name,
      role,
      goal,
      backstory: overrides.backstory || `A ${role} agent that ${goal.toLowerCase()}`,
      verbose: overrides.verbose || false,
      allowDelegation: overrides.allowDelegation || false,
      tools: overrides.tools || [],
      llm: overrides.llm,
    };
  }
}
