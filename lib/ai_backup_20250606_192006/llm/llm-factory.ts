import { BaseLLM, LLMOptions, LLMResponse } from './base-llm';
import { GeminiLLM } from './gemini-llm';
import { log } from '../utils/logger';

export type LLMProvider = 'gemini' | 'openai' | 'anthropic' | 'openrouter';

export interface LLMConfig extends LLMOptions {
  provider: LLMProvider;
  apiKey: string;
  baseUrl?: string;
  headers?: Record<string, string>;
}

export class LLMFactory {
  private static instance: LLMFactory;
  private llmInstances: Map<string, BaseLLM> = new Map();

  private constructor() {}

  public static getInstance(): LLMFactory {
    if (!LLMFactory.instance) {
      LLMFactory.instance = new LLMFactory();
    }
    return LLMFactory.instance;
  }

  public createLLM(config: LLMConfig): BaseLLM {
    const cacheKey = this.getCacheKey(config);
    
    // Return cached instance if available
    if (this.llmInstances.has(cacheKey)) {
      return this.llmInstances.get(cacheKey)!;
    }

    // Create new instance based on provider
    let llmInstance: BaseLLM;
    
    switch (config.provider.toLowerCase()) {
      case 'gemini':
        llmInstance = new GeminiLLM(config.apiKey, config);
        break;
      
      case 'openrouter':
        // Fall through to default for now
      
      case 'openai':
        // Fall through to default for now
      
      case 'anthropic':
        // Fall through to default for now
      
      default:
        throw new Error(`Unsupported LLM provider: ${config.provider}`);
    }

    // Cache the instance
    this.llmInstances.set(cacheKey, llmInstance);
    return llmInstance;
  }

  public async generate(
    config: LLMConfig,
    prompt: string,
    options: Partial<LLMOptions> = {}
  ): Promise<LLMResponse> {
    const llm = this.createLLM(config);
    return llm.generate(prompt, options);
  }

  public clearCache(): void {
    this.llmInstances.clear();
    log.info('Cleared all LLM instances from cache');
  }

  public getCachedInstances(): Map<string, BaseLLM> {
    return new Map(this.llmInstances);
  }

  private getCacheKey(config: LLMConfig): string {
    return `${config.provider}:${config.model}:${JSON.stringify(config)}`;
  }
}

// Singleton instance
export const llmFactory = LLMFactory.getInstance();

// Helper function for quick LLM generation
export async function generateText(
  provider: LLMProvider,
  apiKey: string,
  model: string,
  prompt: string,
  options: Partial<LLMOptions> = {}
): Promise<LLMResponse> {
  return llmFactory.generate(
    {
      provider,
      apiKey,
      model,
      ...options,
    },
    prompt,
    options
  );
}
