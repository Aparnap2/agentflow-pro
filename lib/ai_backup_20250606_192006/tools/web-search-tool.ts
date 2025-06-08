import { z } from 'zod';
import { BaseTool, ToolResult } from './base-tool';
import axios from 'axios';
import { log } from '../utils/logger';
import { toolRegistry } from './tool-registry';

interface WebSearchResult {
  title: string;
  link: string;
  snippet: string;
  source: string;
}

interface WebSearchOptions {
  query: string;
  limit?: number;
  region?: string;
  safeSearch?: boolean;
}

export class WebSearchTool extends BaseTool<WebSearchOptions, WebSearchResult[]> {
  private readonly DEFAULT_LIMIT = 5;
  private readonly API_BASE_URL = 'https://www.googleapis.com/customsearch/v1';
  private readonly API_KEY_ENV_VAR = 'GOOGLE_CSE_API_KEY';
  private readonly CX_ENV_VAR = 'GOOGLE_CSE_CX';

  constructor() {
    super({
      name: 'web_search',
      description: 'Search the web for information',
      schema: z.object({
        query: z.string().min(1, 'Search query is required'),
        limit: z.number().int().min(1).max(10).optional(),
        region: z.string().optional(),
        safeSearch: z.boolean().optional(),
      }),
      requiresApiKey: true,
      apiKeyEnvVar: 'GOOGLE_CSE_API_KEY',
      rateLimit: {
        maxRequests: 100,
        timeWindow: 60 * 60 * 1000, // 1 hour
      },
    });
  }

  protected async _execute(options: WebSearchOptions): Promise<WebSearchResult[]> {
    this.checkApiKey();
    
    const apiKey = process.env[this.API_KEY_ENV_VAR];
    const cx = process.env[this.CX_ENV_VAR];
    
    if (!apiKey) {
      throw new Error(`API key not found. Please set ${this.API_KEY_ENV_VAR} in your environment variables.`);
    }
    
    if (!cx) {
      throw new Error(`Custom Search Engine ID not found. Please set ${this.CX_ENV_VAR} in your environment variables.`);
    }

    const params = {
      key: apiKey,
      cx,
      q: options.query,
      num: options.limit || this.DEFAULT_LIMIT,
      ...(options.region && { gl: options.region }),
      ...(options.safeSearch !== undefined && { safe: options.safeSearch ? 'active' : 'off' }),
    };

    try {
      const response = await axios.get(this.API_BASE_URL, { params });
      
      if (!response.data.items) {
        log.warn('No search results found', { query: options.query });
        return [];
      }

      return response.data.items.map((item: any) => ({
        title: item.title,
        link: item.link,
        snippet: item.snippet,
        source: this.extractSourceDomain(item.link),
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      log.error('Web search failed', { error: errorMessage, query: options.query });
      throw new Error(`Web search failed: ${errorMessage}`);
    }
  }

  private extractSourceDomain(url: string): string {
    try {
      const domain = new URL(url).hostname.replace('www.', '');
      return domain.split('.')[0];
    } catch (error) {
      log.warn('Failed to extract domain from URL', { url });
      return 'unknown';
    }
  }
}

// Register the tool by default
toolRegistry.register(new WebSearchTool());
