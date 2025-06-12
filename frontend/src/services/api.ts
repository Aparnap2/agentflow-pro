import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Agent API
export const agentApi = {
  // Get all agents
  getAgents: async () => {
    const response = await api.get('/agents/list');
    return response.data;
  },

  // Create a new agent
  createAgent: async (agentData: any) => {
    const response = await api.post('/agents/create', agentData);
    return response.data;
  },

  // Process a task with an agent
  processTask: async (agentId: string, task: string, context = {}) => {
    const response = await api.post(`/agents/${agentId}/process`, { task, context });
    return response.data;
  }
};

// Crew API
export const crewApi = {
  // Get all crews
  getCrews: async () => {
    const response = await api.get('/agents/crews/list');
    return response.data;
  },

  // Create a new crew
  createCrew: async (crewData: any) => {
    const response = await api.post('/agents/crews/create', crewData);
    return response.data;
  },

  // Execute a task with a crew
  executeTask: async (crewId: string, task: string, context = {}) => {
    const response = await api.post(`/agents/crews/${crewId}/execute`, { task, context });
    return response.data;
  }
};

// Workflow API
export const workflowApi = {
  // Get all workflows
  getWorkflows: async () => {
    const response = await api.get('/workflows');
    return response.data;
  },

  // Get a specific workflow
  getWorkflow: async (workflowId: string) => {
    const response = await api.get(`/workflows/${workflowId}`);
    return response.data;
  },

  // Create a new workflow
  createWorkflow: async (workflowData: any) => {
    const response = await api.post('/workflows', workflowData);
    return response.data;
  },

  // Execute a workflow
  executeWorkflow: async (workflowId: string, inputData: any = {}, context: any = {}, asyncExecution: boolean = false) => {
    const response = await api.post(`/workflows/${workflowId}/execute`, {
      input_data: inputData,
      context,
      async_execution: asyncExecution
    });
    return response.data;
  },

  // Get workflow execution status
  getWorkflowExecution: async (executionId: string) => {
    const response = await api.get(`/workflows/executions/${executionId}`);
    return response.data;
  },

  // List workflow executions
  listWorkflowExecutions: async (workflowId?: string) => {
    const url = workflowId 
      ? `/workflows/executions?workflow_id=${workflowId}`
      : '/workflows/executions';
    const response = await api.get(url);
    return response.data;
  }
};

// Chat API
export const chatApi = {
  // Send a chat message
  sendMessage: async (message: string, context = {}) => {
    const response = await api.post('/chat', { message, context });
    return response.data;
  }
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await axios.get('http://localhost:8000/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export default {
  agent: agentApi,
  crew: crewApi,
  workflow: workflowApi,
  chat: chatApi,
  healthCheck
};