import { useState, useEffect, useCallback } from 'react';
import { agentApi, crewApi, workflowApi, chatApi } from '../services/api';

// Hook for agent operations
export const useAgents = () => {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await agentApi.getAgents();
      setAgents(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch agents');
      console.error('Error fetching agents:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createAgent = useCallback(async (agentData: any) => {
    setLoading(true);
    setError(null);
    try {
      const newAgent = await agentApi.createAgent(agentData);
      setAgents(prev => [...prev, newAgent]);
      return newAgent;
    } catch (err: any) {
      setError(err.message || 'Failed to create agent');
      console.error('Error creating agent:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const processTask = useCallback(async (agentId: string, task: string, context = {}) => {
    setLoading(true);
    setError(null);
    try {
      const result = await agentApi.processTask(agentId, task, context);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to process task');
      console.error('Error processing task:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return {
    agents,
    loading,
    error,
    fetchAgents,
    createAgent,
    processTask
  };
};

// Hook for crew operations
export const useCrews = () => {
  const [crews, setCrews] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCrews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await crewApi.getCrews();
      setCrews(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch crews');
      console.error('Error fetching crews:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createCrew = useCallback(async (crewData: any) => {
    setLoading(true);
    setError(null);
    try {
      const newCrew = await crewApi.createCrew(crewData);
      setCrews(prev => [...prev, newCrew]);
      return newCrew;
    } catch (err: any) {
      setError(err.message || 'Failed to create crew');
      console.error('Error creating crew:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const executeTask = useCallback(async (crewId: string, task: string, context = {}) => {
    setLoading(true);
    setError(null);
    try {
      const result = await crewApi.executeTask(crewId, task, context);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to execute task');
      console.error('Error executing task:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCrews();
  }, [fetchCrews]);

  return {
    crews,
    loading,
    error,
    fetchCrews,
    createCrew,
    executeTask
  };
};

// Hook for workflow operations
export const useWorkflows = () => {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await workflowApi.getWorkflows();
      setWorkflows(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch workflows');
      console.error('Error fetching workflows:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createWorkflow = useCallback(async (workflowData: any) => {
    setLoading(true);
    setError(null);
    try {
      const newWorkflow = await workflowApi.createWorkflow(workflowData);
      setWorkflows(prev => [...prev, newWorkflow]);
      return newWorkflow;
    } catch (err: any) {
      setError(err.message || 'Failed to create workflow');
      console.error('Error creating workflow:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const executeWorkflow = useCallback(async (
    workflowId: string, 
    inputData: any = {}, 
    context: any = {}, 
    asyncExecution: boolean = false
  ) => {
    setLoading(true);
    setError(null);
    try {
      const result = await workflowApi.executeWorkflow(workflowId, inputData, context, asyncExecution);
      
      // If it's an async execution, we'll need to poll for the result
      if (asyncExecution && result.status === 'started') {
        return result;
      }
      
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to execute workflow');
      console.error('Error executing workflow:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchExecutions = useCallback(async (workflowId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await workflowApi.listWorkflowExecutions(workflowId);
      setExecutions(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch workflow executions');
      console.error('Error fetching workflow executions:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const getExecution = useCallback(async (executionId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await workflowApi.getWorkflowExecution(executionId);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to get workflow execution');
      console.error('Error getting workflow execution:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  return {
    workflows,
    executions,
    loading,
    error,
    fetchWorkflows,
    createWorkflow,
    executeWorkflow,
    fetchExecutions,
    getExecution
  };
};

// Hook for chat operations
export const useChat = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (message: string, context = {}) => {
    setLoading(true);
    setError(null);
    try {
      const result = await chatApi.sendMessage(message, context);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      console.error('Error sending message:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    sendMessage
  };
};