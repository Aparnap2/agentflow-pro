"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { Activity, Brain, Clock, DollarSign, MessageSquare, Zap, Eye, Pause, AlertTriangle } from "lucide-react"
import type { VirtualAgent, WorkflowTask } from "@/types/virtual-office"

interface ActiveAgent extends VirtualAgent {
  currentTasks: WorkflowTask[]
  realtimeMetrics: {
    tokensPerMinute: number
    apiCallsPerMinute: number
    costPerHour: number
    currentThinking: string
    lastAction: string
    nextAction: string
  }
}

interface ActiveAgentsPanelProps {
  activeAgents: ActiveAgent[]
  onViewAgent: (agentId: string) => void
  onInterruptAgent: (agentId: string, taskId: string) => void
  onSendMessage: (agentId: string) => void
  onPauseAgent: (agentId: string) => void
}

export function ActiveAgentsPanel({
  activeAgents,
  onViewAgent,
  onInterruptAgent,
  onSendMessage,
  onPauseAgent,
}: ActiveAgentsPanelProps) {
  const getAgentStatusColor = (status: string) => {
    const colors = {
      active: "border-green-500 bg-green-50 dark:bg-green-950",
      working: "border-blue-500 bg-blue-50 dark:bg-blue-950",
      idle: "border-gray-300 bg-gray-50 dark:bg-gray-950",
      waiting_approval: "border-yellow-500 bg-yellow-50 dark:bg-yellow-950",
    }
    return colors[status as keyof typeof colors] || colors.idle
  }

  const getTaskPriorityColor = (priority: string) => {
    const colors = {
      urgent: "bg-red-100 text-red-800 border-red-200",
      high: "bg-orange-100 text-orange-800 border-orange-200",
      medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
      low: "bg-green-100 text-green-800 border-green-200",
    }
    return colors[priority as keyof typeof colors] || colors.medium
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-600" />
          Active Agents ({activeAgents.length})
        </h3>
        <Badge variant="outline" className="bg-blue-50 text-blue-700">
          Real-time Monitoring
        </Badge>
      </div>

      {activeAgents.map((agent) => (
        <Card key={agent.id} className={`border-2 ${getAgentStatusColor(agent.status)}`}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <AgentAvatar agent={agent} size="md" />
                <div>
                  <CardTitle className="text-base">{agent.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">{agent.role}</p>
                  <Badge variant={agent.status === "working" ? "default" : "secondary"} className="mt-1">
                    {agent.status}
                  </Badge>
                </div>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => onViewAgent(agent.id)}>
                  <Eye className="w-3 h-3 mr-1" />
                  Details
                </Button>
                <Button size="sm" variant="outline" onClick={() => onSendMessage(agent.id)}>
                  <MessageSquare className="w-3 h-3 mr-1" />
                  Message
                </Button>
                <Button size="sm" variant="outline" onClick={() => onPauseAgent(agent.id)}>
                  <Pause className="w-3 h-3 mr-1" />
                  Pause
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Current Thinking */}
            <div className="p-3 bg-slate-100 dark:bg-slate-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium">Current Thinking</span>
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
              </div>
              <p className="text-sm text-muted-foreground italic">"{agent.realtimeMetrics.currentThinking}"</p>
            </div>

            {/* Real-time Metrics */}
            <div className="grid grid-cols-4 gap-3">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Brain className="w-3 h-3 text-blue-600" />
                  <span className="text-xs font-medium">Tokens/min</span>
                </div>
                <p className="text-sm font-bold">{agent.realtimeMetrics.tokensPerMinute}</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Activity className="w-3 h-3 text-green-600" />
                  <span className="text-xs font-medium">API/min</span>
                </div>
                <p className="text-sm font-bold">{agent.realtimeMetrics.apiCallsPerMinute}</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <DollarSign className="w-3 h-3 text-orange-600" />
                  <span className="text-xs font-medium">$/hour</span>
                </div>
                <p className="text-sm font-bold">${agent.realtimeMetrics.costPerHour.toFixed(2)}</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Clock className="w-3 h-3 text-purple-600" />
                  <span className="text-xs font-medium">Workload</span>
                </div>
                <p className="text-sm font-bold">{agent.workload}%</p>
              </div>
            </div>

            <Separator />

            {/* Current Tasks */}
            <div>
              <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                <Zap className="w-4 h-4 text-blue-600" />
                Active Tasks ({agent.currentTasks.length})
              </h4>
              <div className="space-y-2">
                {agent.currentTasks.slice(0, 2).map((task) => (
                  <div key={task.id} className="p-2 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">{task.title}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className={`text-xs ${getTaskPriorityColor(task.priority)}`}>
                          {task.priority}
                        </Badge>
                        <Button size="sm" variant="outline" onClick={() => onInterruptAgent(agent.id, task.id)}>
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          Interrupt
                        </Button>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">{task.description}</p>
                    <div className="flex items-center gap-2">
                      <Progress value={task.progress} className="flex-1 h-1" />
                      <span className="text-xs">{task.progress}%</span>
                    </div>
                  </div>
                ))}
                {agent.currentTasks.length > 2 && (
                  <p className="text-xs text-muted-foreground text-center">
                    +{agent.currentTasks.length - 2} more tasks
                  </p>
                )}
              </div>
            </div>

            {/* Action Timeline */}
            <div>
              <h4 className="font-medium text-sm mb-2">Action Timeline</h4>
              <div className="space-y-1 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-muted-foreground">Last:</span>
                  <span>{agent.realtimeMetrics.lastAction}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-muted-foreground">Next:</span>
                  <span>{agent.realtimeMetrics.nextAction}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}

      {activeAgents.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Active Agents</h3>
            <p className="text-muted-foreground">Agents will appear here when they start executing tasks</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
