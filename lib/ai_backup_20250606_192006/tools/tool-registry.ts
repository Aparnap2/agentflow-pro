import { BaseTool } from './base-tool';
import { log } from '../utils/logger';

type ToolMap = Map<string, BaseTool>;

export class ToolRegistry {
  private static instance: ToolRegistry;
  private tools: ToolMap = new Map();

  private constructor() {}

  public static getInstance(): ToolRegistry {
    if (!ToolRegistry.instance) {
      ToolRegistry.instance = new ToolRegistry();
    }
    return ToolRegistry.instance;
  }

  public register(tool: BaseTool): void {
    const toolName = tool.getName();
    
    if (this.tools.has(toolName)) {
      log.warn(`Tool with name '${toolName}' is already registered and will be overwritten`);
    }
    
    this.tools.set(toolName, tool);
    log.info(`Registered tool: ${toolName}`);
  }

  public registerMultiple(tools: BaseTool[]): void {
    tools.forEach(tool => this.register(tool));
  }

  public getTool(name: string): BaseTool | undefined {
    return this.tools.get(name);
  }

  public getTools(): ToolMap {
    return new Map(this.tools);
  }

  public listTools(): string[] {
    return Array.from(this.tools.keys());
  }

  public removeTool(name: string): boolean {
    const deleted = this.tools.delete(name);
    if (deleted) {
      log.info(`Removed tool: ${name}`);
    } else {
      log.warn(`Attempted to remove non-existent tool: ${name}`);
    }
    return deleted;
  }

  public clear(): void {
    const count = this.tools.size;
    this.tools.clear();
    log.info(`Cleared all ${count} tools from registry`);
  }

  public async executeTool(
    toolName: string, 
    input: Record<string, any>
  ): Promise<ReturnType<BaseTool['execute']>> {
    const tool = this.getTool(toolName);
    
    if (!tool) {
      return {
        success: false,
        error: `Tool '${toolName}' not found`,
      };
    }

    try {
      return await tool.execute(input);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      log.error(`Error executing tool '${toolName}':`, { error: errorMessage });
      return {
        success: false,
        error: `Failed to execute tool: ${errorMessage}`,
      };
    }
  }
}

// Singleton instance
export const toolRegistry = ToolRegistry.getInstance();

// Helper function to register tools
export function registerTools(tools: BaseTool[]): void {
  toolRegistry.registerMultiple(tools);
}

// Helper function to get a tool
export function getTool(name: string): BaseTool | undefined {
  return toolRegistry.getTool(name);
}

// Helper function to execute a tool
export async function executeTool(
  toolName: string, 
  input: Record<string, any>
): Promise<ReturnType<BaseTool['execute']>> {
  return toolRegistry.executeTool(toolName, input);
}
