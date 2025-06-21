export interface AgentAction {
  id: string
  agentId: string
  agentName: string
  action: string
  description: string
  status: "queued" | "in_progress" | "completed" | "paused" | "cancelled" | "failed"
  startTime: string
  endTime?: string
  duration?: string
  parentTaskId?: string
  childActions?: AgentAction[]
  priority: "low" | "medium" | "high" | "urgent"
  progress: number
  metadata?: {
    toolsUsed?: string[]
    apiCalls?: number
    tokensUsed?: number
    cost?: number
  }
}

export interface TaskOrchestration {
  id: string
  title: string
  description: string
  orchestratedBy: string
  status: "planning" | "executing" | "paused" | "completed" | "cancelled"
  startTime: string
  estimatedCompletion?: string
  progress: number
  parallelActions: AgentAction[]
  dependencies: string[]
  totalCost: number
}

export interface SystemMetrics {
  totalActions: number
  activeActions: number
  completedToday: number
  successRate: number
  avgExecutionTime: string
  totalCost: number
  apiCallsToday: number
  tokensUsedToday: number
}
