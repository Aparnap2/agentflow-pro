import { BaseAgent } from '../base-agent';
import { LLMFactory } from '../llm/llm-factory';
import { toolRegistry } from '../tools/tool-registry';
import { log } from '../utils/logger';
import { AgentConfig } from '../types';

interface AgentMemory {
  [key: string]: any;
}

export class BaseAgentImpl extends BaseAgent {
  protected memory: AgentMemory = {};
  // llm is declared in BaseAgent
  declare protected llm: any; // Will be typed properly when LLM is implemented
  protected tools: string[] = [];

  constructor(config: any) {
    super(config);
    this.initializeLLM();
  }

  private initializeLLM(): void {
    // TODO: Initialize LLM based on configuration
    // this.llm = LLMFactory.getInstance().createLLM({
    //   provider: 'gemini',
    //   apiKey: process.env.GEMINI_API_KEY || '',
    //   model: 'gemini-pro',
    // });
  }


  public async processTask(task: string, context: Record<string, any> = {}): Promise<any> {
    try {
      // 1. Parse and understand the task
      const taskAnalysis = await this.analyzeTask(task, context);
      
      // 2. Plan the approach
      const plan = await this.createPlan(taskAnalysis);
      
      // 3. Execute the plan
      const result = await this.executePlan(plan, context);
      
      // 4. Format the response
      return this.formatResponse(result);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      log.error(`Task processing failed: ${errorMessage}`, { task, error });
      throw new Error(`Failed to process task: ${errorMessage}`);
    }
  }

  protected async analyzeTask(task: string, context: Record<string, any>): Promise<any> {
    // TODO: Implement task analysis using LLM
    return { task, context };
  }

  protected async createPlan(taskAnalysis: any): Promise<any[]> {
    // TODO: Implement planning logic
    return [];
  }

  protected async executePlan(plan: any[], context: Record<string, any>): Promise<any> {
    const results: any[] = [];
    
    for (const step of plan) {
      try {
        const result = await this.executeStep(step, context);
        results.push(result);
      } catch (error) {
        log.error(`Step execution failed: ${step}`, { error });
        throw error;
      }
    }
    
    return results;
  }

  protected async executeStep(step: any, context: Record<string, any>): Promise<any> {
    // Check if this is a tool execution step
    if (step.type === 'tool') {
      const tool = toolRegistry.getTool(step.tool);
      if (!tool) {
        throw new Error(`Tool not found: ${step.tool}`);
      }
      return tool.execute(step.params);
    }
    
    // Default implementation for other step types
    return step;
  }

  protected formatResponse(result: any): any {
    // Default implementation - can be overridden by subclasses
    return {
      success: true,
      data: result,
      timestamp: new Date().toISOString(),
      agent: this.name,
    };
  }

  // Memory management
  public remember(key: string, value: any): void {
    this.memory[key] = value;
  }

  public recall<T = any>(key: string): T | undefined {
    return this.memory[key] as T;
  }

  public forget(key: string): boolean {
    if (key in this.memory) {
      delete this.memory[key];
      return true;
    }
    return false;
  }

  // Tool management
  public addTool(toolName: string): void {
    if (!this.tools.includes(toolName)) {
      this.tools.push(toolName);
    }
  }

  public getTools(): string[] {
    return [...this.tools];
  }

  public hasTool(toolName: string): boolean {
    return this.tools.includes(toolName);
  }

  // Cleanup resources
  public async cleanup(): Promise<void> {
    await super.cleanup();
    // Clean up any resources used by this agent
    this.memory = {};
    this.tools = [];
  }
}
