import React, { createContext, useContext, ReactNode } from 'react';
import { useAgent } from '@/hooks/useAgent';
import { useWorkflow } from '@/hooks/useWorkflow';

interface AgentContextType {
  executeTask: (agentType: string, task: string, context?: Record<string, any>) => Promise<any>;
  executeWorkflow: (workflowId: string, inputData?: Record<string, any>, context?: Record<string, any>, isAsync?: boolean) => Promise<any>;
  getWorkflowStatus: (executionId: string) => Promise<any>;
  isLoading: boolean;
  error: Error | null;
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export function AgentProvider({ children }: { children: ReactNode }) {
  const { executeTask, isLoading: agentLoading, error: agentError } = useAgent();
  const { 
    executeWorkflow, 
    getWorkflowStatus, 
    isLoading: workflowLoading, 
    error: workflowError 
  } = useWorkflow();

  const isLoading = agentLoading || workflowLoading;
  const error = agentError || workflowError;

  return (
    <AgentContext.Provider
      value={{
        executeTask,
        executeWorkflow,
        getWorkflowStatus,
        isLoading,
        error,
      }}
    >
      {children}
    </AgentContext.Provider>
  );
}

export function useAgentContext() {
  const context = useContext(AgentContext);
  if (context === undefined) {
    throw new Error('useAgentContext must be used within an AgentProvider');
  }
  return context;
}
