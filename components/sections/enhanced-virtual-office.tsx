"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { VirtualTeamPanel } from "@/components/ui/virtual-team-panel"
import { EnhancedChat } from "@/components/ui/enhanced-chat"
import { WorkflowGraph } from "@/components/ui/workflow-graph"
import { AgentDetailsPanel } from "@/components/ui/agent-details-panel"
import { Building, Users, Settings, MessageSquare, BarChart3, Network } from "lucide-react"
import type { VirtualAgent, Message } from "@/types/virtual-office"
import type { ResearchPlan, WorkflowExecution } from "@/types/workflow"

// Mock data
const virtualTeam: VirtualAgent[] = [
  {
    id: "cofounder",
    name: "Alex Chen",
    role: "Co-Founder Agent",
    status: "active",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Strategic, visionary, collaborative, deeply analytical",
    expertise: ["Business Strategy", "Market Research", "Competitive Analysis", "Strategic Planning"],
    workload: 75,
    currentTask: "Researching Q2 growth strategy",
    performance: { tasksCompleted: 156, successRate: 94, avgResponseTime: "2.3min" },
  },
  {
    id: "manager",
    name: "Sarah Kim",
    role: "Manager Agent",
    status: "working",
    currentTask: "Orchestrating lead generation workflow",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Organized, detail-oriented, diplomatic, excellent coordinator",
    expertise: ["Project Management", "Team Coordination", "Process Optimization", "Workflow Design"],
    workload: 85,
    performance: { tasksCompleted: 234, successRate: 97, avgResponseTime: "1.8min" },
  },
  {
    id: "crm-specialist",
    name: "Mike Rodriguez",
    role: "CRM Specialist",
    status: "working",
    currentTask: "Processing qualified leads",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Analytical, customer-focused, systematic",
    expertise: ["Lead Management", "Sales Pipeline", "Customer Segmentation"],
    workload: 73,
    performance: { tasksCompleted: 89, successRate: 92, avgResponseTime: "3.1min" },
  },
  {
    id: "email-specialist",
    name: "Emma Thompson",
    role: "Email Marketing Specialist",
    status: "working",
    currentTask: "Creating nurture sequences",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Creative, data-driven, persuasive",
    expertise: ["Email Campaigns", "Marketing Automation", "A/B Testing"],
    workload: 60,
    performance: { tasksCompleted: 127, successRate: 89, avgResponseTime: "2.7min" },
  },
]

