import { CrewConfig, CrewResponse, AgentResponse } from './types';
import { BaseAgent } from './base-agent';

export class Crew {
  private id: string;
  private name: string;
  private description: string;
  private agents: Map<string, BaseAgent>;
  private tasks: any[];
  private verbose: boolean;
  private process: 'sequential' | 'hierarchical' | 'collaborative';

  constructor(config: CrewConfig) {
    this.id = config.id;
    this.name = config.name;
    this.description = config.description || '';
    this.verbose = config.verbose || false;
    this.process = config.process || 'sequential';
    this.agents = new Map();
    this.tasks = [];
  }

  // Add an agent to the crew
  public addAgent(agent: BaseAgent): void {
    this.agents.set(agent.getId(), agent);
    if (this.verbose) {
      console.log(`Added agent: ${agent.getName()} (${agent.getId()})`);
    }
  }

  // Add a task to the crew
  public addTask(task: any): void {
    this.tasks.push(task);
    if (this.verbose) {
      console.log(`Added task: ${task.description}`);
    }
  }

  // Initialize all agents in the crew
  public async initialize(): Promise<void> {
    if (this.verbose) {
      console.log(`Initializing crew: ${this.name}`);
    }
    
    for (const agent of this.agents.values()) {
      await agent.initialize();
    }
  }

  // Execute tasks based on the selected process
  public async execute(): Promise<CrewResponse> {
    const startTime = Date.now();
    const results: Record<string, any> = {};
    const errors: Record<string, string> = {};
    
    try {
      if (this.verbose) {
        console.log(`Starting execution with process: ${this.process}`);
      }

      switch (this.process) {
        case 'sequential':
          await this.executeSequentially(results, errors);
          break;
        case 'hierarchical':
          await this.executeHierarchically(results, errors);
          break;
        case 'collaborative':
          await this.executeCollaboratively(results, errors);
          break;
        default:
          throw new Error(`Unsupported process type: ${this.process}`);
      }

      return {
        success: Object.keys(errors).length === 0,
        results,
        errors,
        metadata: {
          executionTime: Date.now() - startTime,
          tokensUsed: 0, // Will be updated with actual token usage
          cost: 0, // Will be calculated based on token usage
        },
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Crew execution failed:', error);
      return {
        success: false,
        results: {},
        errors: { 'crew-execution': errorMessage },
        metadata: {
          executionTime: Date.now() - startTime,
          tokensUsed: 0,
          cost: 0,
        },
      };
    }
  }

  // Clean up all resources
  public async cleanup(): Promise<void> {
    if (this.verbose) {
      console.log('Cleaning up crew resources...');
    }
    
    for (const agent of this.agents.values()) {
      await agent.cleanup();
    }
  }

  // Execute tasks sequentially
  private async executeSequentially(
    results: Record<string, any>,
    errors: Record<string, string>
  ): Promise<void> {
    for (const task of this.tasks) {
      const agent = this.agents.get(task.agentId);
      if (!agent) {
        errors[task.id] = `Agent not found: ${task.agentId}`;
        continue;
      }

      try {
        const result = await agent.processTask(task.description, task.context || {});
        results[task.id] = result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        errors[task.id] = errorMessage;
      }
    }
  }

  // Execute tasks hierarchically (to be implemented)
  private async executeHierarchically(
    results: Record<string, any>,
    errors: Record<string, string>
  ): Promise<void> {
    // Implementation for hierarchical execution
    throw new Error('Hierarchical execution not yet implemented');
  }

  // Execute tasks collaboratively (to be implemented)
  private async executeCollaboratively(
    results: Record<string, any>,
    errors: Record<string, string>
  ): Promise<void> {
    // Implementation for collaborative execution
    throw new Error('Collaborative execution not yet implemented');
  }

  // Getters
  public getId(): string { return this.id; }
  public getName(): string { return this.name; }
  public getDescription(): string { return this.description; }
  public getAgentCount(): number { return this.agents.size; }
  public getTaskCount(): number { return this.tasks.length; }
  public getProcessType(): string { return this.process; }
}
