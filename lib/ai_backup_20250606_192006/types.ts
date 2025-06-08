export interface AgentConfig {
  id: string;
  name: string;
  role: string;
  goal: string;
  backstory?: string;
  verbose?: boolean;
  allowDelegation?: boolean;
  tools?: any[];
  llm?: any;
}

export interface TaskConfig {
  id: string;
  description: string;
  expectedOutput: string;
  agentId: string;
  context?: string[];
  asyncExecution?: boolean;
}

export interface CrewConfig {
  id: string;
  name: string;
  description?: string;
  agents: AgentConfig[];
  tasks: TaskConfig[];
  verbose?: boolean;
  process?: 'sequential' | 'hierarchical' | 'collaborative';
}

export interface AgentResponse {
  success: boolean;
  output?: any;
  error?: string;
  metadata?: Record<string, any>;
}

export interface CrewResponse {
  success: boolean;
  results: Record<string, any>;
  errors: Record<string, string>;
  metadata: {
    executionTime: number;
    tokensUsed: number;
    cost: number;
  };
}
