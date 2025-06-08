import { log } from '../utils/logger';

export interface LLMResponse {
  content: string;
  metadata: {
    model: string;
    tokens: {
      prompt: number;
      completion: number;
      total: number;
    };
    cost: number;
  };
}

export interface LLMOptions {
  model: string;
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  stopSequences?: string[];
}

export abstract class BaseLLM {
  protected options: LLMOptions;
  protected model: string;
  protected tokenCosts: Record<string, { input: number; output: number }>;

  constructor(options: LLMOptions) {
    this.options = {
      temperature: 0.7,
      maxTokens: 1000,
      topP: 1,
      frequencyPenalty: 0,
      presencePenalty: 0,
      ...options,
    };
    this.model = options.model;
    this.tokenCosts = this.initializeTokenCosts();
  }

  public abstract generate(prompt: string, options?: Partial<LLMOptions>): Promise<LLMResponse>;

  protected calculateCost(inputTokens: number, outputTokens: number, model: string): number {
    const costs = this.tokenCosts[model] || this.tokenCosts.default;
    return (inputTokens * costs.input + outputTokens * costs.output) / 1_000_000; // Convert to cost per million tokens
  }

  protected abstract initializeTokenCosts(): Record<string, { input: number; output: number }>;

  protected logUsage(
    model: string,
    promptTokens: number,
    completionTokens: number,
    totalTokens: number,
    cost: number
  ): void {
    log.debug('LLM Usage', {
      model,
      promptTokens,
      completionTokens,
      totalTokens,
      cost: `$${cost.toFixed(6)}`,
    });
  }

  protected validateModel(model: string): void {
    if (!Object.keys(this.tokenCosts).includes(model) && model !== 'default') {
      log.warn(`Model ${model} not found in token costs, using default rates`);
    }
  }
}
