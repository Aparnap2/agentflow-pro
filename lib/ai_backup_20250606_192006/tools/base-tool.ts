import { z } from 'zod';
import { log } from '../utils/logger';

export type ToolResult<T = any> = {
  success: boolean;
  data?: T;
  error?: string;
  metadata?: Record<string, any>;
};

export interface ToolConfig {
  name: string;
  description: string;
  schema: z.ZodSchema<any>;
  requiresApiKey?: boolean;
  apiKeyEnvVar?: string;
  rateLimit?: {
    maxRequests: number;
    timeWindow: number; // in milliseconds
  };
}

export abstract class BaseTool<TInput = any, TOutput = any> {
  protected config: ToolConfig;
  private requestCount: number = 0;
  private lastResetTime: number = Date.now();

  constructor(config: ToolConfig) {
    this.config = {
      requiresApiKey: false,
      ...config,
    };
  }

  public getName(): string {
    return this.config.name;
  }

  public getDescription(): string {
    return this.config.description;
  }

  public getSchema(): z.ZodSchema<any> {
    return this.config.schema;
  }

  public async execute(input: TInput): Promise<ToolResult<TOutput>> {
    try {
      // Check rate limiting
      if (this.config.rateLimit) {
        await this.checkRateLimit();
      }

      // Validate input
      const validationResult = await this.validateInput(input);
      if (!validationResult.success) {
        return {
          success: false,
          error: `Input validation failed: ${validationResult.error}`,
        };
      }

      // Execute the tool
      const result = await this._execute(validationResult.data);
      return {
        success: true,
        data: result,
        metadata: {
          timestamp: new Date().toISOString(),
          tool: this.config.name,
        },
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      log.error(`Tool execution failed: ${this.config.name}`, { error: errorMessage });
      return {
        success: false,
        error: errorMessage,
        metadata: {
          timestamp: new Date().toISOString(),
          tool: this.config.name,
        },
      };
    } finally {
      this.requestCount++;
    }
  }

  protected abstract _execute(input: TInput): Promise<TOutput>;

  private async validateInput(input: TInput): Promise<{ success: boolean; data?: any; error?: string }> {
    try {
      const validated = await this.config.schema.parseAsync(input);
      return { success: true, data: validated };
    } catch (error) {
      if (error instanceof z.ZodError) {
        return {
          success: false,
          error: error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', '),
        };
      }
      return { success: false, error: 'Unknown validation error' };
    }
  }

  private async checkRateLimit(): Promise<void> {
    if (!this.config.rateLimit) return;

    const now = Date.now();
    const timeElapsed = now - this.lastResetTime;

    // Reset counter if time window has passed
    if (timeElapsed > this.config.rateLimit.timeWindow) {
      this.requestCount = 0;
      this.lastResetTime = now;
      return;
    }

    // Check if rate limit exceeded
    if (this.requestCount >= this.config.rateLimit.maxRequests) {
      const timeToWait = this.config.rateLimit.timeWindow - timeElapsed;
      throw new Error(
        `Rate limit exceeded. Please wait ${Math.ceil(timeToWait / 1000)} seconds before trying again.`
      );
    }
  }

  // Helper method to check if API key is available
  protected checkApiKey(): void {
    if (this.config.requiresApiKey && this.config.apiKeyEnvVar) {
      const apiKey = process.env[this.config.apiKeyEnvVar];
      if (!apiKey) {
        throw new Error(
          `API key is required for ${this.config.name}. Please set ${this.config.apiKeyEnvVar} in your environment variables.`
        );
      }
    }
  }
}
