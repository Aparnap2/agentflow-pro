"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { Play, Pause, Clock, CheckCircle, AlertTriangle, Zap, Eye } from "lucide-react"
import type { WorkflowExecution, VirtualAgent } from "@/types/virtual-office"

interface FlowNode {
  id: string
  type: "agent" | "task" | "decision" | "parallel" | "merge"
  agentId?: string
  taskId?: string
  title: string
  description: string
  status: "pending" | "running" | "completed" | "failed" | "paused"
  startTime?: string
  endTime?: string
  duration?: string
  progress: number
  children: string[]
  parents: string[]
  position: { x: number; y: number }
  metadata?: {
    tokensUsed?: number
    cost?: number
    apiCalls?: number
    outputs?: string[]
  }
}

interface LangSmithFlowGraphProps {
  workflow: WorkflowExecution
  agents: VirtualAgent[]
  onViewAgent: (agentId: string) => void
  onInterruptAgent: (agentId: string, taskId: string) => void
  onPauseTask: (taskId: string) => void
  onResumeTask: (taskId: string) => void
}

export function LangSmithFlowGraph({
  workflow,
  agents,
  onViewAgent,
  onInterruptAgent,
  onPauseTask,
  onResumeTask,
}: LangSmithFlowGraphProps) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [flowNodes, setFlowNodes] = useState<FlowNode[]>([])

  // Generate flow nodes from workflow data
  useEffect(() => {
    const nodes: FlowNode[] = []
    let yPosition = 100

    // Manager orchestration node
    nodes.push({
      id: "manager-start",
      type: "agent",
      agentId: workflow.orchestratedBy,
      title: "Manager Orchestration",
      description: "Analyzing plan and coordinating execution",
      status: "running",
      progress: 100,
      children: workflow.phases.map((p) => `phase-${p.id}`),
      parents: [],
      position: { x: 400, y: yPosition },
      metadata: {
        tokensUsed: 2500,
        cost: 0.05,
        apiCalls: 3,
      },
    })

    yPosition += 150

    // Phase nodes
    workflow.phases.forEach((phase, phaseIndex) => {
      const phaseNodeId = `phase-${phase.id}`

      // Phase header node
      nodes.push({
        id: phaseNodeId,
        type: "decision",
        title: `Phase ${phaseIndex + 1}: ${phase.name}`,
        description: phase.description,
        status: phase.status === "in_progress" ? "running" : phase.status === "completed" ? "completed" : "pending",
        progress: phase.progress,
        children: phase.tasks.map((t) => `task-${t.id}`),
        parents: phaseIndex === 0 ? ["manager-start"] : [`phase-${workflow.phases[phaseIndex - 1].id}`],
        position: { x: 400, y: yPosition },
        startTime: phase.startTime,
        endTime: phase.endTime,
      })

      yPosition += 100

      // Task nodes for this phase
      const tasksInParallel = phase.tasks.length > 1
      const taskStartX = tasksInParallel ? 200 : 400
      const taskSpacing = tasksInParallel ? 400 : 0

      phase.tasks.forEach((task, taskIndex) => {
        const taskNodeId = `task-${task.id}`
        const agent = agents.find((a) => a.id === task.assignedTo)

        nodes.push({
          id: taskNodeId,
          type: "task",
          agentId: task.assignedTo,
          taskId: task.id,
          title: task.title,
          description: task.description,
          status:
            task.status === "in_progress"
              ? "running"
              : task.status === "completed"
                ? "completed"
                : task.status === "failed"
                  ? "failed"
                  : task.status === "paused"
                    ? "paused"
                    : "pending",
          progress: task.progress,
          children: [],
          parents: [phaseNodeId],
          position: {
            x: taskStartX + taskIndex * taskSpacing,
            y: yPosition,
          },
          metadata: {
            tokensUsed: Math.floor(Math.random() * 5000) + 1000,
            cost: Math.random() * 0.5 + 0.1,
            apiCalls: Math.floor(Math.random() * 10) + 2,
            outputs: task.outputs,
          },
        })
      })

      yPosition += 150
    })

    setFlowNodes(nodes)
  }, [workflow, agents])

  const getNodeStatusColor = (status: string) => {
    const colors = {
      pending: "border-gray-300 bg-gray-50",
      running: "border-blue-500 bg-blue-50 shadow-lg shadow-blue-200",
      completed: "border-green-500 bg-green-50",
      failed: "border-red-500 bg-red-50",
      paused: "border-yellow-500 bg-yellow-50",
    }
    return colors[status as keyof typeof colors] || colors.pending
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <Play className="w-4 h-4 text-blue-600 animate-pulse" />
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case "failed":
        return <AlertTriangle className="w-4 h-4 text-red-600" />
      case "paused":
        return <Pause className="w-4 h-4 text-yellow-600" />
      default:
        return <Clock className="w-4 h-4 text-gray-600" />
    }
  }

  const getAgentById = (id: string) => agents.find((a) => a.id === id)

  const renderConnections = () => {
    return flowNodes.flatMap((node) =>
      node.children.map((childId) => {
        const childNode = flowNodes.find((n) => n.id === childId)
        if (!childNode) return null

        const startX = node.position.x + 150 // Node width / 2
        const startY = node.position.y + 40 // Node height
        const endX = childNode.position.x + 150
        const endY = childNode.position.y

        return (
          <svg
            key={`${node.id}-${childId}`}
            className="absolute pointer-events-none"
            style={{
              left: Math.min(startX, endX) - 10,
              top: Math.min(startY, endY) - 10,
              width: Math.abs(endX - startX) + 20,
              height: Math.abs(endY - startY) + 20,
            }}
          >
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280" />
              </marker>
            </defs>
            <line
              x1={startX - Math.min(startX, endX) + 10}
              y1={startY - Math.min(startY, endY) + 10}
              x2={endX - Math.min(startX, endX) + 10}
              y2={endY - Math.min(startY, endY) + 10}
              stroke="#6b7280"
              strokeWidth="2"
              markerEnd="url(#arrowhead)"
              className={node.status === "running" ? "animate-pulse" : ""}
            />
          </svg>
        )
      }),
    )
  }

  return (
    <Card className="h-[800px] overflow-hidden">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-blue-600" />
          Live Workflow Execution Graph
          <Badge variant="secondary">{workflow.status}</Badge>
          <Badge variant="outline" className="ml-auto">
            {flowNodes.filter((n) => n.status === "running").length} Active
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 h-full">
        <div className="relative h-full overflow-auto bg-slate-50 dark:bg-slate-900">
          {/* Render connections first (behind nodes) */}
          {renderConnections()}

          {/* Render nodes */}
          {flowNodes.map((node) => {
            const agent = node.agentId ? getAgentById(node.agentId) : null
            const isSelected = selectedNode === node.id

            return (
              <div
                key={node.id}
                className={`absolute w-80 cursor-pointer transition-all duration-200 ${
                  isSelected ? "z-20 scale-105" : "z-10"
                }`}
                style={{
                  left: node.position.x,
                  top: node.position.y,
                }}
                onClick={() => setSelectedNode(isSelected ? null : node.id)}
              >
                <Card
                  className={`border-2 ${getNodeStatusColor(node.status)} ${isSelected ? "ring-2 ring-blue-500" : ""}`}
                >
                  <CardContent className="p-4">
                    {/* Node Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(node.status)}
                        {agent && <AgentAvatar agent={agent} size="sm" showStatus={false} />}
                        <div>
                          <h4 className="font-semibold text-sm">{node.title}</h4>
                          <p className="text-xs text-muted-foreground">{node.description}</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {node.type}
                      </Badge>
                    </div>

                    {/* Progress Bar */}
                    {node.status === "running" && (
                      <div className="mb-3">
                        <div className="flex justify-between text-xs mb-1">
                          <span>Progress</span>
                          <span>{node.progress}%</span>
                        </div>
                        <Progress value={node.progress} className="h-2" />
                      </div>
                    )}

                    {/* Metadata */}
                    {node.metadata && (
                      <div className="grid grid-cols-3 gap-2 mb-3 text-xs">
                        {node.metadata.tokensUsed && (
                          <div className="text-center">
                            <p className="font-medium">{node.metadata.tokensUsed.toLocaleString()}</p>
                            <p className="text-muted-foreground">Tokens</p>
                          </div>
                        )}
                        {node.metadata.cost && (
                          <div className="text-center">
                            <p className="font-medium">${node.metadata.cost.toFixed(3)}</p>
                            <p className="text-muted-foreground">Cost</p>
                          </div>
                        )}
                        {node.metadata.apiCalls && (
                          <div className="text-center">
                            <p className="font-medium">{node.metadata.apiCalls}</p>
                            <p className="text-muted-foreground">API Calls</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Timing */}
                    {node.startTime && (
                      <div className="text-xs text-muted-foreground mb-3">
                        Started: {new Date(node.startTime).toLocaleTimeString()}
                        {node.endTime && <span> • Completed: {new Date(node.endTime).toLocaleTimeString()}</span>}
                      </div>
                    )}

                    {/* Outputs */}
                    {node.metadata?.outputs && node.metadata.outputs.length > 0 && (
                      <div className="mb-3">
                        <p className="text-xs font-medium mb-1">Outputs:</p>
                        <div className="flex flex-wrap gap-1">
                          {node.metadata.outputs.slice(0, 2).map((output, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {output}
                            </Badge>
                          ))}
                          {node.metadata.outputs.length > 2 && (
                            <Badge variant="outline" className="text-xs">
                              +{node.metadata.outputs.length - 2} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-2">
                      {node.agentId && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation()
                            onViewAgent(node.agentId!)
                          }}
                        >
                          <Eye className="w-3 h-3 mr-1" />
                          View Agent
                        </Button>
                      )}

                      {node.status === "running" && node.taskId && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation()
                              onPauseTask(node.taskId!)
                            }}
                          >
                            <Pause className="w-3 h-3 mr-1" />
                            Pause
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={(e) => {
                              e.stopPropagation()
                              if (node.agentId && node.taskId) {
                                onInterruptAgent(node.agentId, node.taskId)
                              }
                            }}
                          >
                            <Zap className="w-3 h-3 mr-1" />
                            Interrupt
                          </Button>
                        </>
                      )}

                      {node.status === "paused" && node.taskId && (
                        <Button
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            onResumeTask(node.taskId!)
                          }}
                        >
                          <Play className="w-3 h-3 mr-1" />
                          Resume
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )
          })}

          {/* Legend */}
          <div className="absolute top-4 right-4 bg-white dark:bg-slate-800 p-4 rounded-lg border shadow-lg">
            <h4 className="font-semibold text-sm mb-2">Status Legend</h4>
            <div className="space-y-1 text-xs">
              <div className="flex items-center gap-2">
                <Play className="w-3 h-3 text-blue-600" />
                <span>Running</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-3 h-3 text-green-600" />
                <span>Completed</span>
              </div>
              <div className="flex items-center gap-2">
                <Pause className="w-3 h-3 text-yellow-600" />
                <span>Paused</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-3 h-3 text-gray-600" />
                <span>Pending</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
