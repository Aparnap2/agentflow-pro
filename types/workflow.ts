export interface ResearchPlan {
  id: string
  title: string
  description: string
  researchFindings: string[]
  proposedActions: string[]
  expectedOutcomes: string[]
  timeline: string
  resources: string[]
  risks: string[]
  budget: number
  priority: "low" | "medium" | "high" | "urgent"
  createdBy: string
  createdAt: string
  status: "pending_approval" | "approved" | "rejected" | "executing"
}

export interface WorkflowExecution {
  id: string
  planId: string
  orchestratedBy: string
  status: "planning" | "executing" | "paused" | "completed" | "cancelled"
  startTime: string
  phases: WorkflowPhase[]
  activeAgents: string[]
  progress: number
  totalCost: number
}

export interface WorkflowPhase {
  id: string
  name: string
  description: string
  assignedAgents: string[]
  dependencies: string[]
  status: "pending" | "in_progress" | "completed" | "blocked"
  startTime?: string
  endTime?: string
  progress: number
  tasks: WorkflowTask[]
}

export interface WorkflowTask {
  id: string
  title: string
  description: string
  assignedTo: string
  status: "queued" | "in_progress" | "completed" | "paused" | "failed"
  priority: "low" | "medium" | "high" | "urgent"
  estimatedTime: string
  actualTime?: string
  progress: number
  dependencies: string[]
  outputs?: string[]
}

export interface AgentInterruption {
  id: string
  agentId: string
  taskId: string
  reason: string
  newInstructions: string
  requestedBy: string
  timestamp: string
  status: "pending" | "applied" | "rejected"
}
