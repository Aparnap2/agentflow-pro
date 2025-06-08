import { useState, useCallback, useEffect, useRef } from 'react';
import { workflowClient, WorkflowExecutionResult, WorkflowTemplate } from '@/lib/api/workflow-client';

export type { WorkflowTemplate };

export interface WorkflowExecution extends WorkflowExecutionResult {}

export interface UseWorkflowOptions {
  onSuccess?: (result: WorkflowExecution) => void;
  onError?: (error: Error) => void;
  autoRefresh?: boolean;
  refreshInterval?: number;
  autoStart?: boolean;
}

export function useWorkflow(workflowId?: string, options: UseWorkflowOptions = {}) {
  const {
    onSuccess,
    onError,
    autoRefresh = false,
    refreshInterval = 5000,
    autoStart = false,
  } = options;

  const [isLoading, setIsLoading] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [execution, setExecution] = useState<WorkflowExecution | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const isMounted = useRef(true);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMounted.current = false;
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
      }
    };
  }, []);

  // Start auto-refresh if enabled
  useEffect(() => {
    if (autoRefresh && execution?.executionId && !isPolling) {
      startPolling(execution.executionId);
    }
    return () => {
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [autoRefresh, execution?.executionId, isPolling]);

  // Auto-start workflow if specified
  useEffect(() => {
    if (autoStart && workflowId) {
      executeWorkflow(workflowId);
    }
  }, [autoStart, workflowId]);

  const startPolling = useCallback((executionId: string) => {
    if (!isMounted.current) return;

    setIsPolling(true);
    
    const poll = async () => {
      if (!isMounted.current) return;
      
      try {
        const status = await workflowClient.getWorkflowStatus(workflowId!, executionId);
        setExecution(status);

        if (['completed', 'failed'].includes(status.status)) {
          setIsPolling(false);
          onSuccess?.(status);
          return;
        }

        
        // Continue polling
        pollingRef.current = setTimeout(poll, refreshInterval);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to poll workflow status');
        setError(error);
        onError?.(error);
        setIsPolling(false);
      }
    };

    poll();
  }, [onSuccess, onError, refreshInterval, workflowId]);

  const executeWorkflow = useCallback(async (
    workflowIdOrTemplate: string | WorkflowTemplate,
    input: Record<string, any> = {},
    context: Record<string, any> = {},
    execute = true
  ): Promise<WorkflowExecution> => {
    if (!isMounted.current) {
      throw new Error('Hook is not mounted');
    }

    setIsLoading(true);
    setIsExecuting(true);
    setError(null);
    
    try {
      let result: WorkflowExecution;
      
      if (typeof workflowIdOrTemplate === 'string') {
        // Execute by workflow ID
        result = await workflowClient.executeWorkflow(
          workflowIdOrTemplate,
          input,
          context,
          execute
        );
      } else {
        // Execute template workflow
        result = await workflowClient.executeTemplateWorkflow(
          workflowIdOrTemplate,
          input,
          context
        );
      }

      setExecution(result);
      
      if (autoRefresh && result.executionId) {
        startPolling(result.executionId);
      }
      
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to execute workflow');
      setError(error);
      onError?.(error);
      throw error;
    } finally {
      if (isMounted.current) {
        setIsLoading(false);
        setIsExecuting(false);
      }
    }
  }, [autoRefresh, onError, startPolling]);

  const getWorkflowStatus = useCallback(async (executionId: string): Promise<WorkflowExecution> => {
    if (!workflowId) {
      throw new Error('workflowId is required');
    }
    
    setIsLoading(true);
    
    try {
      const response = await fetch(`/api/workflows/executions/${executionId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get workflow status: ${response.statusText}`);
      }

      return await response.json();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('An unknown error occurred');
      setError(error);
      throw error;
    }
  }, []);

  return { 
    executeWorkflow, 
    getWorkflowStatus,
    isLoading, 
    error 
  };
}
