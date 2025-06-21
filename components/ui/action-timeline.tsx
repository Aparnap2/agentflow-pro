"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { Play, Pause, Square, Clock, AlertTriangle } from "lucide-react"
import type { AgentAction, VirtualAgent } from "@/types/virtual-office"

interface ActionTimelineProps {
  actions: AgentAction[]
  agents: VirtualAgent[]
  onPauseAction: (actionId: string) => void
  onCancelAction: (actionId: string) => void
  onResumeAction: (actionId: string) => void
}

export function ActionTimeline({
  actions,
  agents,
  onPauseAction,
  onCancelAction,
  onResumeAction,
}: ActionTimelineProps) {
  const getAgentById = (id: string) => agents.find((agent) => agent.id === id)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "in_progress":
        return <Play className="w-4 h-4 text-blue-500" />
      case "paused":
        return <Pause className="w-4 h-4 text-yellow-500" />
      case "completed":
        return <div className="w-4 h-4 bg-green-500 rounded-full" />
      case "cancelled":
        return <Square className="w-4 h-4 text-red-500" />
      case "failed":
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      case "queued":
        return <Clock className="w-4 h-4 text-gray-500" />
      default:
        return <div className="w-4 h-4 bg-gray-300 rounded-full" />
    }
  }

  const getStatusColor = (status: string) => {
    const colors = {
      in_progress: "border-blue-500 bg-blue-50 dark:bg-blue-950",
      paused: "border-yellow-500 bg-yellow-50 dark:bg-yellow-950",
      completed: "border-green-500 bg-green-50 dark:bg-green-950",
      cancelled: "border-red-500 bg-red-50 dark:bg-red-950",
      failed: "border-red-500 bg-red-50 dark:bg-red-950",
      queued: "border-gray-300 bg-gray-50 dark:bg-gray-950",
    }
    return colors[status as keyof typeof colors] || "border-gray-200"
  }

  return (
    <div className="space-y-4">
      {actions.map((action) => {
        const agent = getAgentById(action.agentId)

        return (
          <Card key={action.id} className={`border-l-4 ${getStatusColor(action.status)}`}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  {getStatusIcon(action.status)}
                  {agent && <AgentAvatar agent={agent} size="sm" showStatus={false} />}
                  <div>
                    <h4 className="font-semibold text-sm">{action.action}</h4>
                    <p className="text-xs text-muted-foreground">{action.description}</p>
                    <p className="text-xs text-muted-foreground">
                      by {action.agentName} • {new Date(action.startTime).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={action.priority === "urgent" ? "destructive" : "secondary"}>{action.priority}</Badge>
                  <Badge variant="outline">{action.status.replace("_", " ")}</Badge>
                </div>
              </div>

              {action.status === "in_progress" && (
                <div className="mb-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span>Progress</span>
                    <span>{action.progress}%</span>
                  </div>
                  <Progress value={action.progress} className="h-2" />
                </div>
              )}

              {action.metadata && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3 text-xs">
                  {action.metadata.toolsUsed && (
                    <div>
                      <span className="text-muted-foreground">Tools:</span>
                      <p className="font-medium">{action.metadata.toolsUsed.join(", ")}</p>
                    </div>
                  )}
                  {action.metadata.apiCalls && (
                    <div>
                      <span className="text-muted-foreground">API Calls:</span>
                      <p className="font-medium">{action.metadata.apiCalls}</p>
                    </div>
                  )}
                  {action.metadata.tokensUsed && (
                    <div>
                      <span className="text-muted-foreground">Tokens:</span>
                      <p className="font-medium">{action.metadata.tokensUsed.toLocaleString()}</p>
                    </div>
                  )}
                  {action.metadata.cost && (
                    <div>
                      <span className="text-muted-foreground">Cost:</span>
                      <p className="font-medium">${action.metadata.cost.toFixed(4)}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Child Actions (Hierarchical) */}
              {action.childActions && action.childActions.length > 0 && (
                <div className="ml-6 border-l-2 border-gray-200 pl-4 space-y-2">
                  {action.childActions.map((childAction) => (
                    <div key={childAction.id} className="flex items-center gap-2 text-sm">
                      {getStatusIcon(childAction.status)}
                      <span className="font-medium">{childAction.action}</span>
                      <Badge variant="outline" className="text-xs">
                        {childAction.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}

              {/* Action Controls */}
              <div className="flex gap-2 mt-3">
                {action.status === "in_progress" && (
                  <>
                    <Button size="sm" variant="outline" onClick={() => onPauseAction(action.id)}>
                      <Pause className="w-3 h-3 mr-1" />
                      Pause
                    </Button>
                    <Button size="sm" variant="destructive" onClick={() => onCancelAction(action.id)}>
                      <Square className="w-3 h-3 mr-1" />
                      Cancel
                    </Button>
                  </>
                )}
                {action.status === "paused" && (
                  <Button size="sm" onClick={() => onResumeAction(action.id)}>
                    <Play className="w-3 h-3 mr-1" />
                    Resume
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
