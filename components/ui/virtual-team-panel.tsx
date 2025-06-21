import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { Target } from "lucide-react"
import type { VirtualAgent } from "@/types/virtual-office"

interface VirtualTeamPanelProps {
  agents: VirtualAgent[]
}

export function VirtualTeamPanel({ agents }: VirtualTeamPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="w-5 h-5" />
          Virtual Team Status
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {agents.map((agent) => (
            <div key={agent.id} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <AgentAvatar agent={agent} size="md" />
                  <div>
                    <h4 className="font-semibold">{agent.name}</h4>
                    <p className="text-sm text-muted-foreground">{agent.role}</p>
                    <p className="text-xs text-muted-foreground mt-1">{agent.personality}</p>
                  </div>
                </div>
                <Badge variant={agent.status === "active" ? "default" : "secondary"}>
                  {agent.status.replace("_", " ")}
                </Badge>
              </div>

              {agent.currentTask && (
                <div className="mb-3 p-2 bg-blue-50 dark:bg-blue-950 rounded text-sm">
                  <p className="font-medium">Current Task:</p>
                  <p className="text-muted-foreground">{agent.currentTask}</p>
                </div>
              )}

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Workload</span>
                  <span>{agent.workload}%</span>
                </div>
                <Progress value={agent.workload} className="h-2" />
              </div>

              <div className="grid grid-cols-3 gap-4 mt-3 text-center">
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

              <div className="mt-3">
                <p className="text-sm font-medium mb-1">Expertise:</p>
                <div className="flex flex-wrap gap-1">
                  {agent.expertise.map((skill) => (
                    <Badge key={skill} variant="outline" className="text-xs">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
