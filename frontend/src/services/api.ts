import axios from 'axios';
import { Key, ReactNode } from 'react';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor to handle errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error:', error.response.data);
      return Promise.reject(error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('API Error: No response received', error.request);
      return Promise.reject({ message: 'No response from server' });
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Error:', error.message);
      return Promise.reject({ message: error.message });
    }
  }
);

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

// Types for Analytics and Dashboard
export interface DashboardMetrics {
  avgTaskTime: any;
  activeAgents: number;
  tasksCompleted: number;
  costSavings: number;
  timeSaved: number;
  recentActivities: Array<{
    id: string;
    agent: string;
    task: string;
    status: 'working' | 'completed' | 'pending_approval' | 'failed';
    timestamp: string;
  }>;
}

export interface AnalyticsData {
  kpis: Array<{
    label: string;
    value: string | number;
    change: string;
    changeType: 'positive' | 'negative' | 'neutral';
    description: string;
    trend: number[];
  }>;
  agentPerformance: Array<{
    id: Key | null | undefined;
    avatar: any;
    role: any;
    status: ReactNode;
    name: string;
    tasksCompleted: number;
    successRate: number;
    costSavings: number;
    timeSpent: string;
    efficiency: number;
    humanInterventions: number;
    avgResponseTime: string;
    tokenUsage: number;
  }>;
  taskCategories: Array<{
    id: Key | null | undefined;
    color: any;
    category: string;
    completed: number;
    percentage: number;
    growth: string;
  }>;
  costBreakdown: Array<{
    id: Key | null | undefined;
    color: any;
    category: string;
    amount: number;
    percentage: number;
  }>;
}

// Admin API
export const adminApi = {
  // Dashboard specific endpoints
  getDashboardOverview: async () => {
    const response = await api.get('/api/v1/admin/dashboard/overview');
    return response.data;
  },

  // System metrics
  getSystemMetrics: async (legacy: boolean = false) => {
    const response = await api.get('/api/v1/admin/system-metrics', { 
      params: { legacy } 
    });
    return response.data;
  },

  getResourceUsage: async () => {
    const response = await api.get('/api/v1/admin/system-metrics');
    return response.data;
  },

  // Activity logs
  getActivityLogs: async (limit: number = 50, offset: number = 0, severity?: string) => {
    const response = await api.get('/api/v1/admin/activity-logs', {
      params: { limit, offset, severity }
    });
    return response.data;
  },

  // Analytics data
  getAnalyticsData: async (period: string = '7d'): Promise<AnalyticsData> => {
    const response = await api.get('/api/v1/analytics', { params: { period } });
    return response.data;
  },

  // Dashboard metrics
  getDashboardMetrics: async (): Promise<DashboardMetrics> => {
    const response = await api.get('/api/v1/analytics');
    return response.data as DashboardMetrics;
  },

  // Task metrics
  getTaskMetrics: async (timeRange: string = '24h') => {
    const response = await api.get('/api/v1/analytics', {
      params: { period: timeRange }
    });
    return response.data;
  },

  // System maintenance
  clearCache: async () => {
    const response = await api.post('/api/v1/admin/clear-cache');
    return response.data;
  },

  runMaintenance: async () => {
    const response = await api.post('/api/v1/admin/run-maintenance');
    return response.data;
  },

  // These methods are now in agentManagementApi and userApi
  // Please use those instead
  getAgents: async (status?: string) => {
    console.warn('DEPRECATED: Use agentManagementApi.listAgents() instead');
    return agentManagementApi.listAgents(status);
  },

  getAgentDetails: async (agentId: string) => {
    console.warn('DEPRECATED: Use agentManagementApi.getAgentDetails() instead');
    return agentManagementApi.getAgentDetails(agentId);
  },

  controlAgent: async (agentId: string, action: 'start' | 'stop' | 'pause' | 'resume') => {
    console.warn('DEPRECATED: Use agentManagementApi.controlAgent() instead');
    return agentManagementApi.controlAgent(agentId, action as any);
  },

  getUsers: async (params: any = {}) => {
    console.warn('DEPRECATED: Use userApi.getUsers() instead');
    return userApi.getUsers(params);
  },

  getUser: async (userId: string) => {
    console.warn('DEPRECATED: Use userApi.getUser() instead');
    return userApi.getUser(userId);
  },

  createUser: async (userData: any) => {
    console.warn('DEPRECATED: Use userApi.createUser() instead');
    return userApi.createUser(userData);
  },

  updateUser: async (userId: string, userData: any) => {
    console.warn('DEPRECATED: Use userApi.updateUser() instead');
    return userApi.updateUser(userId, userData);
  },

  deleteUser: async (userId: string) => {
    console.warn('DEPRECATED: Use userApi.deleteUser() instead');
    return userApi.deleteUser(userId);
  },

  // Deprecated methods
  getTasks: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return [];
  },

  submitTask: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return {};
  },

  getPendingApprovals: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return [];
  },

  processApproval: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return {};
  },

  updateSystemSettings: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return {};
  },

  createBackup: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return {};
  },

  listBackups: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return [];
  },

  restoreBackup: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return {};
  },

  getSystemLogs: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return [];
  },

  getApiUsage: async () => {
    console.warn('DEPRECATED: This method is no longer supported');
    return {};
  }
};

