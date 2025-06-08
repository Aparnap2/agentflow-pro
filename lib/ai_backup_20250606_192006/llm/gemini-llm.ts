import { log } from '../utils/logger';
import { BaseLLM, LLMResponse, LLMOptions } from './base-llm';
import { GoogleGenerativeAI, GenerativeModel } from '@google/generative-ai';

interface GeminiModelConfig {
  model: string;
  maxOutputTokens: number;
  temperature: number;
  topP: number;
  topK: number;
}

export class GeminiLLM extends BaseLLM {
  private client: GoogleGenerativeAI;
  private modelInstance: GenerativeModel;
  private static readonly SUPPORTED_MODELS: Record<string, GeminiModelConfig> = {
    'gemini-pro': {
      model: 'gemini-pro',
      maxOutputTokens: 2048,
      temperature: 0.7,
      topP: 1,
      topK: 40,
    },
    'gemini-1.5-pro': {
      model: 'gemini-1.5-pro',
      maxOutputTokens: 8192,
      temperature: 0.7,
      topP: 1,
      topK: 40,
    },
  };

  constructor(apiKey: string, options: LLMOptions) {
    super(options);
    this.validateModel(this.model);
    this.client = new GoogleGenerativeAI(apiKey);
    this.modelInstance = this.client.getGenerativeModel({
      model: this.options.model,
      generationConfig: {
        temperature: this.options.temperature,
        topP: this.options.topP,
        topK: 40,
        maxOutputTokens: this.options.maxTokens,
      },
    });
  }

  protected initializeTokenCosts() {
    // Costs per 1M tokens (input/output)
    return {
      'gemini-pro': { input: 0.25, output: 0.5 },
      'gemini-1.5-pro': { input: 3.5, output: 10.5 },
      default: { input: 1, output: 3 },
    };
  }

  public async generate(prompt: string, options: Partial<LLMOptions> = {}): Promise<LLMResponse> {
    const mergedOptions = { ...this.options, ...options };
    const modelConfig = GeminiLLM.SUPPORTED_MODELS[mergedOptions.model] || GeminiLLM.SUPPORTED_MODELS['gemini-pro'];
    
    try {
      const result = await this.modelInstance.generateContent({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: mergedOptions.temperature,
          topP: mergedOptions.topP,
          maxOutputTokens: mergedOptions.maxTokens || modelConfig.maxOutputTokens,
        },
      });

      const response = result.response;
      const text = response.text();
      
      // Estimate token usage (Gemini doesn't provide token counts in the response)
      const promptTokens = Math.ceil(prompt.length / 4); // Rough estimate
      const completionTokens = Math.ceil(text.length / 4); // Rough estimate
      const totalTokens = promptTokens + completionTokens;
      
      const cost = this.calculateCost(promptTokens, completionTokens, this.model);
      
      this.logUsage(this.model, promptTokens, completionTokens, totalTokens, cost);

      return {
        content: text,
        metadata: {
          model: this.model,
          tokens: {
            prompt: promptTokens,
            completion: completionTokens,
            total: totalTokens,
          },
          cost,
        },
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      log.error('Gemini API Error', { error: errorMessage, model: this.model });
      throw new Error(`Gemini API Error: ${errorMessage}`);
    }
  }

  public static getSupportedModels(): string[] {
    return Object.keys(GeminiLLM.SUPPORTED_MODELS);
  }
}
