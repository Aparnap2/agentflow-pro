"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { Network, Play, Pause, AlertCircle, CheckCircle } from "lucide-react"
import type { WorkflowExecution, VirtualAgent } from "@/types/virtual-office"

interface WorkflowGraphProps {
  workflow: WorkflowExecution
  agents: VirtualAgent[]
  onViewAgentDetails: (agentId: string) => void
  onInterruptAgent: (agentId: string, taskId: string) => void
}

export function WorkflowGraph({ workflow, agents, onViewAgentDetails, onInterruptAgent }: WorkflowGraphProps) {
  const getAgentById = (id: string) => agents.find((agent) => agent.id === id)
  const manager = getAgentById(workflow.orchestratedBy)

  const getPhaseStatusColor = (status: string) => {
    const colors = {
      pending: "bg-gray-100 border-gray-300",
      in_progress: "bg-blue-100 border-blue-300",
      completed: "bg-green-100 border-green-300",
      blocked: "bg-red-100 border-red-300",
    }
    return colors[status as keyof typeof colors] || colors.pending
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case "in_progress":
        return <Play className="w-4 h-4 text-blue-600" />
      case "blocked":
        return <AlertCircle className="w-4 h-4 text-red-600" />
      default:
        return <Pause className="w-4 h-4 text-gray-600" />
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Network className="w-5 h-5" />
          Workflow Execution Graph
          <Badge variant="secondary">{workflow.status}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Manager Orchestration */}
          <div className="text-center">
            <div className="inline-flex items-center gap-3 p-4 bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-900 dark:to-indigo-900 rounded-lg border-2 border-purple-200">
              {manager && <AgentAvatar agent={manager} size="md" />}
              <div>
                <h4 className="font-semibold">{manager?.name} (Manager)</h4>
                <p className="text-sm text-muted-foreground">Orchestrating Workflow</p>
                <Progress value={workflow.progress} className="w-32 h-2 mt-2" />
              </div>
            </div>
          </div>

          {/* Workflow Phases */}
          <div className="space-y-4">
            {workflow.phases.map((phase, phaseIndex) => (
              <div key={phase.id} className="space-y-3">
                <div className={`p-4 rounded-lg border-2 ${getPhaseStatusColor(phase.status)}`}>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(phase.status)}
                      <h5 className="font-semibold">
                        Phase {phaseIndex + 1}: {phase.name}
                      </h5>
                    </div>
                    <Badge variant="outline">{phase.status.replace("_", " ")}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{phase.description}</p>

                  <div className="mb-3">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Phase Progress</span>
                      <span>{phase.progress}%</span>
                    </div>
                    <Progress value={phase.progress} className="h-2" />
                  </div>

                  {/* Assigned Agents */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {phase.assignedAgents.map((agentId) => {
                      const agent = getAgentById(agentId)
                      if (!agent) return null

                      return (
                        <div
                          key={agentId}
                          className="flex items-center gap-2 p-2 bg-white dark:bg-slate-800 rounded border cursor-pointer hover:shadow-md transition-all"
                          onClick={() => onViewAgentDetails(agentId)}
                        >
                          <AgentAvatar agent={agent} size="sm" />
                          <div>
                            <p className="text-xs font-medium">{agent.name}</p>
                            <p className="text-xs text-muted-foreground">{agent.role}</p>
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            className="ml-2"
                            onClick={(e) => {
                              e.stopPropagation()
                              // Find active task for this agent in this phase
                              const activeTask = phase.tasks.find(
                                (task) => task.assignedTo === agentId && task.status === "in_progress",
                              )
                              if (activeTask) {
                                onInterruptAgent(agentId, activeTask.id)
                              }
                            }}
                          >
                            Interrupt
                          </Button>
                        </div>
                      )
                    })}
                  </div>

                  {/* Phase Tasks */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {phase.tasks.map((task) => {
                      const assignedAgent = getAgentById(task.assignedTo)
                      return (
                        <div key={task.id} className="p-2 bg-white dark:bg-slate-800 rounded border text-xs">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">{task.title}</span>
                            <Badge variant="outline" className="text-xs">
                              {task.status.replace("_", " ")}
                            </Badge>
                          </div>
                          <p className="text-muted-foreground mb-2">{task.description}</p>
                          <div className="flex items-center gap-2">
                            {assignedAgent && <AgentAvatar agent={assignedAgent} size="sm" showStatus={false} />}
                            <div className="flex-1">
                              <Progress value={task.progress} className="h-1" />
                            </div>
                            <span className="text-xs">{task.progress}%</span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Connection Line to Next Phase */}
                {phaseIndex < workflow.phases.length - 1 && (
                  <div className="flex justify-center">
                    <div className="w-px h-8 bg-gray-300"></div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Workflow Summary */}
          <div className="grid grid-cols-3 gap-4 text-center p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <div>
              <p className="text-lg font-bold text-blue-600">{workflow.progress}%</p>
              <p className="text-xs text-muted-foreground">Overall Progress</p>
            </div>
            <div>
              <p className="text-lg font-bold text-green-600">{workflow.activeAgents.length}</p>
              <p className="text-xs text-muted-foreground">Active Agents</p>
            </div>
            <div>
              <p className="text-lg font-bold text-purple-600">${workflow.totalCost.toFixed(2)}</p>
              <p className="text-xs text-muted-foreground">Total Cost</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
