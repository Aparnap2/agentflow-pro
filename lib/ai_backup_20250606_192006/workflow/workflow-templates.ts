import { workflowManager } from './workflow-manager';
import type { WorkflowStep } from './workflow-manager';

// Predefined workflow templates
export const WORKFLOW_TEMPLATES = {
  // Research workflow: Research a topic and generate a report
  RESEARCH_REPORT: 'RESEARCH_REPORT',
  
  // Content creation workflow: Generate content based on a topic
  CONTENT_CREATION: 'CONTENT_CREATION',
  
  // Data analysis workflow: Analyze data and generate insights
  DATA_ANALYSIS: 'DATA_ANALYSIS',
  
  // Customer support workflow: Handle customer support inquiries
  CUSTOMER_SUPPORT: 'CUSTOMER_SUPPORT',
} as const;

type WorkflowTemplate = keyof typeof WORKFLOW_TEMPLATES;

interface CreateWorkflowOptions {
  name: string;
  description?: string;
  context?: Record<string, any>;
  template?: WorkflowTemplate;
  customSteps?: Array<{
    agentType: string;
    input: Record<string, any>;
    id?: string;
  }>;
}

export async function createWorkflow(options: CreateWorkflowOptions) {
  const { name, description, context = {}, template, customSteps } = options;
  
  let steps = [];
  
  // Use predefined templates or custom steps
  if (template && !customSteps) {
    steps = getTemplateSteps(template, context);
  } else if (customSteps) {
    steps = customSteps.map(step => ({
      ...step,
      id: step.id || crypto.randomUUID(),
      status: 'pending' as const,
      input: step.input || {},
      metadata: {},
      output: undefined,
      error: undefined,
    } as WorkflowStep));
  } else {
    throw new Error('Either template or customSteps must be provided');
  }
  
  return workflowManager.createWorkflow({
    name,
    description,
    steps,
    context,
  });
}

function getTemplateSteps(template: WorkflowTemplate, context: Record<string, any>) {
  const baseContext = {
    ...context,
    timestamp: new Date().toISOString(),
  };

  // Helper function to create a workflow step with required fields
  const createStep = (
    id: string,
    agentType: string,
    input: Record<string, any> = {},
    name: string = id.charAt(0).toUpperCase() + id.slice(1).replace(/-/g, ' '),
    description: string = `Step ${id}`,
    role: string = agentType.charAt(0).toUpperCase() + agentType.slice(1),
    goal: string = `Execute ${id} step`
  ): WorkflowStep => ({
    id,
    name,
    description,
    agentType,
    role,
    goal,
    input,
    status: 'pending' as const,
    metadata: {},
    output: undefined,
    error: undefined,
  });

  const { topic, maxResults, sources, analysisType, format, style, contentType, tone, wordCount, reviewCriteria } = context;

  switch (template) {
    case WORKFLOW_TEMPLATES.RESEARCH_REPORT:
      return [
        createStep(
          'research',
          'research',
          {
            topic: topic || 'AI in 2024',
            maxResults: maxResults || 10,
            sources: sources || ['web', 'academic', 'news'],
          },
          'Research',
          'Gather information about the topic',
          'Researcher',
          'Find relevant information about the topic'
        ),
        createStep(
          'analyze',
          'analysis',
          {
            researchData: '{{research.output}}',
            analysisType: analysisType || 'trends',
          },
          'Analysis',
          'Analyze the research data',
          'Analyst',
          'Extract key insights from the research'
        ),
        createStep(
          'generate-report',
          'content',
          {
            analysis: '{{analyze.output}}',
            format: format || 'markdown',
            style: style || 'professional',
          },
          'Generate Report',
          'Create a report from the analysis',
          'Content Writer',
          'Generate a well-structured report'
        ),
      ];

    case WORKFLOW_TEMPLATES.CONTENT_CREATION:
      return [
        createStep(
          'research',
          'research',
          {
            topic: topic || 'AI in 2024',
            maxResults: maxResults || 5,
          }
        ),
        createStep(
          'outline',
          'content',
          {
            research: '{{research.output}}',
            contentType: contentType || 'blog-post',
            tone: tone || 'informative',
          }
        ),
        createStep(
          'draft',
          'content',
          {
            outline: '{{outline.output}}',
            style: style || 'engaging',
            wordCount: wordCount || 1000,
          }
        ),
        createStep(
          'review',
          'review',
          {
            content: '{{draft.output}}',
            criteria: reviewCriteria || ['clarity', 'accuracy', 'engagement'],
          }
        ),
      ];

    case WORKFLOW_TEMPLATES.DATA_ANALYSIS:
      return [
        createStep(
          'preprocess',
          'data',
          {
            data: context.data || [],
            operations: context.preprocessingSteps || ['clean', 'normalize'],
          }
        ),
        createStep(
          'analyze',
          'analysis',
          {
            data: '{{preprocess.output}}',
            analysisType: analysisType || 'trends',
          }
        ),
        createStep(
          'visualize',
          'data',
          {
            analysis: '{{analyze.output}}',
            visualizationType: context.visualizationType || 'chart',
          }
        ),
      ];

    case WORKFLOW_TEMPLATES.CUSTOMER_SUPPORT:
      return [
        createStep(
          'classify',
          'classifier',
          {
            message: context.message || '',
            categories: context.categories || ['billing', 'technical', 'account', 'general'],
          }
        ),
        createStep(
          'retrieve',
          'retrieval',
          {
            query: '{{classify.output.query}}',
            context: '{{classify.output.context}}',
            maxResults: 3,
          }
        ),
        createStep(
          'respond',
          'support',
          {
            classification: '{{classify.output}}',
            context: '{{retrieve.output}}',
            tone: tone || 'friendly',
          }
        ),
      ];

    default:
      throw new Error(`Unknown workflow template: ${template}`);
  }
}

// Helper function to create a workflow from a template
export async function createWorkflowFromTemplate(
  template: WorkflowTemplate,
  options: Omit<CreateWorkflowOptions, 'template' | 'customSteps'> & {
    context?: Record<string, any>;
  }
) {
  return createWorkflow({
    ...options,
    template,
  });
}

// Helper function to create a custom workflow
export async function createCustomWorkflow(
  options: Omit<CreateWorkflowOptions, 'template'>
) {
  if (!options.customSteps || options.customSteps.length === 0) {
    throw new Error('customSteps must be provided for custom workflows');
  }
  
  return createWorkflow(options);
}
