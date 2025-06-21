export interface User {
  id: string
  name: string
  email: string
  role: "admin" | "ceo"
  avatar?: string
}

export interface VirtualAgent {
  id: string
  name: string
  role: string
  status: "active" | "idle" | "working" | "waiting_approval"
  currentTask?: string
  avatar: string
  personality: string
  expertise: string[]
  workload: number
  performance: {
    tasksCompleted: number
    successRate: number
    avgResponseTime: string
  }
}

export interface Task {
  id: string
  title: string
  description: string
  assignedTo: string
  requestedBy: string
  status: "pending_approval" | "approved" | "in_progress" | "completed" | "rejected"
  priority: "low" | "medium" | "high" | "urgent"
  estimatedTime: string
  createdAt: string
  dueDate?: string
  approvalRequired: boolean
}

export interface Conversation {
  id: string
  participants: string[]
  messages: Message[]
  topic: string
  status: "active" | "archived"
}

export interface Message {
  id: string
  sender: string
  content: string
  timestamp: string
  type: "text" | "task_request" | "approval_request" | "system"
  metadata?: any
}

export interface BusinessPlan {
  id: string
  title: string
  description: string
  objectives: string[]
  timeline: string
  resources: string[]
  status: "draft" | "discussing" | "approved" | "executing"
  createdBy: string
  lastUpdated: string
}
