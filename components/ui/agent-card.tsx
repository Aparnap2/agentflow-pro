"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Settings, BarChart3 } from "lucide-react"

interface AgentCardProps {
  name: string
  description: string
  icon: string
  status: "active" | "inactive" | "configuring"
  tasksCompleted: number
  successRate: number
  monthlySavings: string
  onDeploy: () => void
  onConfigure: () => void
  onViewMetrics: () => void
}

export function AgentCard({
  name,
  description,
  icon,
  status,
  tasksCompleted,
  successRate,
  monthlySavings,
  onDeploy,
  onConfigure,
  onViewMetrics,
}: AgentCardProps) {
  const statusColors = {
    active: "bg-green-500",
    inactive: "bg-gray-400",
    configuring: "bg-yellow-500",
  }

  return (
    <Card className="hover:shadow-lg transition-all">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="text-3xl">{icon}</div>
            <div>
              <CardTitle className="text-lg">{name}</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">{description}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${statusColors[status]}`}></div>
            <Badge variant={status === "active" ? "default" : "secondary"}>{status}</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">{tasksCompleted}</p>
              <p className="text-xs text-muted-foreground">Tasks</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{successRate}%</p>
              <p className="text-xs text-muted-foreground">Success</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">{monthlySavings}</p>
              <p className="text-xs text-muted-foreground">Savings</p>
            </div>
          </div>

          <div className="flex gap-2">
            <Button size="sm" onClick={onDeploy} className="flex-1">
              <Play className="w-4 h-4 mr-1" />
              {status === "active" ? "Running" : "Deploy"}
            </Button>
            <Button size="sm" variant="outline" onClick={onConfigure}>
              <Settings className="w-4 h-4" />
            </Button>
            <Button size="sm" variant="outline" onClick={onViewMetrics}>
              <BarChart3 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
