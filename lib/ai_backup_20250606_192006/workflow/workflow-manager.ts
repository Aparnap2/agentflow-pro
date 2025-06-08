import { log } from '../utils/logger';
import { AgentFactory } from '../agent-factory';
import type { AgentConfig, AgentResponse } from '../types';

// Using crypto.randomUUID() instead of uuid package
const uuidv4 = () => crypto.randomUUID();

// Export the WorkflowStep type for use in other files
export type WorkflowStep = {
  id: string;
  name: string;
  description?: string;
  agentType: string;
  input: Record<string, any>;
  output?: any;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  error?: string;
  metadata?: Record<string, any>;
  role?: string;
  goal?: string;
};

// Using AgentType from agent-factory to ensure type safety
type AgentType = 'support' | 'sales' | 'content' | 'analyst' | 'general';

type WorkflowStepInput = Record<string, any>;

// WorkflowAgentConfig ensures required fields are always provided
interface WorkflowAgentConfig extends Omit<AgentConfig, 'id' | 'name' | 'role' | 'goal'> {
  id: string;
  name: string;
  role: string;
  goal: string;
}

type WorkflowDefinition = {
  id: string;
  name: string;
  description?: string;
  steps: WorkflowStep[];
  context?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
};

type WorkflowExecution = {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  results: Record<string, {
    success: boolean;
    output?: any;
    error?: string;
    metadata: {
      startedAt: Date;
      completedAt: Date;
      duration: number;
    };
  }>;
  error?: string;
  steps: WorkflowStep[];
  currentStep?: string;
  context: Record<string, any>;
  metadata: {
    createdAt: Date;
    startedAt: Date;
    completedAt?: Date;
    duration?: number;
    createdBy: string;
  };
};

type WorkflowStepResult = {
  success: boolean;
  output?: any;
  error?: string;
  stepId: string;
  timestamp: string;
};

class WorkflowManager {
  private static instance: WorkflowManager;
  private workflows: Map<string, WorkflowDefinition> = new Map();
  private executions: Map<string, WorkflowExecution> = new Map();
  private agentFactory: ReturnType<typeof AgentFactory.getInstance>;

  private constructor() {
    this.agentFactory = AgentFactory.getInstance();
  }

  public static getInstance(): WorkflowManager {
    if (!WorkflowManager.instance) {
      WorkflowManager.instance = new WorkflowManager();
    }
    return WorkflowManager.instance;
  }

  private isValidAgentType(agentType: string): agentType is AgentType {
    return [
      'research', 'analysis', 'content', 'review', 
      'data', 'classifier', 'retrieval', 'support'
    ].includes(agentType);
  }

  private async executeAgent(
    agentType: AgentType, 
    input: WorkflowStepInput,
    stepId: string,
    context: Record<string, any> = {}
  ): Promise<AgentResponse> {
    const agentConfig: WorkflowAgentConfig = {
      id: `workflow-agent-${stepId}`,
      name: `${agentType}-agent`,
      role: `Handles ${agentType} tasks in workflows`,
      goal: `Execute ${agentType} tasks as part of a workflow`,
      verbose: process.env.NODE_ENV === 'development',
      ...(input.agentConfig || {})
    };

    try {
      const agent = this.agentFactory.createAgent(agentType, agentConfig);
      await agent.initialize();
      
      // Process the task with the input and context
      const taskInput = typeof input === 'string' ? input : JSON.stringify(input);
      const result = await agent.processTask(taskInput, context);
      
      // Clean up the agent
      await agent.cleanup();
      
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error executing agent';
      log.error(`Error in ${agentType} agent (step ${stepId}):`, { error: errorMessage });
      throw error;
    }
  }

  private handleError(error: unknown, context: string = 'Workflow execution error', execution?: WorkflowExecution): never {
    const errorMessage = error instanceof Error ? error.message : String(error);
    const errorObj = error instanceof Error ? error : new Error(errorMessage);
    
    // Update execution state if provided
    if (execution) {
      execution.status = 'failed';
      execution.error = errorMessage;
      execution.metadata = execution.metadata || {
        createdAt: new Date(),
        startedAt: new Date(),
        createdBy: 'system',
      };
      execution.metadata.completedAt = new Date();
      if (execution.metadata.startedAt) {
        execution.metadata.duration = Date.now() - execution.metadata.startedAt.getTime();
      }
    }
    
    // Ensure we're passing a proper error object to log.error
    log.error(`${context}:`, { error: errorMessage });
    throw errorObj;
  }

