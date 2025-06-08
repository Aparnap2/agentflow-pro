import { WORKFLOW_TEMPLATES } from '@/lib/ai/workflow/workflow-templates';

export type WorkflowTemplate = keyof typeof WORKFLOW_TEMPLATES;

export interface WorkflowExecutionResult {
  success: boolean;
  executionId: string;
  status: string;
  result?: any;
  error?: string;
  metadata: {
    startedAt: Date;
    completedAt?: Date;
    duration?: number;
    steps: Array<{
      id: string;
      agentType: string;
      status: string;
      error?: string;
      metadata?: any;
    }>;
  };
}

export interface WorkflowStatusResult extends WorkflowExecutionResult {}

export class WorkflowClient {
  private baseUrl: string;
  private authToken?: string;

  constructor(baseUrl: string = '/api', authToken?: string) {
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
    this.authToken = authToken;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers = new Headers(options.headers);
    headers.set('Content-Type', 'application/json');
    
    if (this.authToken) {
      headers.set('Authorization', `Bearer ${this.authToken}`);
    }

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'Failed to execute workflow');
    }

    return response.json();
  }

  // Execute a workflow by ID
  async executeWorkflow(
    workflowId: string, 
    input: Record<string, any> = {},
    context: Record<string, any> = {},
    execute = true
  ): Promise<WorkflowExecutionResult> {
    return this.request<WorkflowExecutionResult>('/workflows', {
      method: 'POST',
      body: JSON.stringify({ workflowId, input, context, execute }),
    });
  }

  // Get workflow status
  async getWorkflowStatus(
    workflowId: string, 
    executionId: string
  ): Promise<WorkflowStatusResult> {
    return this.request<WorkflowStatusResult>(
      `/workflows?workflowId=${encodeURIComponent(workflowId)}&executionId=${encodeURIComponent(executionId)}`,
      { method: 'GET' }
    );
  }

  // Create and execute a workflow from a template
  async executeTemplateWorkflow(
    template: WorkflowTemplate,
    input: Record<string, any> = {},
    context: Record<string, any> = {}
  ): Promise<WorkflowExecutionResult> {
    return this.request<WorkflowExecutionResult>('/workflows/templates/execute', {
      method: 'POST',
      body: JSON.stringify({ template, input, context }),
    });
  }

  // Poll for workflow completion
  async waitForWorkflowCompletion(
    workflowId: string, 
    executionId: string, 
    interval: number = 1000,
    timeout: number = 300000
  ): Promise<WorkflowStatusResult> {
    const startTime = Date.now();
    
    return new Promise((resolve, reject) => {
      const checkStatus = async () => {
        try {
          const status = await this.getWorkflowStatus(workflowId, executionId);
          
          if (['completed', 'failed'].includes(status.status)) {
            resolve(status);
            return;
          }
          
          if (Date.now() - startTime >= timeout) {
            reject(new Error('Workflow execution timed out'));
            return;
          }
          
          setTimeout(checkStatus, interval);
        } catch (error) {
          reject(error);
        }
      };
      
      checkStatus();
    });
  }
}

// Default instance for use throughout the app
export const workflowClient = new WorkflowClient();
