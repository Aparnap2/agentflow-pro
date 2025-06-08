import { useState, useCallback } from 'react';
import { AgentResponse } from '@/lib/ai/types';

export function useAgent() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const executeTask = useCallback(async (
    agentType: string, 
    task: string, 
    context: Record<string, any> = {}
  ): Promise<AgentResponse> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agentType, task, context }),
      });

      if (!response.ok) {
        throw new Error(`Agent request failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('An unknown error occurred');
      setError(error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { executeTask, isLoading, error };
}
