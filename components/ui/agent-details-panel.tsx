"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Textarea } from "@/components/ui/textarea"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { X, MessageSquare, Zap, AlertTriangle } from "lucide-react"
import { useState } from "react"
import type { VirtualAgent, WorkflowTask } from "@/types/virtual-office"

interface AgentDetailsPanelProps {
  agent: VirtualAgent
  currentTasks: WorkflowTask[]
  onClose: () => void
  onInterrupt: (agentId: string, taskId: string, instructions: string) => void
  onSendMessage: (agentId: string, message: string) => void
}

export function AgentDetailsPanel({
  agent,
  currentTasks,
  onClose,
  onInterrupt,
  onSendMessage,
}: AgentDetailsPanelProps) {
  const [interruptInstructions, setInterruptInstructions] = useState("")
  const [directMessage, setDirectMessage] = useState("")
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null)

  const handleInterrupt = () => {
    if (selectedTaskId && interruptInstructions.trim()) {
      onInterrupt(agent.id, selectedTaskId, interruptInstructions)
      setInterruptInstructions("")
      setSelectedTaskId(null)
    }
  }

  const handleSendMessage = () => {
    if (directMessage.trim()) {
      onSendMessage(agent.id, directMessage)
      setDirectMessage("")
    }
  }

  const activeTasks = currentTasks.filter((task) => task.status === "in_progress")
  const completedTasks = currentTasks.filter((task) => task.status === "completed")

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AgentAvatar agent={agent} size="lg" />
            <div>
              <CardTitle className="text-xl">{agent.name}</CardTitle>
              <p className="text-sm text-muted-foreground">{agent.role}</p>
              <Badge variant={agent.status === "working" ? "default" : "secondary"} className="mt-1">
                {agent.status}
              </Badge>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Agent Overview */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="font-semibold mb-2">Performance</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Success Rate</span>
                <span className="font-medium">{agent.performance.successRate}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Tasks Completed</span>
                <span className="font-medium">{agent.performance.tasksCompleted}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Avg Response Time</span>
                <span className="font-medium">{agent.performance.avgResponseTime}</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Current Workload</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Workload</span>
                <span className="font-medium">{agent.workload}%</span>
              </div>
              <Progress value={agent.workload} className="h-2" />
              <div className="text-xs text-muted-foreground">
                {activeTasks.length} active tasks, {completedTasks.length} completed today
              </div>
            </div>
          </div>
        </div>

        {/* Current Tasks */}
        <div>
          <h4 className="font-semibold mb-3">Current Tasks</h4>
          <div className="space-y-2">
            {activeTasks.length === 0 ? (
              <p className="text-sm text-muted-foreground">No active tasks</p>
            ) : (
              activeTasks.map((task) => (
                <div
                  key={task.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedTaskId === task.id ? "border-blue-500 bg-blue-50 dark:bg-blue-950" : "hover:bg-slate-50"
                  }`}
                  onClick={() => setSelectedTaskId(task.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="font-medium text-sm">{task.title}</h5>
                    <Badge variant="outline">{task.priority}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">{task.description}</p>
                  <div className="flex items-center gap-2">
                    <Progress value={task.progress} className="flex-1 h-1" />
                    <span className="text-xs">{task.progress}%</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Interrupt Controls */}
        {selectedTaskId && (
          <div className="p-4 border-2 border-orange-200 bg-orange-50 dark:bg-orange-950 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-orange-600" />
              <h4 className="font-semibold">Interrupt Agent</h4>
            </div>
            <p className="text-sm text-muted-foreground mb-3">
              Provide new instructions or approach for the selected task
            </p>
            <Textarea
              placeholder="Enter new instructions or different approach..."
              value={interruptInstructions}
              onChange={(e) => setInterruptInstructions(e.target.value)}
              className="mb-3"
            />
            <div className="flex gap-2">
              <Button onClick={handleInterrupt} className="bg-orange-600 hover:bg-orange-700">
                <Zap className="w-4 h-4 mr-2" />
                Apply Interrupt
              </Button>
              <Button variant="outline" onClick={() => setSelectedTaskId(null)}>
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Direct Message */}
        <div className="p-4 border rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <MessageSquare className="w-4 h-4 text-blue-600" />
            <h4 className="font-semibold">Send Direct Message</h4>
          </div>
          <Textarea
            placeholder="Send a direct message to this agent..."
            value={directMessage}
            onChange={(e) => setDirectMessage(e.target.value)}
            className="mb-3"
          />
          <Button onClick={handleSendMessage} disabled={!directMessage.trim()}>
            Send Message
          </Button>
        </div>

        {/* Agent Expertise */}
        <div>
          <h4 className="font-semibold mb-2">Expertise & Personality</h4>
          <p className="text-sm text-muted-foreground mb-2">{agent.personality}</p>
          <div className="flex flex-wrap gap-1">
            {agent.expertise.map((skill) => (
              <Badge key={skill} variant="outline" className="text-xs">
                {skill}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
