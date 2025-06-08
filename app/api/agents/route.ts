import { NextResponse } from 'next/server';
import { auth } from '@/auth';
import { AgentFactory } from '@/lib/ai/agent-factory';
import { toolRegistry } from '@/lib/ai/tools/tool-registry';
import { log } from '@/lib/ai/utils/logger';

// Initialize the agent factory with supported agents
const agentFactory = AgentFactory.getInstance();

// Register agent types (in a real app, this would be in a separate initialization file)
// agentFactory.registerAgent('support', SupportAgent);

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

    const { agentType, task, context = {} } = await request.json();

    if (!agentType || !task) {
      return NextResponse.json(
        { error: 'agentType and task are required' },
        { status: 400 }
      );
    }

    // Create the agent
    const agent = agentFactory.createAgent(agentType, {
      id: `user-${session.user.id}-${Date.now()}`,
      name: `${agentType}-agent`,
      role: 'AI Assistant',
      goal: 'Assist the user with their request',
      verbose: process.env.NODE_ENV === 'development',
    });

    // Process the task
    const result = await agent.processTask(task, {
      ...context,
      userId: session.user.id,
      timestamp: new Date().toISOString(),
    });

    // Log the interaction for analytics
    log.info('Agent task completed', {
      agentType,
      task,
      userId: session.user.id,
      success: result.success,
    });

    return NextResponse.json({
      success: true,
      data: result,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    log.error('Agent API error', { error: errorMessage });
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to process request',
        details: process.env.NODE_ENV === 'development' ? errorMessage : undefined
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  // Return available agents and tools
  return NextResponse.json({
    agents: agentFactory.listRegisteredAgents(),
    tools: toolRegistry.listTools(),
  });
}