  private resolveTemplates(input: any, context: Record<string, any> = {}): any {
    if (typeof input === 'string') {
      // Simple template replacement: {{variable}}
      return input.replace(/\{\{([^}]+)\}\}/g, (_: string, key: string) => {
        const value = context[key.trim()];
        return value !== undefined ? String(value) : '';
      });
    } else if (Array.isArray(input)) {
      return input.map(item => this.resolveTemplates(item, context));
    } else if (typeof input === 'object' && input !== null) {
      const result: Record<string, any> = {};
      for (const [key, value] of Object.entries(input)) {
        result[key] = this.resolveTemplates(value, context);
      }
      return result;
    }
    return input;
  }

  public async createWorkflow(definition: Omit<WorkflowDefinition, 'id' | 'createdAt' | 'updatedAt'>) {
    const workflowId = uuidv4();
    const now = new Date();
    
    const workflow: WorkflowDefinition = {
      ...definition,
      id: workflowId,
      steps: definition.steps.map(step => ({
        ...step,
        id: step.id || uuidv4(),
        status: 'pending',
      })),
      createdAt: now,
      updatedAt: now,
    };

    this.workflows.set(workflowId, workflow);
    return workflow;
  }

  public async getWorkflow(workflowId: string): Promise<WorkflowDefinition | undefined> {
    return this.workflows.get(workflowId);
  }

  public async executeWorkflow(
    workflowId: string,
    input: Record<string, any>,
    context: Record<string, any> = {},
    execute = true
  ): Promise<{
    success: boolean;
    executionId: string;
    status: string;
    result?: Record<string, any>;
    error?: string;
    message?: string;
  }> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow ${workflowId} not found`);
    }

    const executionId = crypto.randomUUID();
    const startedAt = new Date();

    const execution: WorkflowExecution = {
      id: executionId,
      workflowId: workflow.id,
      status: 'pending',
      steps: workflow.steps.map(step => ({
        ...step,
        name: step.name || `Step ${step.id}`,
        status: 'pending' as const,
        input: step.input || {},
        output: undefined,
        error: undefined,
        metadata: {},
      })),
      results: {},
      context: {
        ...workflow.context,
        ...context,
        input,
      },
      metadata: {
        createdAt: new Date(),
        startedAt: startedAt,
        createdBy: context.userId || 'system',
      },
    };

    this.executions.set(executionId, execution);

    if (execute) {
      return this.executeWorkflowSteps(executionId);
    }

    return {
      success: true,
      executionId,
      status: 'pending',
      message: 'Workflow execution created and queued',
    };
  }

  private async executeWorkflowSteps(
    executionId: string
  ): Promise<{
    success: boolean;
    executionId: string;
    status: string;
    result?: Record<string, any>;
    error?: string;
    message?: string;
  }> {
    const execution = this.executions.get(executionId);
    if (!execution) {
      throw new Error(`Execution ${executionId} not found`);
    }

    execution.status = 'running';

    try {
      for (const step of execution.steps) {
        if (step.status !== 'pending') continue;

        step.status = 'in-progress';
        
        const stepStartTime = new Date();
        try {
          // Validate agent type
          if (!this.isValidAgentType(step.agentType)) {
            throw new Error(`Invalid agent type: ${step.agentType}`);
          }

          // Execute the agent and handle the response
          const agentResponse = await this.executeAgent(step.agentType, step.input, step.id, execution.context);
          const stepEndTime = new Date();
          
          // Update step status and output
          step.status = 'completed';
          step.output = agentResponse.output;
          step.metadata = {
            ...step.metadata,
            startedAt: stepStartTime,
            completedAt: stepEndTime,
            duration: stepEndTime.getTime() - stepStartTime.getTime(),
          };
          
          // Update execution results
          execution.results[step.id] = {
            success: true,
            output: agentResponse.output,
            metadata: {
              startedAt: stepStartTime,
              completedAt: stepEndTime,
              duration: stepEndTime.getTime() - stepStartTime.getTime(),
            },
          };
          
          // Update context with step output
          if (agentResponse.output) {
            execution.context[`step_${step.id}`] = agentResponse.output;
          }
        } catch (error: unknown) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          const stepEndTime = new Date();
          
          // Update step with error information
          step.status = 'failed';
          step.error = errorMessage;
          step.metadata = {
            ...step.metadata,
            error: errorMessage,
            startedAt: stepStartTime,
            completedAt: stepEndTime,
            duration: stepEndTime.getTime() - stepStartTime.getTime(),
          };
          
          // Update execution state
          execution.status = 'failed';
          execution.error = errorMessage;
          execution.metadata.completedAt = stepEndTime;
          execution.metadata.duration = stepEndTime.getTime() - (execution.metadata.startedAt?.getTime() || stepEndTime.getTime());
          
          // Update results with error
          execution.results[step.id] = {
            success: false,
            error: errorMessage,
            metadata: {
              startedAt: stepStartTime,
              completedAt: stepEndTime,
              duration: stepEndTime.getTime() - stepStartTime.getTime(),
            },
          };
          
          throw error;
        }
      }

      // If we get here, all steps completed successfully
      execution.status = 'completed';
      execution.metadata.completedAt = new Date();
      if (execution.metadata.startedAt) {
        execution.metadata.duration = 
          execution.metadata.completedAt.getTime() - execution.metadata.startedAt.getTime();
      }

      return {
        success: true,
        executionId: execution.id,
        status: execution.status,
        result: execution.results,
      };
    } catch (error) {
      if (!execution) {
        // This should never happen as we check for execution at the start of the method
        throw new Error('Execution not found when handling error');
      }
      return this.handleExecutionError(error, 'Error executing workflow steps', execution);
    }
  }

  private handleExecutionError(
    error: unknown,
    context: string,
    execution: WorkflowExecution
  ): { success: boolean; executionId: string; status: string; error: string } {
    const errorMessage = error instanceof Error ? error.message : String(error);
    const errorStack = error instanceof Error ? error.stack : undefined;
    
    log.error(`${context}: ${errorMessage}`, { 
      error: errorMessage,
      stack: errorStack,
      executionId: execution?.id,
      workflowId: execution?.workflowId,
    });
    
    if (execution) {
      execution.status = 'failed';
      execution.error = errorMessage;
      
      // Ensure metadata exists before updating
      execution.metadata = execution.metadata || {};
      execution.metadata.completedAt = new Date();
      
      if (execution.metadata.startedAt) {
        execution.metadata.duration = 
          execution.metadata.completedAt.getTime() - execution.metadata.startedAt.getTime();
      }
      
      // Update current step if available
      if (execution.currentStep) {
        const step = execution.steps.find(s => s.id === execution.currentStep);
        if (step) {
          step.status = 'failed';
          step.error = errorMessage;
          step.metadata = {
            ...(step.metadata || {}),
            error: errorMessage,
            completedAt: new Date(),
          };
          
          if (step.metadata.startedAt) {
            step.metadata.duration = 
              step.metadata.completedAt.getTime() - step.metadata.startedAt.getTime();
          }
        }
      }
    }
    
    return {
      success: false,
      error: errorMessage,
      status: 'failed' as const,
      executionId: execution?.id,
    };
  }

  public async getWorkflowStatus(executionId: string) {
    const execution = this.executions.get(executionId);
    if (!execution) {
      throw new Error(`No execution found with ID: ${executionId}`);
    }

    if (execution.status === 'failed' || execution.status === 'completed') {
      return {
        success: execution.status === 'completed',
        error: execution.error,
        executionId: execution.id,
        workflowId: execution.workflowId,
        metadata: {
          startedAt: execution.metadata.startedAt,
          completedAt: execution.metadata.completedAt,
          duration: execution.metadata.duration,
        },
      };
    }

    const currentStep = execution.steps.find(s => s.status === 'in-progress');
    return {
      success: true,
      executionId: execution.id,
      workflowId: execution.workflowId,
      status: execution.status,
      progress: currentStep ? {
        stepId: currentStep.id,
        name: currentStep.name || 'Unknown',
        completed: Object.keys(execution.results).length,
        total: execution.steps.length,
      } : undefined,
      metadata: {
        startedAt: execution.metadata.startedAt,
        ...(execution.metadata.completedAt && {
          completedAt: execution.metadata.completedAt,
          duration: execution.metadata.duration,
        }),
      },
    };
  }
}

export const workflowManager = WorkflowManager.getInstance();
