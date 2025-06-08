import { NextResponse } from 'next/server';
import { auth } from '@/auth';
import { workflowManager } from '@/lib/ai/workflow/workflow-manager';
import { log } from '@/lib/ai/utils/logger';

// Workflow execution
export async function POST(request: Request) {
  try {
    // Verify authentication
    const session = await auth();
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { workflowId, input, context = {}, execute = true } = await request.json();

    if (!workflowId) {
      return NextResponse.json(
        { error: 'workflowId is required' },
        { status: 400 }
      );
    }

    // Execute the workflow
    const result = await workflowManager.executeWorkflow(
      workflowId,
      input,
      {
        ...context,
        userId: session.user.id,
        timestamp: new Date().toISOString(),
      },
      execute
    );

    // Log the workflow execution
    log.info('Workflow execution completed', {
      workflowId,
      userId: session.user.id,
      status: result.success ? 'success' : 'failed',
      duration: result.metadata?.duration,
    });

    return NextResponse.json(result);
  } catch (error) {
    log.error('Workflow execution failed', { error });
    return NextResponse.json(
      { error: 'Failed to execute workflow', details: error.message },
      { status: 500 }
    );
  }
}

// Get workflow status
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const workflowId = searchParams.get('workflowId');
    const executionId = searchParams.get('executionId');

    if (!workflowId || !executionId) {
      return NextResponse.json(
        { error: 'workflowId and executionId are required' },
        { status: 400 }
      );
    }

    const status = await workflowManager.getWorkflowStatus(workflowId, executionId);
    
    if (!status) {
      return NextResponse.json(
        { error: 'Workflow execution not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(status);
  } catch (error) {
    log.error('Failed to get workflow status', { error });
    return NextResponse.json(
      { error: 'Failed to get workflow status', details: error.message },
      { status: 500 }
    );
  }
}
