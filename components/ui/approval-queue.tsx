"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react"
import type { Task, VirtualAgent } from "@/types/virtual-office"

interface ApprovalQueueProps {
  tasks: Task[]
  agents: VirtualAgent[]
  onApprove: (taskId: string) => void
  onReject: (taskId: string) => void
}

export function ApprovalQueue({ tasks, agents, onApprove, onReject }: ApprovalQueueProps) {
  const pendingTasks = tasks.filter((task) => task.status === "pending_approval")

  const getAgentById = (id: string) => {
    return agents.find((agent) => agent.id === id)
  }

  const getPriorityColor = (priority: string) => {
    const colors = {
      urgent: "border-red-500 bg-red-50 dark:bg-red-950",
      high: "border-orange-500 bg-orange-50 dark:bg-orange-950",
      medium: "border-yellow-500 bg-yellow-50 dark:bg-yellow-950",
      low: "border-green-500 bg-green-50 dark:bg-green-950",
    }
    return colors[priority as keyof typeof colors] || "border-gray-200"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-orange-500" />
          Approval Queue
          <Badge variant="secondary">{pendingTasks.length} pending</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {pendingTasks.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
            <p className="text-muted-foreground">No tasks pending approval</p>
          </div>
        ) : (
          <div className="space-y-4">
            {pendingTasks.map((task) => {
              const assignedAgent = getAgentById(task.assignedTo)
              const requestingAgent = getAgentById(task.requestedBy)

              return (
                <div key={task.id} className={`p-4 border-2 rounded-lg ${getPriorityColor(task.priority)}`}>
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold">{task.title}</h4>
                      <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
                    </div>
                    <Badge variant={task.priority === "urgent" ? "destructive" : "secondary"}>{task.priority}</Badge>
                  </div>

                  <div className="flex items-center gap-4 mb-3 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Requested by:</span>
                      {requestingAgent && (
                        <div className="flex items-center gap-1">
                          <AgentAvatar agent={requestingAgent} size="sm" showStatus={false} />
                          <span>{requestingAgent.name}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Assign to:</span>
                      {assignedAgent && (
                        <div className="flex items-center gap-1">
                          <AgentAvatar agent={assignedAgent} size="sm" showStatus={false} />
                          <span>{assignedAgent.name}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm mb-4">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>Est. {task.estimatedTime}</span>
                    </div>
                    <span className="text-muted-foreground">{new Date(task.createdAt).toLocaleString()}</span>
                  </div>

                  <div className="flex gap-3">
                    <Button
                      size="sm"
                      onClick={() => onApprove(task.id)}
                      className="flex-1 bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Approve Task
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => onReject(task.id)} className="flex-1">
                      <XCircle className="w-4 h-4 mr-2" />
                      Reject
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
