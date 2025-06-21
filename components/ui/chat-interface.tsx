"use client"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { Send, ThumbsUp, ThumbsDown } from "lucide-react"
import type { Message, VirtualAgent } from "@/types/virtual-office"

interface ChatInterfaceProps {
  participants: VirtualAgent[]
  messages: Message[]
  onSendMessage: (content: string) => void
  onApproveTask?: (taskId: string) => void
  onRejectTask?: (taskId: string) => void
}

export function ChatInterface({
  participants,
  messages,
  onSendMessage,
  onApproveTask,
  onRejectTask,
}: ChatInterfaceProps) {
  const [newMessage, setNewMessage] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (newMessage.trim()) {
      onSendMessage(newMessage)
      setNewMessage("")
    }
  }

  const getAgentByName = (name: string) => {
    return participants.find((p) => p.name === name)
  }

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Virtual Office Chat</CardTitle>
          <div className="flex -space-x-2">
            {participants.map((agent) => (
              <AgentAvatar key={agent.id} agent={agent} size="sm" />
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => {
            const agent = getAgentByName(message.sender)
            const isUser = message.sender === "You"

            return (
              <div key={message.id} className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
                {!isUser && agent && <AgentAvatar agent={agent} size="sm" showStatus={false} />}
                <div className={`flex-1 max-w-[80%] ${isUser ? "text-right" : ""}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium">{message.sender}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                    {message.type !== "text" && (
                      <Badge variant="outline" className="text-xs">
                        {message.type.replace("_", " ")}
                      </Badge>
                    )}
                  </div>
                  <div
                    className={`p-3 rounded-lg ${
                      isUser
                        ? "bg-blue-500 text-white"
                        : message.type === "approval_request"
                          ? "bg-yellow-50 border border-yellow-200"
                          : "bg-slate-100 dark:bg-slate-800"
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>

                    {/* Approval Request Actions */}
                    {message.type === "approval_request" && message.metadata?.taskId && (
                      <div className="flex gap-2 mt-3">
                        <Button
                          size="sm"
                          onClick={() => onApproveTask?.(message.metadata.taskId)}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <ThumbsUp className="w-3 h-3 mr-1" />
                          Approve
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => onRejectTask?.(message.metadata.taskId)}>
                          <ThumbsDown className="w-3 h-3 mr-1" />
                          Reject
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              placeholder="Type your message to the team..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
            />
            <Button onClick={handleSend}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
