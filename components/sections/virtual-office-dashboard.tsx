"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { ChatInterface } from "@/components/ui/chat-interface"
import { VirtualTeamPanel } from "@/components/ui/virtual-team-panel"
import { ApprovalQueue } from "@/components/ui/approval-queue"
import { StatCard } from "@/components/ui/stat-card"
import { Users, CheckCircle, Clock, TrendingUp } from "lucide-react"
import type { VirtualAgent, Task, Message } from "@/types/virtual-office"

// Mock data
const virtualTeam: VirtualAgent[] = [
  {
    id: "cofounder",
    name: "Alex Chen",
    role: "Co-Founder Agent",
    status: "active",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Strategic, visionary, collaborative",
    expertise: ["Business Strategy", "Product Vision", "Team Leadership"],
    workload: 75,
    performance: { tasksCompleted: 156, successRate: 94, avgResponseTime: "2.3min" },
  },
  {
    id: "manager",
    name: "Sarah Kim",
    role: "Manager Agent",
    status: "working",
    currentTask: "Reviewing CRM automation workflow",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Organized, detail-oriented, diplomatic",
    expertise: ["Project Management", "Team Coordination", "Process Optimization"],
    workload: 85,
    performance: { tasksCompleted: 234, successRate: 97, avgResponseTime: "1.8min" },
  },
  {
    id: "crm-specialist",
    name: "Mike Rodriguez",
    role: "CRM Specialist",
    status: "idle",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Analytical, customer-focused, systematic",
    expertise: ["Lead Management", "Sales Pipeline", "Customer Segmentation"],
    workload: 45,
    performance: { tasksCompleted: 89, successRate: 92, avgResponseTime: "3.1min" },
  },
  {
    id: "email-specialist",
    name: "Emma Thompson",
    role: "Email Marketing Specialist",
    status: "working",
    currentTask: "Creating drip sequence for new leads",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Creative, data-driven, persuasive",
    expertise: ["Email Campaigns", "Marketing Automation", "A/B Testing"],
    workload: 60,
    performance: { tasksCompleted: 127, successRate: 89, avgResponseTime: "2.7min" },
  },
]

const pendingTasks: Task[] = [
  {
    id: "task-1",
    title: "Implement Lead Scoring System",
    description: "Set up automated lead scoring based on engagement and company size",
    assignedTo: "crm-specialist",
    requestedBy: "manager",
    status: "pending_approval",
    priority: "high",
    estimatedTime: "4 hours",
    createdAt: new Date().toISOString(),
    approvalRequired: true,
  },
  {
    id: "task-2",
    title: "Create Welcome Email Sequence",
    description: "Design 5-email welcome sequence for new subscribers",
    assignedTo: "email-specialist",
    requestedBy: "manager",
    status: "pending_approval",
    priority: "medium",
    estimatedTime: "6 hours",
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    approvalRequired: true,
  },
]

const chatMessages: Message[] = [
  {
    id: "1",
    sender: "Alex Chen",
    content:
      "Good morning! I've been analyzing our Q1 performance. We should focus on automating our lead qualification process to improve conversion rates.",
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    type: "text",
  },
  {
    id: "2",
    sender: "You",
    content: "That sounds great, Alex. What's your recommendation for the implementation approach?",
    timestamp: new Date(Date.now() - 7000000).toISOString(),
    type: "text",
  },
  {
    id: "3",
    sender: "Alex Chen",
    content:
      "I suggest we start with CRM automation and email marketing integration. Sarah can coordinate the team to implement this in phases.",
    timestamp: new Date(Date.now() - 6800000).toISOString(),
    type: "text",
  },
  {
    id: "4",
    sender: "Sarah Kim",
    content:
      "I'd like to assign the lead scoring system to Mike and the email sequences to Emma. May I have your approval to proceed?",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    type: "approval_request",
    metadata: { taskId: "task-1" },
  },
]

export function VirtualOfficeDashboard() {
  const [messages, setMessages] = useState<Message[]>(chatMessages)
  const [tasks, setTasks] = useState<Task[]>(pendingTasks)

  const handleSendMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      content,
      timestamp: new Date().toISOString(),
      type: "text",
    }
    setMessages((prev) => [...prev, newMessage])
  }

  const handleApproveTask = (taskId: string) => {
    setTasks((prev) => prev.map((task) => (task.id === taskId ? { ...task, status: "approved" as const } : task)))

    const approvalMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      content: `Task approved: ${tasks.find((t) => t.id === taskId)?.title}`,
      timestamp: new Date().toISOString(),
      type: "text",
    }
    setMessages((prev) => [...prev, approvalMessage])
  }

  const handleRejectTask = (taskId: string) => {
    setTasks((prev) => prev.map((task) => (task.id === taskId ? { ...task, status: "rejected" as const } : task)))

    const rejectionMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      content: `Task rejected: ${tasks.find((t) => t.id === taskId)?.title}. Please provide more details.`,
      timestamp: new Date().toISOString(),
      type: "text",
    }
    setMessages((prev) => [...prev, rejectionMessage])
  }

  const stats = {
    activeAgents: virtualTeam.filter((a) => a.status === "active" || a.status === "working").length,
    pendingApprovals: tasks.filter((t) => t.status === "pending_approval").length,
    tasksCompleted: virtualTeam.reduce((sum, agent) => sum + agent.performance.tasksCompleted, 0),
    avgSuccessRate: Math.round(
      virtualTeam.reduce((sum, agent) => sum + agent.performance.successRate, 0) / virtualTeam.length,
    ),
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Virtual Office Dashboard</h2>
          <p className="text-muted-foreground">Command and monitor your AI-powered virtual team</p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 px-3 py-1">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            {stats.activeAgents} Active
          </Badge>
          <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200 px-3 py-1">
            <Clock className="w-3 h-3 mr-1" />
            {stats.pendingApprovals} Pending
          </Badge>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Team Members"
          value={stats.activeAgents}
          description="AI agents working"
          icon={Users}
          color="blue"
        />
        <StatCard
          title="Pending Approvals"
          value={stats.pendingApprovals}
          description="Tasks awaiting approval"
          icon={Clock}
          color="orange"
        />
        <StatCard
          title="Tasks Completed"
          value={stats.tasksCompleted}
          description="Total team output"
          icon={CheckCircle}
          color="green"
        />
        <StatCard
          title="Success Rate"
          value={`${stats.avgSuccessRate}%`}
          description="Team performance"
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <ChatInterface
            participants={virtualTeam}
            messages={messages}
            onSendMessage={handleSendMessage}
            onApproveTask={handleApproveTask}
            onRejectTask={handleRejectTask}
          />
        </div>

        {/* Team Panel */}
        <div>
          <VirtualTeamPanel agents={virtualTeam} />
        </div>
      </div>

      {/* Approval Queue */}
      <ApprovalQueue tasks={tasks} agents={virtualTeam} onApprove={handleApproveTask} onReject={handleRejectTask} />
    </div>
  )
}
