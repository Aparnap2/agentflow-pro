"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { Pause, Clock, CheckCircle, AlertTriangle, Zap, Eye, Brain, Activity } from "lucide-react"
import type { WorkflowExecution, VirtualAgent } from "@/types/virtual-office"

interface FlowNode {
  id: string
  type: "start" | "agent" | "task" | "decision" | "end"
  agentId?: string
  taskId?: string
  title: string
  subtitle?: string
  status: "pending" | "running" | "completed" | "failed" | "paused"
  progress: number
  children: string[]
  level: number
  metadata?: {
    tokensUsed?: number
    cost?: number
    duration?: string
    outputs?: string[]
  }
}

interface ProfessionalFlowGraphProps {
  workflow: WorkflowExecution
  agents: VirtualAgent[]
  onViewAgent: (agentId: string) => void
  onInterruptAgent: (agentId: string, taskId: string) => void
  onPauseTask: (taskId: string) => void
  onResumeTask: (taskId: string) => void
}

export function ProfessionalFlowGraph({
  workflow,
  agents,
  onViewAgent,
  onInterruptAgent,
  onPauseTask,
  onResumeTask,
}: ProfessionalFlowGraphProps) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const svgRef = useRef<SVGSVGElement>(null)

  // Generate clean flow structure
  const generateFlowNodes = (): FlowNode[] => {
    const nodes: FlowNode[] = []

    // Start node
    nodes.push({
      id: "start",
      type: "start",
      title: "Workflow Started",
      subtitle: "Manager orchestrating execution",
      status: "completed",
      progress: 100,
      children: workflow.phases.map((p) => `phase-${p.id}`),
      level: 0,
    })

    // Phase and task nodes
    workflow.phases.forEach((phase, phaseIndex) => {
      // Phase decision node
      nodes.push({
        id: `phase-${phase.id}`,
        type: "decision",
        title: phase.name,
        subtitle: `Phase ${phaseIndex + 1}`,
        status: phase.status === "in_progress" ? "running" : phase.status === "completed" ? "completed" : "pending",
        progress: phase.progress,
        children: phase.tasks.map((t) => `task-${t.id}`),
        level: phaseIndex + 1,
      })

      // Task nodes
      phase.tasks.forEach((task) => {
        const agent = agents.find((a) => a.id === task.assignedTo)
        nodes.push({
          id: `task-${task.id}`,
          type: "task",
          agentId: task.assignedTo,
          taskId: task.id,
          title: task.title,
          subtitle: agent?.name,
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
          level: phaseIndex + 2,
          metadata: {
            tokensUsed: Math.floor(Math.random() * 5000) + 1000,
            cost: Math.random() * 0.5 + 0.1,
            duration: task.status === "completed" ? "2m 34s" : undefined,
            outputs: task.outputs,
          },
        })
      })
    })

    return nodes
  }

  const [flowNodes, setFlowNodes] = useState<FlowNode[]>([])

  useEffect(() => {
    setFlowNodes(generateFlowNodes())
  }, [workflow, agents])

  const getNodeColor = (status: string, isHovered = false) => {
    const baseColors = {
      pending: { bg: "#f8fafc", border: "#e2e8f0", text: "#64748b" },
      running: { bg: "#dbeafe", border: "#3b82f6", text: "#1e40af" },
      completed: { bg: "#dcfce7", border: "#22c55e", text: "#15803d" },
      failed: { bg: "#fee2e2", border: "#ef4444", text: "#dc2626" },
      paused: { bg: "#fef3c7", border: "#f59e0b", text: "#d97706" },
    }

    const colors = baseColors[status as keyof typeof baseColors] || baseColors.pending
    return {
      ...colors,
      bg: isHovered ? colors.border + "20" : colors.bg,
    }
  }

  const getStatusIcon = (status: string) => {
    const iconProps = { className: "w-4 h-4" }
    switch (status) {
      case "running":
        return <Activity {...iconProps} className="w-4 h-4 text-blue-600 animate-pulse" />
      case "completed":
        return <CheckCircle {...iconProps} className="w-4 h-4 text-green-600" />
      case "failed":
        return <AlertTriangle {...iconProps} className="w-4 h-4 text-red-600" />
      case "paused":
        return <Pause {...iconProps} className="w-4 h-4 text-yellow-600" />
      default:
        return <Clock {...iconProps} className="w-4 h-4 text-gray-500" />
    }
  }

  const getAgentById = (id: string) => agents.find((a) => a.id === id)

  // Calculate positions for clean layout
  const calculatePositions = () => {
    const positions: { [key: string]: { x: number; y: number } } = {}
    const levelWidth = 300
    const nodeHeight = 120
    const levelCounts: { [level: number]: number } = {}

    // Count nodes per level
    flowNodes.forEach((node) => {
      levelCounts[node.level] = (levelCounts[node.level] || 0) + 1
    })

    // Position nodes
    const levelCounters: { [level: number]: number } = {}
    flowNodes.forEach((node) => {
      levelCounters[node.level] = (levelCounters[node.level] || 0) + 1
      const nodesInLevel = levelCounts[node.level]
      const nodeIndex = levelCounters[node.level] - 1

      positions[node.id] = {
        x: node.level * levelWidth + 50,
        y: 50 + nodeIndex * (nodeHeight + 40) + (nodeIndex > 0 ? 20 : 0),
      }
    })

    return positions
  }

  const positions = calculatePositions()

  const renderConnections = () => {
    return flowNodes.flatMap((node) =>
      node.children.map((childId) => {
        const childNode = flowNodes.find((n) => n.id === childId)
        if (!childNode) return null

        const startPos = positions[node.id]
        const endPos = positions[childId]
        if (!startPos || !endPos) return null

        const startX = startPos.x + 200 // Node width
        const startY = startPos.y + 40 // Node height / 2
        const endX = endPos.x
        const endY = endPos.y + 40

        const midX = startX + (endX - startX) / 2

        const isActive = node.status === "running" || childNode.status === "running"

        return (
          <g key={`${node.id}-${childId}`}>
            <path
              d={`M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`}
              stroke={isActive ? "#3b82f6" : "#e2e8f0"}
              strokeWidth={isActive ? "3" : "2"}
              fill="none"
              className={isActive ? "animate-pulse" : ""}
            />
            <circle
              cx={endX}
              cy={endY}
              r="4"
              fill={isActive ? "#3b82f6" : "#e2e8f0"}
              className={isActive ? "animate-pulse" : ""}
            />
          </g>
        )
      }),
    )
  }

  const maxX = Math.max(...Object.values(positions).map((p) => p.x)) + 250
  const maxY = Math.max(...Object.values(positions).map((p) => p.y)) + 100

  return (
    <Card className="h-[700px] overflow-hidden">
      <CardHeader className="pb-3 border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-blue-600" />
            Workflow Execution Graph
            <Badge variant="secondary">{workflow.status}</Badge>
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-blue-50 text-blue-700">
              {flowNodes.filter((n) => n.status === "running").length} Active
            </Badge>
            <Badge variant="outline" className="bg-green-50 text-green-700">
              {flowNodes.filter((n) => n.status === "completed").length} Completed
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0 h-full">
        <div className="relative h-full overflow-auto bg-gradient-to-br from-slate-50 to-white dark:from-slate-900 dark:to-slate-800">
          <svg ref={svgRef} width={maxX} height={maxY} className="absolute inset-0">
            <defs>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            {renderConnections()}
          </svg>

          {/* Render nodes */}
          {flowNodes.map((node) => {
            const pos = positions[node.id]
            if (!pos) return null

            const agent = node.agentId ? getAgentById(node.agentId) : null
            const isSelected = selectedNode === node.id
            const isHovered = hoveredNode === node.id
            const colors = getNodeColor(node.status, isHovered)

            return (
              <div
                key={node.id}
                className={`absolute transition-all duration-200 cursor-pointer ${
                  isSelected ? "z-20 scale-105" : "z-10"
                } ${node.status === "running" ? "animate-pulse" : ""}`}
                style={{
                  left: pos.x,
                  top: pos.y,
                  width: "200px",
                  height: "80px",
                }}
                onClick={() => setSelectedNode(isSelected ? null : node.id)}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
              >
                <div
                  className={`w-full h-full rounded-lg border-2 shadow-sm hover:shadow-md transition-all ${
                    isSelected ? "ring-2 ring-blue-500 ring-offset-2" : ""
                  }`}
                  style={{
                    backgroundColor: colors.bg,
                    borderColor: colors.border,
                    filter: node.status === "running" ? "url(#glow)" : "none",
                  }}
                >
                  <div className="p-3 h-full flex flex-col justify-between">
                    {/* Node Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2 min-w-0">
                        {getStatusIcon(node.status)}
                        {agent && <AgentAvatar agent={agent} size="sm" showStatus={false} />}
                        <div className="min-w-0">
                          <h4 className="font-semibold text-sm truncate" style={{ color: colors.text }}>
                            {node.title}
                          </h4>
                          {node.subtitle && (
                            <p className="text-xs opacity-70 truncate" style={{ color: colors.text }}>
                              {node.subtitle}
                            </p>
                          )}
                        </div>
                      </div>
                      <Badge
                        variant="outline"
                        className="text-xs ml-2 flex-shrink-0"
                        style={{ borderColor: colors.border, color: colors.text }}
                      >
                        {node.type}
                      </Badge>
                    </div>

                    {/* Progress Bar */}
                    {node.status === "running" && (
                      <div className="mt-2">
                        <Progress value={node.progress} className="h-1" />
                      </div>
                    )}

                    {/* Metadata */}
                    {node.metadata && (
                      <div className="flex justify-between text-xs mt-1" style={{ color: colors.text }}>
                        {node.metadata.tokensUsed && <span>{(node.metadata.tokensUsed / 1000).toFixed(1)}k</span>}
                        {node.metadata.cost && <span>${node.metadata.cost.toFixed(2)}</span>}
                        {node.metadata.duration && <span>{node.metadata.duration}</span>}
                      </div>
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                {isSelected && (
                  <div className="absolute top-full left-0 mt-2 w-80 bg-white dark:bg-slate-800 border rounded-lg shadow-lg p-4 z-30">
                    <h4 className="font-semibold mb-2">{node.title}</h4>
                    {node.subtitle && <p className="text-sm text-muted-foreground mb-3">{node.subtitle}</p>}

                    {node.metadata && (
                      <div className="grid grid-cols-2 gap-2 mb-3 text-sm">
                        {node.metadata.tokensUsed && (
                          <div>
                            <span className="text-muted-foreground">Tokens:</span>
                            <span className="ml-1 font-medium">{node.metadata.tokensUsed.toLocaleString()}</span>
                          </div>
                        )}
                        {node.metadata.cost && (
                          <div>
                            <span className="text-muted-foreground">Cost:</span>
                            <span className="ml-1 font-medium">${node.metadata.cost.toFixed(3)}</span>
                          </div>
                        )}
                      </div>
                    )}

                    {node.metadata?.outputs && (
                      <div className="mb-3">
                        <p className="text-sm font-medium mb-1">Outputs:</p>
                        <div className="flex flex-wrap gap-1">
                          {node.metadata.outputs.slice(0, 3).map((output, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {output}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2">
                      {node.agentId && (
                        <Button size="sm" variant="outline" onClick={() => onViewAgent(node.agentId!)}>
                          <Eye className="w-3 h-3 mr-1" />
                          View Agent
                        </Button>
                      )}
                      {node.status === "running" && node.taskId && (
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => {
                            if (node.agentId && node.taskId) {
                              onInterruptAgent(node.agentId, node.taskId)
                            }
                          }}
                        >
                          <Zap className="w-3 h-3 mr-1" />
                          Interrupt
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          })}

          {/* Legend */}
          <div className="absolute top-4 right-4 bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm p-4 rounded-lg border shadow-lg">
            <h4 className="font-semibold text-sm mb-3">Status Legend</h4>
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-blue-100 border border-blue-500"></div>
                <span>Running</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-green-100 border border-green-500"></div>
                <span>Completed</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-yellow-100 border border-yellow-500"></div>
                <span>Paused</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-gray-100 border border-gray-300"></div>
                <span>Pending</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