// User Management API
export const userApi = {
  // Get all users
  getUsers: async (params: any = {}) => {
    const response = await api.get('/api/v1/users', { params });
    return response.data;
  },

  // Get user by ID
  getUser: async (userId: string) => {
    const response = await api.get(`/api/v1/users/${userId}`);
    return response.data;
  },

  // Create user
  createUser: async (userData: any) => {
    const response = await api.post('/api/v1/users', userData);
    return response.data;
  },

  // Update user
  updateUser: async (userId: string, userData: any) => {
    const response = await api.put(`/api/v1/users/${userId}`, userData);
    return response.data;
  },

  // Delete user
  deleteUser: async (userId: string) => {
    const response = await api.delete(`/api/v1/users/${userId}`);
    return response.data;
  },

  // Get user activity
  getUserActivity: async (userId: string, days: number = 30, limit: number = 50) => {
    const response = await api.get(`/api/v1/users/${userId}/activity`, {
      params: { days, limit }
    });
    return response.data;
  }
};

// Agent Management API
export const agentManagementApi = {
  // List all agents
  listAgents: async (status?: string) => {
    const response = await api.get('/api/v1/agents', { 
      params: { status } 
    });
    return response.data;
  },

  // Get agent details
  getAgentDetails: async (agentId: string) => {
    const response = await api.get(`/api/v1/agents/${agentId}`);
    return response.data;
  },

  // Control agent
  controlAgent: async (agentId: string, action: 'start' | 'stop' | 'restart' | 'pause' | 'resume') => {
    const response = await api.post(`/api/v1/agents/${agentId}/control`, {}, {
      params: { action }
    });
    return response.data;
  },

  // Get agent metrics
  getAgentMetrics: async (agentId: string, timeRange: string = '1h', metrics: string = 'all') => {
    const response = await api.get(`/api/v1/agents/${agentId}/metrics`, {
      params: { time_range: timeRange, metrics }
    });
    return response.data;
  },

  // Get agent performance
  getAgentPerformance: async (agentId?: string, timeRange: string = '7d') => {
    const url = agentId 
      ? `/api/v1/agents/${agentId}/performance` 
      : '/api/v1/analytics/agent-performance';
    
    const response = await api.get(url, {
      params: { time_range: timeRange }
    });
    return response.data;
  }
};

// Chat API
export const chatApi = {
  // Send a chat message
  sendMessage: async (message: string, context = {}) => {
    const response = await api.post('/api/v1/chat', { message, context });
    return response.data;
  }
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
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
  admin: adminApi,
  chat: chatApi,
  user: userApi,
  agentManagement: agentManagementApi,
  healthCheck
};