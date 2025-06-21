"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ProfessionalFlowGraph } from "@/components/ui/professional-flow-graph"
import { ActiveAgentsPanel } from "@/components/ui/active-agents-panel"
import { AgentDetailsPanel } from "@/components/ui/agent-details-panel"
import { QuickStatusCards } from "@/components/ui/quick-status-cards"
import { Activity, Users, Play, Pause, Brain } from "lucide-react"
import type { WorkflowExecution, SystemMetrics } from "@/types/virtual-office"

// Enhanced mock data with real-time metrics
const mockActiveAgents = [
  {
    id: "manager",
    name: "Sarah Kim",
    role: "Manager Agent",
    status: "working" as const,
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Organized, detail-oriented, diplomatic",
    expertise: ["Project Management", "Team Coordination", "Process Optimization"],
    workload: 85,
    currentTask: "Orchestrating lead generation workflow",
    performance: { tasksCompleted: 234, successRate: 97, avgResponseTime: "1.8min" },
    currentTasks: [
      {
        id: "task-orchestration",
        title: "Workflow Orchestration",
        description: "Coordinating specialist agents for lead generation",
        assignedTo: "manager",
        status: "in_progress" as const,
        priority: "high" as const,
        estimatedTime: "ongoing",
        progress: 75,
        dependencies: [],
      },
    ],
    realtimeMetrics: {
      tokensPerMinute: 450,
      apiCallsPerMinute: 12,
      costPerHour: 2.34,
      currentThinking: "Analyzing task dependencies and optimizing agent allocation for maximum efficiency",
      lastAction: "Assigned lead qualification task to CRM specialist",
      nextAction: "Monitor email specialist progress and adjust timeline",
    },
  },
  {
    id: "crm-specialist",
    name: "Mike Rodriguez",
    role: "CRM Specialist",
    status: "working" as const,
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Analytical, customer-focused, systematic",
    expertise: ["Lead Management", "Sales Pipeline", "Customer Segmentation"],
    workload: 73,
    currentTask: "Processing qualified leads",
    performance: { tasksCompleted: 89, successRate: 92, avgResponseTime: "3.1min" },
    currentTasks: [
      {
        id: "task-lead-qualification",
        title: "Lead Data Enrichment",
        description: "Enriching 47 leads with company and contact information",
        assignedTo: "crm-specialist",
        status: "in_progress" as const,
        priority: "high" as const,
        estimatedTime: "25 minutes",
        progress: 68,
        dependencies: [],
        outputs: ["47 leads processed", "Company data enriched", "Contact info verified"],
      },
      {
        id: "task-lead-scoring",
        title: "Lead Scoring Analysis",
        description: "Applying ML-based scoring to qualified leads",
        assignedTo: "crm-specialist",
        status: "in_progress" as const,
        priority: "medium" as const,
        estimatedTime: "15 minutes",
        progress: 23,
        dependencies: ["task-lead-qualification"],
      },
    ],
    realtimeMetrics: {
      tokensPerMinute: 680,
      apiCallsPerMinute: 8,
      costPerHour: 1.89,
      currentThinking: "Cross-referencing lead data with LinkedIn and company databases to ensure accuracy",
      lastAction: "Enriched lead data for TechCorp Inc with 12 additional data points",
      nextAction: "Apply lead scoring algorithm to batch of 15 qualified leads",
    },
  },
  {
    id: "email-specialist",
    name: "Emma Thompson",
    role: "Email Marketing Specialist",
    status: "working" as const,
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Creative, data-driven, persuasive",
    expertise: ["Email Campaigns", "Marketing Automation", "A/B Testing"],
    workload: 60,
    currentTask: "Creating nurture sequences",
    performance: { tasksCompleted: 127, successRate: 89, avgResponseTime: "2.7min" },
    currentTasks: [
      {
        id: "task-email-templates",
        title: "Personalized Email Templates",
        description: "Creating industry-specific email templates for lead nurturing",
        assignedTo: "email-specialist",
        status: "in_progress" as const,
        priority: "high" as const,
        estimatedTime: "35 minutes",
        progress: 45,
        dependencies: ["task-lead-qualification"],
      },
    ],
    realtimeMetrics: {
      tokensPerMinute: 520,
      apiCallsPerMinute: 6,
      costPerHour: 1.45,
      currentThinking: "Analyzing successful email patterns and crafting personalized subject lines for SaaS prospects",
      lastAction: "Generated 3 email variants for software industry prospects",
      nextAction: "Create follow-up sequence for non-responders",
    },
  },
]

