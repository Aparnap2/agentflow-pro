"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ActionTimeline } from "@/components/ui/action-timeline"
import { OrchestrationBoard } from "@/components/ui/orchestration-board"
import { QuickStatusCards } from "@/components/ui/quick-status-cards"
import { Monitor, Activity, Network, Pause, Play } from "lucide-react"
import type { AgentAction, TaskOrchestration, SystemMetrics, VirtualAgent } from "@/types/virtual-office"

// Mock data
const mockActions: AgentAction[] = [
  {
    id: "action-1",
    agentId: "crm-specialist",
    agentName: "Mike Rodriguez",
    action: "Processing Lead Qualification",
    description: "Analyzing 47 new leads from website form submissions",
    status: "in_progress",
    startTime: new Date(Date.now() - 300000).toISOString(),
    priority: "high",
    progress: 73,
    metadata: {
      toolsUsed: ["HubSpot API", "Email Validator"],
      apiCalls: 47,
      tokensUsed: 12500,
      cost: 0.25,
    },
    childActions: [
      {
        id: "child-1",
        agentId: "crm-specialist",
        agentName: "Mike Rodriguez",
        action: "Email Validation",
        description: "Validating email addresses",
        status: "completed",
        startTime: new Date(Date.now() - 250000).toISOString(),
        priority: "medium",
        progress: 100,
      },
      {
        id: "child-2",
        agentId: "crm-specialist",
        agentName: "Mike Rodriguez",
        action: "Company Research",
        description: "Researching company information",
        status: "in_progress",
        startTime: new Date(Date.now() - 200000).toISOString(),
        priority: "medium",
        progress: 60,
      },
    ],
  },
  {
    id: "action-2",
    agentId: "email-specialist",
    agentName: "Emma Thompson",
    action: "Creating Welcome Email Sequence",
    description: "Designing 5-email welcome series for new subscribers",
    status: "in_progress",
    startTime: new Date(Date.now() - 600000).toISOString(),
    priority: "medium",
    progress: 40,
    metadata: {
      toolsUsed: ["Mailchimp API", "Template Engine"],
      apiCalls: 12,
      tokensUsed: 8500,
      cost: 0.17,
    },
  },
]

const mockOrchestrations: TaskOrchestration[] = [
  {
    id: "orch-1",
    title: "Q1 Lead Generation Campaign",
    description: "Comprehensive lead generation and nurturing campaign for Q1 targets",
    orchestratedBy: "manager",
    status: "executing",
    startTime: new Date(Date.now() - 3600000).toISOString(),
    estimatedCompletion: new Date(Date.now() + 7200000).toISOString(),
    progress: 65,
    parallelActions: mockActions,
    dependencies: ["crm-setup", "email-templates"],
    totalCost: 2.45,
  },
]

const mockMetrics: SystemMetrics = {
  totalActions: 156,
  activeActions: 12,
  completedToday: 89,
  successRate: 94.2,
  avgExecutionTime: "2m 34s",
  totalCost: 15.67,
  apiCallsToday: 1247,
  tokensUsedToday: 45600,
}

const mockAgents: VirtualAgent[] = [
  {
    id: "manager",
    name: "Sarah Kim",
    role: "Manager Agent",
    status: "working",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Organized, detail-oriented",
    expertise: ["Project Management", "Team Coordination"],
    workload: 85,
    performance: { tasksCompleted: 234, successRate: 97, avgResponseTime: "1.8min" },
  },
  {
    id: "crm-specialist",
    name: "Mike Rodriguez",
    role: "CRM Specialist",
    status: "working",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Analytical, systematic",
    expertise: ["Lead Management", "Sales Pipeline"],
    workload: 73,
    performance: { tasksCompleted: 89, successRate: 92, avgResponseTime: "3.1min" },
  },
  {
    id: "email-specialist",
    name: "Emma Thompson",
    role: "Email Marketing Specialist",
    status: "working",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Creative, data-driven",
    expertise: ["Email Campaigns", "Marketing Automation"],
    workload: 60,
    performance: { tasksCompleted: 127, successRate: 89, avgResponseTime: "2.7min" },
  },
]

export function MonitoringDashboard() {
  const [actions, setActions] = useState<AgentAction[]>(mockActions)
  const [orchestrations, setOrchestrations] = useState<TaskOrchestration[]>(mockOrchestrations)
  const [systemPaused, setSystemPaused] = useState(false)

  const handlePauseAction = (actionId: string) => {
    setActions((prev) =>
      prev.map((action) => (action.id === actionId ? { ...action, status: "paused" as const } : action)),
    )
  }

  const handleCancelAction = (actionId: string) => {
    setActions((prev) =>
      prev.map((action) => (action.id === actionId ? { ...action, status: "cancelled" as const } : action)),
    )
  }

  const handleResumeAction = (actionId: string) => {
    setActions((prev) =>
      prev.map((action) => (action.id === actionId ? { ...action, status: "in_progress" as const } : action)),
    )
  }

  const handlePauseOrchestration = (id: string) => {
    setOrchestrations((prev) => prev.map((orch) => (orch.id === id ? { ...orch, status: "paused" as const } : orch)))
  }

  const handleCancelOrchestration = (id: string) => {
    setOrchestrations((prev) => prev.map((orch) => (orch.id === id ? { ...orch, status: "cancelled" as const } : orch)))
  }

  const handleResumeOrchestration = (id: string) => {
    setOrchestrations((prev) => prev.map((orch) => (orch.id === id ? { ...orch, status: "executing" as const } : orch)))
  }

  const handleSystemPause = () => {
    setSystemPaused(!systemPaused)
    // In real implementation, this would pause all active actions
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Real-Time Monitoring</h2>
          <p className="text-muted-foreground">Monitor every action your virtual team is performing</p>
        </div>
        <div className="flex gap-2">
          <Badge variant={systemPaused ? "destructive" : "default"} className="px-3 py-1">
            <div
              className={`w-2 h-2 rounded-full mr-2 ${systemPaused ? "bg-red-500" : "bg-green-500 animate-pulse"}`}
            ></div>
            {systemPaused ? "System Paused" : "System Active"}
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

      {/* Monitoring Tabs */}
      <Tabs defaultValue="live-actions" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="live-actions" className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Live Actions
          </TabsTrigger>
          <TabsTrigger value="orchestration" className="flex items-center gap-2">
            <Network className="w-4 h-4" />
            Orchestration
          </TabsTrigger>
          <TabsTrigger value="system-health" className="flex items-center gap-2">
            <Monitor className="w-4 h-4" />
            System Health
          </TabsTrigger>
        </TabsList>

        <TabsContent value="live-actions">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Live Agent Actions
                <Badge variant="secondary">{actions.filter((a) => a.status === "in_progress").length} active</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ActionTimeline
                actions={actions}
                agents={mockAgents}
                onPauseAction={handlePauseAction}
                onCancelAction={handleCancelAction}
                onResumeAction={handleResumeAction}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="orchestration">
          <OrchestrationBoard
            orchestrations={orchestrations}
            agents={mockAgents}
            onPauseOrchestration={handlePauseOrchestration}
            onCancelOrchestration={handleCancelOrchestration}
            onResumeOrchestration={handleResumeOrchestration}
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
    </div>
  )
}