const initialMessages: Message[] = [
  {
    id: "1",
    sender: "Alex Chen",
    content:
      "Good morning! I'm ready to help you research and plan strategic initiatives. What would you like me to analyze today?",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    type: "text",
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
      status: "completed",
      startTime: new Date(Date.now() - 1800000).toISOString(),
      endTime: new Date(Date.now() - 1200000).toISOString(),
      progress: 100,
      tasks: [
        {
          id: "task-1",
          title: "Lead Data Enrichment",
          description: "Enrich lead data with company information",
          assignedTo: "crm-specialist",
          status: "completed",
          priority: "high",
          estimatedTime: "30 minutes",
          actualTime: "25 minutes",
          progress: 100,
          dependencies: [],
          outputs: ["47 leads enriched", "Company data added"],
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
      progress: 65,
      tasks: [
        {
          id: "task-2",
          title: "Personalized Email Templates",
          description: "Create industry-specific email templates",
          assignedTo: "email-specialist",
          status: "in_progress",
          priority: "high",
          estimatedTime: "45 minutes",
          progress: 65,
          dependencies: ["task-1"],
        },
      ],
    },
  ],
  activeAgents: ["email-specialist"],
  progress: 75,
  totalCost: 3.45,
}

export function EnhancedVirtualOffice() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [pendingApprovals, setPendingApprovals] = useState<ResearchPlan[]>([])
  const [activeWorkflow, setActiveWorkflow] = useState<WorkflowExecution | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [activeAgent, setActiveAgent] = useState<string>("Alex Chen")

  const handleSendMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      content,
      timestamp: new Date().toISOString(),
      type: "text",
    }
    setMessages((prev) => [...prev, newMessage])

    // Simulate Co-Founder research and plan generation
    setTimeout(() => {
      setActiveAgent("Alex Chen")
      const researchMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "Alex Chen",
        content:
          "I'm conducting deep research on your request. Let me analyze market data, competitor strategies, and create a comprehensive plan...",
        timestamp: new Date().toISOString(),
        type: "text",
      }
      setMessages((prev) => [...prev, researchMessage])

      // Generate research plan after "research"
      setTimeout(() => {
        const plan: ResearchPlan = {
          id: `plan-${Date.now()}`,
          title: "Q2 Growth Strategy Implementation",
          description: "Comprehensive plan to accelerate growth through automated lead generation and nurturing",
          researchFindings: [
            "Market analysis shows 34% increase in demand for our target segment",
            "Competitors are underutilizing email automation (67% opportunity gap)",
            "Lead qualification can be improved by 45% with better data enrichment",
            "Customer acquisition cost can be reduced by 28% through better targeting",
          ],
          proposedActions: [
            "Implement advanced lead scoring system with 12 data points",
            "Create industry-specific email nurture sequences",
            "Set up automated competitor monitoring",
            "Deploy social proof collection system",
          ],
          expectedOutcomes: [
            "40% increase in qualified leads",
            "25% improvement in conversion rates",
            "30% reduction in manual work",
            "ROI improvement of 150%",
          ],
          timeline: "3-4 weeks",
          resources: ["CRM integration", "Email platform", "Data enrichment tools"],
          risks: ["Data quality issues", "Integration complexity", "Team adoption"],
          budget: 8500,
          priority: "high",
          createdBy: "cofounder",
          createdAt: new Date().toISOString(),
          status: "pending_approval",
        }

        setPendingApprovals((prev) => [...prev, plan])

        const planMessage: Message = {
          id: (Date.now() + 2).toString(),
          sender: "Alex Chen",
          content:
            "I've completed my research and created a detailed strategic plan. Please review the plan above and let me know if you'd like me to proceed with execution.",
          timestamp: new Date().toISOString(),
          type: "text",
        }
        setMessages((prev) => [...prev, planMessage])
      }, 3000)
    }, 1500)
  }

  const handleApprovePlan = (planId: string) => {
    const plan = pendingApprovals.find((p) => p.id === planId)
    if (!plan) return

    setPendingApprovals((prev) => prev.filter((p) => p.id !== planId))

    // Co-Founder triggers Manager
    const approvalMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      content: "Plan approved! Please proceed with execution.",
      timestamp: new Date().toISOString(),
      type: "text",
    }
    setMessages((prev) => [...prev, approvalMessage])

    setTimeout(() => {
      const cofounderMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "Alex Chen",
        content:
          "Excellent! I'm now briefing Sarah (Manager Agent) with the detailed plan and architecture. She'll coordinate the specialist agents to execute this strategy.",
        timestamp: new Date().toISOString(),
        type: "text",
      }
      setMessages((prev) => [...prev, cofounderMessage])

      setTimeout(() => {
        const managerMessage: Message = {
          id: (Date.now() + 2).toString(),
          sender: "Sarah Kim",
          content:
            "I've received the strategic plan from Alex. I'm now orchestrating the execution across our specialist agents. You can monitor the progress in the Live Monitoring tab.",
          timestamp: new Date().toISOString(),
          type: "text",
        }
        setMessages((prev) => [...prev, managerMessage])

        // Set active workflow
        setActiveWorkflow(mockWorkflow)
      }, 2000)
    }, 1500)
  }

  const handleRejectPlan = (planId: string) => {
    setPendingApprovals((prev) => prev.filter((p) => p.id !== planId))

    const rejectionMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      content: "Plan rejected. Please revise the approach.",
      timestamp: new Date().toISOString(),
      type: "text",
    }
    setMessages((prev) => [...prev, rejectionMessage])
  }

  const handleViewAgentDetails = (agentId: string) => {
    setSelectedAgent(agentId)
  }

  const handleInterruptAgent = (agentId: string, taskId: string, instructions: string) => {
    const interruptMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      content: `Interrupting ${virtualTeam.find((a) => a.id === agentId)?.name} with new instructions: ${instructions}`,
      timestamp: new Date().toISOString(),
      type: "text",
    }
    setMessages((prev) => [...prev, interruptMessage])

    setTimeout(() => {
      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: virtualTeam.find((a) => a.id === agentId)?.name || "Agent",
        content: "Understood! I'm adjusting my approach based on your new instructions.",
        timestamp: new Date().toISOString(),
        type: "text",
      }
      setMessages((prev) => [...prev, agentResponse])
    }, 1000)

    setSelectedAgent(null)
  }

  const handleSendDirectMessage = (agentId: string, message: string) => {
    const directMessage: Message = {
      id: Date.now().toString(),
      sender: "You",
      content: `@${virtualTeam.find((a) => a.id === agentId)?.name}: ${message}`,
      timestamp: new Date().toISOString(),
      type: "text",
    }
    setMessages((prev) => [...prev, directMessage])
  }

  const stats = {
    activeMembers: virtualTeam.filter((a) => a.status === "active" || a.status === "working").length,
    totalTasks: virtualTeam.reduce((sum, agent) => sum + agent.performance.tasksCompleted, 0),
    avgWorkload: Math.round(virtualTeam.reduce((sum, agent) => sum + agent.workload, 0) / virtualTeam.length),
    avgSuccessRate: Math.round(
      virtualTeam.reduce((sum, agent) => sum + agent.performance.successRate, 0) / virtualTeam.length,
    ),
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Virtual Office</h2>
          <p className="text-muted-foreground">Your AI-powered virtual team workspace</p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 px-3 py-1">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            {stats.activeMembers} Active
          </Badge>
          {pendingApprovals.length > 0 && (
            <Badge variant="destructive" className="px-3 py-1">
              {pendingApprovals.length} Pending Approval
            </Badge>
          )}
          {activeWorkflow && (
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 px-3 py-1">
              <Network className="w-3 h-3 mr-1" />
              Workflow Active
            </Badge>
          )}
        </div>
      </div>

      {/* Office Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 border-blue-200">
          <CardContent className="p-4 text-center">
            <Users className="w-6 h-6 text-blue-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{stats.activeMembers}</p>
            <p className="text-xs text-blue-700 dark:text-blue-300">Active Team Members</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900 border-green-200">
          <CardContent className="p-4 text-center">
            <BarChart3 className="w-6 h-6 text-green-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-green-900 dark:text-green-100">{stats.totalTasks}</p>
            <p className="text-xs text-green-700 dark:text-green-300">Total Tasks Completed</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 border-purple-200">
          <CardContent className="p-4 text-center">
            <Building className="w-6 h-6 text-purple-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">{stats.avgWorkload}%</p>
            <p className="text-xs text-purple-700 dark:text-purple-300">Average Workload</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900 border-orange-200">
          <CardContent className="p-4 text-center">
            <MessageSquare className="w-6 h-6 text-orange-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-orange-900 dark:text-orange-100">{messages.length}</p>
            <p className="text-xs text-orange-700 dark:text-orange-300">Messages Today</p>
          </CardContent>
        </Card>
      </div>

      {/* Office Workspace */}
      <Tabs defaultValue="workspace" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="workspace" className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            Workspace
          </TabsTrigger>
          <TabsTrigger value="workflow" className="flex items-center gap-2">
            <Network className="w-4 h-4" />
            Active Workflow
          </TabsTrigger>
          <TabsTrigger value="team-details" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Team Details
          </TabsTrigger>
          <TabsTrigger value="office-config" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Configuration
          </TabsTrigger>
        </TabsList>

        <TabsContent value="workspace">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <EnhancedChat
                participants={virtualTeam}
                messages={messages}
                pendingApprovals={pendingApprovals}
                onSendMessage={handleSendMessage}
                onApprovePlan={handleApprovePlan}
                onRejectPlan={handleRejectPlan}
                activeAgent={activeAgent}
              />
            </div>
            <div>
              <VirtualTeamPanel agents={virtualTeam} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="workflow">
          {activeWorkflow ? (
            <div className="space-y-6">
              <WorkflowGraph
                workflow={activeWorkflow}
                agents={virtualTeam}
                onViewAgentDetails={handleViewAgentDetails}
                onInterruptAgent={(agentId, taskId) => handleViewAgentDetails(agentId)}
              />

              {selectedAgent && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                  <AgentDetailsPanel
                    agent={virtualTeam.find((a) => a.id === selectedAgent)!}
                    currentTasks={activeWorkflow.phases
                      .flatMap((p) => p.tasks)
                      .filter((t) => t.assignedTo === selectedAgent)}
                    onClose={() => setSelectedAgent(null)}
                    onInterrupt={handleInterruptAgent}
                    onSendMessage={handleSendDirectMessage}
                  />
                </div>
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Network className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Active Workflow</h3>
                <p className="text-muted-foreground">
                  Ask your Co-Founder Agent to research and plan a strategy to see workflow execution here.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="team-details">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {virtualTeam.map((agent) => (
              <Card key={agent.id} className="hover:shadow-lg transition-all">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                      {agent.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{agent.name}</CardTitle>
                      <p className="text-sm text-muted-foreground">{agent.role}</p>
                    </div>
                    <Badge variant={agent.status === "active" ? "default" : "secondary"} className="ml-auto">
                      {agent.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium mb-1">Personality</p>
                      <p className="text-sm text-muted-foreground">{agent.personality}</p>
                    </div>

                    <div>
                      <p className="text-sm font-medium mb-2">Expertise</p>
                      <div className="flex flex-wrap gap-1">
                        {agent.expertise.map((skill) => (
                          <Badge key={skill} variant="outline" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {agent.currentTask && (
                      <div>
                        <p className="text-sm font-medium mb-1">Current Task</p>
                        <p className="text-sm text-muted-foreground">{agent.currentTask}</p>
                      </div>
                    )}

                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <p className="text-lg font-bold text-blue-600">{agent.performance.tasksCompleted}</p>
                        <p className="text-xs text-muted-foreground">Tasks</p>
                      </div>
                      <div>
                        <p className="text-lg font-bold text-green-600">{agent.performance.successRate}%</p>
                        <p className="text-xs text-muted-foreground">Success</p>
                      </div>
                      <div>
                        <p className="text-lg font-bold text-purple-600">{agent.performance.avgResponseTime}</p>
                        <p className="text-xs text-muted-foreground">Avg Time</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="office-config">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Office Configuration</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Configure your virtual office settings and team behavior
                </p>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-muted-foreground">Office configuration interface coming soon...</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
