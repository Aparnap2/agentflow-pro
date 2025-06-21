"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { VirtualTeamPanel } from "@/components/ui/virtual-team-panel"
import { IntuitiveChat } from "@/components/ui/intuitive-chat"
import { Building, Users, Settings, MessageSquare, BarChart3 } from "lucide-react"
import type { VirtualAgent, Message } from "@/types/virtual-office"

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
    currentTask: "Analyzing Q1 performance metrics",
    performance: { tasksCompleted: 156, successRate: 94, avgResponseTime: "2.3min" },
  },
  {
    id: "manager",
    name: "Sarah Kim",
    role: "Manager Agent",
    status: "working",
    currentTask: "Coordinating lead qualification workflow",
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
    status: "working",
    currentTask: "Processing 47 new leads",
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
    currentTask: "Creating welcome email sequence",
    avatar: "/placeholder.svg?height=40&width=40",
    personality: "Creative, data-driven, persuasive",
    expertise: ["Email Campaigns", "Marketing Automation", "A/B Testing"],
    workload: 60,
    performance: { tasksCompleted: 127, successRate: 89, avgResponseTime: "2.7min" },
  },
]

const chatMessages: Message[] = [
  {
    id: "1",
    sender: "Alex Chen",
    content:
      "Good morning! I've been reviewing our Q1 performance. Our lead conversion rate has improved by 23% since implementing the automated qualification system.",
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    type: "text",
  },
  {
    id: "2",
    sender: "You",
    content: "That's excellent news, Alex! What do you think we should focus on for Q2?",
    timestamp: new Date(Date.now() - 7000000).toISOString(),
    type: "text",
  },
  {
    id: "3",
    sender: "Alex Chen",
    content:
      "I recommend we expand our email marketing automation and implement social media scheduling. Sarah can coordinate the team to handle both initiatives simultaneously.",
    timestamp: new Date(Date.now() - 6800000).toISOString(),
    type: "text",
  },
  {
    id: "4",
    sender: "Sarah Kim",
    content:
      "I can definitely coordinate that! Mike is currently processing leads efficiently, and Emma has bandwidth for the email expansion. Should I start planning the social media integration?",
    timestamp: new Date(Date.now() - 6600000).toISOString(),
    type: "text",
  },
]

export function VirtualOfficeSection() {
  const [messages, setMessages] = useState<Message[]>(chatMessages)
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

    // Simulate agent response
    setTimeout(() => {
      const responses = [
        "I'll analyze that and get back to you with recommendations.",
        "That's a great point. Let me coordinate with the team on this.",
        "I understand. I'll make sure the team prioritizes this accordingly.",
        "Excellent idea! I'll start working on that right away.",
      ]

      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: activeAgent,
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date().toISOString(),
        type: "text",
      }
      setMessages((prev) => [...prev, agentResponse])
    }, 1500)
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
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 px-3 py-1">
            <BarChart3 className="w-3 h-3 mr-1" />
            {stats.avgSuccessRate}% Success Rate
          </Badge>
          <Button size="sm" className="bg-gradient-to-r from-blue-600 to-purple-600">
            <Settings className="w-4 h-4 mr-2" />
            Configure Office
          </Button>
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
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="workspace" className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            Workspace
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
              <IntuitiveChat
                participants={virtualTeam}
                messages={messages}
                onSendMessage={handleSendMessage}
                activeAgent={activeAgent}
              />
            </div>
            <div>
              <VirtualTeamPanel agents={virtualTeam} />
            </div>
          </div>
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
