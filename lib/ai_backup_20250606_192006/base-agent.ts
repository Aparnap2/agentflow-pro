import { AgentConfig, AgentResponse } from './types';

export abstract class BaseAgent {
  protected id: string;
  protected name: string;
  protected role: string;
  protected goal: string;
  protected backstory: string;
  protected verbose: boolean;
  protected allowDelegation: boolean;
  protected tools: any[];
  protected llm: any;

  constructor(config: AgentConfig) {
    this.id = config.id;
    this.name = config.name;
    this.role = config.role;
    this.goal = config.goal;
    this.backstory = config.backstory || '';
    this.verbose = config.verbose || false;
    this.allowDelegation = config.allowDelegation || false;
    this.tools = config.tools || [];
    this.llm = config.llm;
  }

  // Initialize the agent with required resources
  async initialize(): Promise<void> {
    if (this.verbose) {
      console.log(`Initializing agent: ${this.name} (${this.role})`);
    }
    // Initialize tools and other resources here
  }

  // Process a task and return the result
  abstract processTask(task: string, context?: Record<string, any>): Promise<AgentResponse>;

  // Clean up resources when the agent is no longer needed
  async cleanup(): Promise<void> {
    if (this.verbose) {
      console.log(`Cleaning up agent: ${this.name}`);
    }
    // Clean up resources here
  }

  // Helper method to log messages
  protected log(message: string, data?: any): void {
    if (!this.verbose) return;
    
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      agent: this.name,
      message,
      ...(data && { data })
    };
    
    console.log(JSON.stringify(logEntry, null, 2));
  }

  // Getters
  public getId(): string { return this.id; }
  public getName(): string { return this.name; }
  public getRole(): string { return this.role; }
  public getGoal(): string { return this.goal; }
  public getBackstory(): string { return this.backstory; }
  public isVerbose(): boolean { return this.verbose; }
  public canDelegate(): boolean { return this.allowDelegation; }
}
