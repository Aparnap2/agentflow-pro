"use client"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { AgentAvatar } from "@/components/ui/agent-avatar"
import { ApprovalCard } from "@/components/ui/approval-card"
import { Send, Paperclip, Mic, MoreHorizontal } from "lucide-react"
import type { Message, VirtualAgent } from "@/types/virtual-office"
import type { ResearchPlan } from "@/types/workflow"

interface EnhancedChatProps {
  participants: VirtualAgent[]
  messages: Message[]
  pendingApprovals: ResearchPlan[]
  onSendMessage: (content: string) => void
  onApprovePlan: (planId: string) => void
  onRejectPlan: (planId: string) => void
  activeAgent?: string
}

export function EnhancedChat({
  participants,
  messages,
  pendingApprovals,
  onSendMessage,
  onApprovePlan,
  onRejectPlan,
  activeAgent,
}: EnhancedChatProps) {
  const [newMessage, setNewMessage] = useState("")
  const [isTyping, setIsTyping] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, pendingApprovals])

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
    <Card className="h-[700px] flex flex-col">
      <CardHeader className="pb-3 border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Virtual Office Chat</CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {participants.filter((p) => p.status === "active" || p.status === "working").length} online
            </Badge>
            {pendingApprovals.length > 0 && (
              <Badge variant="destructive" className="text-xs">
                {pendingApprovals.length} pending approval
              </Badge>
            )}
            <div className="flex -space-x-2">
              {participants.slice(0, 4).map((agent) => (
                <AgentAvatar key={agent.id} agent={agent} size="sm" />
              ))}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => {
            const agent = getAgentByName(message.sender)
            const isUser = message.sender === "You"
            const isConsecutive = index > 0 && messages[index - 1].sender === message.sender

            return (
              <div key={message.id} className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
                {!isUser && !isConsecutive && agent && <AgentAvatar agent={agent} size="sm" showStatus={true} />}
                {!isUser && isConsecutive && <div className="w-8" />}

                <div className={`flex-1 max-w-[75%] ${isUser ? "text-right" : ""}`}>
                  {!isConsecutive && (
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium">{message.sender}</span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                      {agent?.status === "working" && (
                        <Badge variant="secondary" className="text-xs">
                          working
                        </Badge>
                      )}
                    </div>
                  )}

                  <div
                    className={`p-3 rounded-2xl ${
                      isUser ? "bg-blue-500 text-white rounded-br-md" : "bg-slate-100 dark:bg-slate-800 rounded-bl-md"
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{message.content}</p>
                  </div>
                </div>
              </div>
            )
          })}

          {/* Approval Cards */}
          {pendingApprovals.map((plan) => (
            <div key={plan.id} className="flex justify-center">
              <ApprovalCard plan={plan} onApprove={onApprovePlan} onReject={onRejectPlan} />
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex gap-3">
              <AgentAvatar agent={participants.find((p) => p.name === isTyping)!} size="sm" showStatus={false} />
              <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-2xl rounded-bl-md">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t p-4">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm">
              <Paperclip className="w-4 h-4" />
            </Button>
            <div className="flex-1 relative">
              <Input
                placeholder="Ask your Co-Founder Agent to research and plan..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                className="pr-20"
              />
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex gap-1">
                <Button variant="ghost" size="sm">
                  <Mic className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <Button onClick={handleSend} disabled={!newMessage.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </div>

          {activeAgent && (
            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>{activeAgent} is researching your request...</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