const mockWorkflow: WorkflowExecution = {
  id: "workflow-1",
  planId: "plan-1",
  orchestratedBy: "manager",
  status: "executing",
  startTime: new Date(Date.now() - 1800000).toISOString(),
  phases: [
    {
      id: "phase-1",
      name: "Lead Research & Qualification",
      description: "Research and qualify incoming leads using multiple data sources",
      assignedAgents: ["crm-specialist"],
      dependencies: [],
      status: "in_progress",
      startTime: new Date(Date.now() - 1800000).toISOString(),
      progress: 68,
      tasks: [
        {
          id: "task-lead-qualification",
          title: "Lead Data Enrichment",
          description: "Enriching 47 leads with company and contact information",
          assignedTo: "crm-specialist",
          status: "in_progress",
          priority: "high",
          estimatedTime: "25 minutes",
          progress: 68,
          dependencies: [],
          outputs: ["47 leads processed", "Company data enriched", "Contact info verified"],
        },
        {
          id: "task-lead-scoring",
          title: "Lead Scoring Analysis",
          description: "Applying ML-based scoring to qualified leads",
          assignedTo: "crm-specialist",
          status: "in_progress",
          priority: "medium",
          estimatedTime: "15 minutes",
          progress: 23,
          dependencies: ["task-lead-qualification"],
        },
      ],
    },
    {
      id: "phase-2",
      name: "Email Campaign Creation",
      description: "Create personalized email campaigns for qualified leads",
      assignedAgents: ["email-specialist"],
      dependencies: ["phase-1"],
      status: "in_progress",
      startTime: new Date(Date.now() - 1200000).toISOString(),
      progress: 45,
      tasks: [
        {
          id: "task-email-templates",
          title: "Personalized Email Templates",
          description: "Creating industry-specific email templates for lead nurturing",
          assignedTo: "email-specialist",
          status: "in_progress",
          priority: "high",
          estimatedTime: "35 minutes",
          progress: 45,
          dependencies: ["task-lead-qualification"],
        },
      ],
    },
  ],
  activeAgents: ["manager", "crm-specialist", "email-specialist"],
  progress: 56,
  totalCost: 5.68,
}

const mockMetrics: SystemMetrics = {
  totalActions: 156,
  activeActions: 8,
  completedToday: 89,
  successRate: 94.2,
  avgExecutionTime: "2m 34s",
  totalCost: 15.67,
  apiCallsToday: 1247,
  tokensUsedToday: 45600,
}

export function LangSmithMonitoring() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [systemPaused, setSystemPaused] = useState(false)

  const handleViewAgent = (agentId: string) => {
    setSelectedAgent(agentId)
  }

  const handleInterruptAgent = (agentId: string, taskId: string) => {
    console.log(`Interrupting agent ${agentId} on task ${taskId}`)
    // This would open an interrupt dialog
  }

  const handlePauseTask = (taskId: string) => {
    console.log(`Pausing task ${taskId}`)
  }

  const handleResumeTask = (taskId: string) => {
    console.log(`Resuming task ${taskId}`)
  }

  const handleSendMessage = (agentId: string) => {
    console.log(`Sending message to agent ${agentId}`)
  }

  const handlePauseAgent = (agentId: string) => {
    console.log(`Pausing agent ${agentId}`)
  }

  const handleSystemPause = () => {
    setSystemPaused(!systemPaused)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Live Workflow Monitoring</h2>
          <p className="text-muted-foreground">Professional execution tracking with real-time visualization</p>
        </div>
        <div className="flex gap-2">
          <Badge variant={systemPaused ? "destructive" : "default"} className="px-3 py-1">
            <div
              className={`w-2 h-2 rounded-full mr-2 ${systemPaused ? "bg-red-500" : "bg-green-500 animate-pulse"}`}
            ></div>
            {systemPaused ? "System Paused" : "Live Monitoring"}
          </Badge>
          <Button variant={systemPaused ? "default" : "destructive"} size="sm" onClick={handleSystemPause}>
            {systemPaused ? (
              <>
                <Play className="w-4 h-4 mr-2" />
                Resume All
              </>
            ) : (
              <>
                <Pause className="w-4 h-4 mr-2" />
                Pause All
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Quick Status Cards */}
      <QuickStatusCards metrics={mockMetrics} />

      {/* Main Monitoring Interface */}
      <Tabs defaultValue="flow-graph" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="flow-graph" className="flex items-center gap-2">
            <Brain className="w-4 h-4" />
            Execution Flow
          </TabsTrigger>
          <TabsTrigger value="active-agents" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Active Agents
          </TabsTrigger>
          <TabsTrigger value="system-health" className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            System Health
          </TabsTrigger>
        </TabsList>

        <TabsContent value="flow-graph">
          <ProfessionalFlowGraph
            workflow={mockWorkflow}
            agents={mockActiveAgents}
            onViewAgent={handleViewAgent}
            onInterruptAgent={handleInterruptAgent}
            onPauseTask={handlePauseTask}
            onResumeTask={handleResumeTask}
          />
        </TabsContent>

        <TabsContent value="active-agents">
          <ActiveAgentsPanel
            activeAgents={mockActiveAgents}
            onViewAgent={handleViewAgent}
            onInterruptAgent={handleInterruptAgent}
            onSendMessage={handleSendMessage}
            onPauseAgent={handlePauseAgent}
          />
        </TabsContent>

        <TabsContent value="system-health">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>System Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-muted-foreground">System health metrics coming soon...</p>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Resource Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-muted-foreground">Resource monitoring coming soon...</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Agent Details Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <AgentDetailsPanel
            agent={mockActiveAgents.find((a) => a.id === selectedAgent)!}
            currentTasks={mockActiveAgents.find((a) => a.id === selectedAgent)?.currentTasks || []}
            onClose={() => setSelectedAgent(null)}
            onInterrupt={handleInterruptAgent}
            onSendMessage={(agentId, message) => console.log(`Message to ${agentId}: ${message}`)}
          />
        </div>
      )}
    </div>
  )
}
