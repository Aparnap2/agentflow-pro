"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { Network, Play, Pause, Square, Clock } from "lucide-react"
import type { TaskOrchestration, VirtualAgent } from "@/types/virtual-office"

interface OrchestrationBoardProps {
  orchestrations: TaskOrchestration[]
  agents: VirtualAgent[]
  onPauseOrchestration: (id: string) => void
  onCancelOrchestration: (id: string) => void
  onResumeOrchestration: (id: string) => void
}

export function OrchestrationBoard({
  orchestrations,
  agents,
  onPauseOrchestration,
  onCancelOrchestration,
  onResumeOrchestration,
}: OrchestrationBoardProps) {
  const getAgentById = (id: string) => agents.find((agent) => agent.id === id)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Network className="w-5 h-5" />
          Manager Orchestration Board
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {orchestrations.map((orchestration) => {
            const manager = getAgentById(orchestration.orchestratedBy)

            return (
              <Card key={orchestration.id} className="border-2 border-blue-200">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      {manager && <AgentAvatar agent={manager} size="md" />}
                      <div>
                        <h4 className="font-semibold">{orchestration.title}</h4>
                        <p className="text-sm text-muted-foreground">{orchestration.description}</p>
                        <p className="text-xs text-muted-foreground">
                          Orchestrated by {manager?.name} • {new Date(orchestration.startTime).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <Badge variant={orchestration.status === "executing" ? "default" : "secondary"}>
                      {orchestration.status}
                    </Badge>
                  </div>

                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span>Overall Progress</span>
                      <span>{orchestration.progress}%</span>
                    </div>
                    <Progress value={orchestration.progress} className="h-3" />
                  </div>

                  {/* Parallel Actions */}
                  <div className="mb-4">
                    <h5 className="font-medium text-sm mb-2">
                      Parallel Actions ({orchestration.parallelActions.length})
                    </h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {orchestration.parallelActions.map((action) => {
                        const agent = getAgentById(action.agentId)
                        return (
                          <div
                            key={action.id}
                            className="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-800 rounded"
                          >
                            {agent && <AgentAvatar agent={agent} size="sm" showStatus={false} />}
                            <div className="flex-1">
                              <p className="text-xs font-medium">{action.action}</p>
                              <div className="flex items-center gap-2">
                                <Progress value={action.progress} className="h-1 flex-1" />
                                <span className="text-xs text-muted-foreground">{action.progress}%</span>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4 text-center text-sm">
                    <div>
                      <p className="font-semibold text-blue-600">${orchestration.totalCost.toFixed(2)}</p>
                      <p className="text-muted-foreground">Total Cost</p>
                    </div>
                    <div>
                      <p className="font-semibold text-green-600">
                        {orchestration.parallelActions.filter((a) => a.status === "completed").length}
                      </p>
                      <p className="text-muted-foreground">Completed</p>
                    </div>
                    <div>
                      <p className="font-semibold text-orange-600">
                        {orchestration.parallelActions.filter((a) => a.status === "in_progress").length}
                      </p>
                      <p className="text-muted-foreground">In Progress</p>
                    </div>
                  </div>

                  {orchestration.estimatedCompletion && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                      <Clock className="w-4 h-4" />
                      <span>Est. completion: {new Date(orchestration.estimatedCompletion).toLocaleString()}</span>
                    </div>
                  )}

                  <div className="flex gap-2">
                    {orchestration.status === "executing" && (
                      <>
                        <Button size="sm" variant="outline" onClick={() => onPauseOrchestration(orchestration.id)}>
                          <Pause className="w-3 h-3 mr-1" />
                          Pause All
                        </Button>
                        <Button size="sm" variant="destructive" onClick={() => onCancelOrchestration(orchestration.id)}>
                          <Square className="w-3 h-3 mr-1" />
                          Cancel
                        </Button>
                      </>
                    )}
                    {orchestration.status === "paused" && (
                      <Button size="sm" onClick={() => onResumeOrchestration(orchestration.id)}>
                        <Play className="w-3 h-3 mr-1" />
                        Resume All
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
