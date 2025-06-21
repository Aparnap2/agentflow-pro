"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"

interface AgentConfigFormProps {
  agentType: string
  onSave: (config: any) => void
  onCancel: () => void
}

export function AgentConfigForm({ agentType, onSave, onCancel }: AgentConfigFormProps) {
  const [config, setConfig] = useState({
    name: "",
    description: "",
    llmModel: "claude-3.5-sonnet",
    triggerType: "manual",
    schedule: "",
    tools: [] as string[],
    systemPrompt: "",
  })

  const agentTemplates = {
    crm: {
      name: "CRM Agent",
      description: "Automates lead capture, follow-ups, and pipeline management",
      defaultPrompt: "You are a CRM specialist that helps manage leads, follow-ups, and sales pipeline updates.",
      availableTools: ["HubSpot API", "Salesforce API", "Gmail API", "Calendar API"],
    },
    email_marketing: {
      name: "Email Marketing Agent",
      description: "Handles email campaigns and drip sequences",
      defaultPrompt: "You are an email marketing specialist that creates and manages email campaigns.",
      availableTools: ["Mailchimp API", "SendGrid API", "Gmail API", "Analytics API"],
    },
    invoice: {
      name: "Invoice Agent",
      description: "Automates invoice creation and payment reminders",
      defaultPrompt: "You are an invoicing specialist that creates invoices and manages payments.",
      availableTools: ["QuickBooks API", "Stripe API", "PayPal API", "Xero API"],
    },
    scheduling: {
      name: "Scheduling Agent",
      description: "Manages appointments and calendar sync",
      defaultPrompt: "You are a scheduling specialist that manages appointments and calendar coordination.",
      availableTools: ["Google Calendar API", "Calendly API", "Zoom API", "Teams API"],
    },
    social: {
      name: "Social Media Agent",
      description: "Schedules posts and monitors engagement",
      defaultPrompt: "You are a social media specialist that manages posts and engagement.",
      availableTools: ["Twitter API", "LinkedIn API", "Facebook API", "Instagram API"],
    },
    hr: {
      name: "HR Agent",
      description: "Tracks time and manages leave requests",
      defaultPrompt: "You are an HR specialist that manages time tracking and employee requests.",
      availableTools: ["BambooHR API", "Slack API", "Google Sheets API", "Payroll API"],
    },
    admin: {
      name: "Admin Agent",
      description: "Fills forms and generates reports",
      defaultPrompt: "You are an admin specialist that handles forms and generates reports.",
      availableTools: ["Google Forms API", "Airtable API", "Notion API", "PDF Generator"],
    },
    review: {
      name: "Review Agent",
      description: "Monitors and responds to customer reviews",
      defaultPrompt: "You are a review management specialist that monitors and responds to feedback.",
      availableTools: ["Google Reviews API", "Yelp API", "Trustpilot API", "Survey APIs"],
    },
  }

  const template = agentTemplates[agentType as keyof typeof agentTemplates]

  const handleToolToggle = (tool: string) => {
    setConfig((prev) => ({
      ...prev,
      tools: prev.tools.includes(tool) ? prev.tools.filter((t) => t !== tool) : [...prev.tools, tool],
    }))
  }

  const handleSave = () => {
    onSave({
      ...config,
      type: agentType,
      template: template.name,
    })
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Configure {template.name}</CardTitle>
        <p className="text-sm text-muted-foreground">{template.description}</p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Basic Configuration */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="agent-name">Agent Name</Label>
            <Input
              id="agent-name"
              placeholder={`My ${template.name}`}
              value={config.name}
              onChange={(e) => setConfig((prev) => ({ ...prev, name: e.target.value }))}
            />
          </div>

          <div>
            <Label htmlFor="agent-description">Description</Label>
            <Textarea
              id="agent-description"
              placeholder="Describe what this agent will do for your business..."
              value={config.description}
              onChange={(e) => setConfig((prev) => ({ ...prev, description: e.target.value }))}
            />
          </div>
        </div>

        <Separator />

        {/* LLM Configuration */}
        <div className="space-y-4">
          <h3 className="font-semibold">LLM Configuration</h3>
          <div>
            <Label>Model</Label>
            <Select
              value={config.llmModel}
              onValueChange={(value) => setConfig((prev) => ({ ...prev, llmModel: value }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="claude-3.5-sonnet">Claude 3.5 Sonnet (Recommended)</SelectItem>
                <SelectItem value="gpt-4">GPT-4</SelectItem>
                <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                <SelectItem value="llama-3">Llama 3</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="system-prompt">System Prompt</Label>
            <Textarea
              id="system-prompt"
              placeholder={template.defaultPrompt}
              value={config.systemPrompt}
              onChange={(e) => setConfig((prev) => ({ ...prev, systemPrompt: e.target.value }))}
              className="min-h-[100px]"
            />
          </div>
        </div>

        <Separator />

        {/* Trigger Configuration */}
        <div className="space-y-4">
          <h3 className="font-semibold">Trigger Configuration</h3>
          <div>
            <Label>Trigger Type</Label>
            <Select
              value={config.triggerType}
              onValueChange={(value) => setConfig((prev) => ({ ...prev, triggerType: value }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="manual">Manual</SelectItem>
                <SelectItem value="webhook">Webhook</SelectItem>
                <SelectItem value="schedule">Schedule</SelectItem>
                <SelectItem value="event">Event-based</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {config.triggerType === "schedule" && (
            <div>
              <Label htmlFor="schedule">Schedule (Cron Expression)</Label>
              <Input
                id="schedule"
                placeholder="0 9 * * 1-5 (Every weekday at 9 AM)"
                value={config.schedule}
                onChange={(e) => setConfig((prev) => ({ ...prev, schedule: e.target.value }))}
              />
            </div>
          )}
        </div>

        <Separator />

        {/* Tools Configuration */}
        <div className="space-y-4">
          <h3 className="font-semibold">Available Tools</h3>
          <div className="grid grid-cols-2 gap-2">
            {template.availableTools.map((tool) => (
              <div
                key={tool}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  config.tools.includes(tool) ? "border-blue-500 bg-blue-50 dark:bg-blue-950" : "hover:bg-slate-50"
                }`}
                onClick={() => handleToolToggle(tool)}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{tool}</span>
                  {config.tools.includes(tool) && <Badge variant="secondary">Selected</Badge>}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <Button onClick={handleSave} className="flex-1">
            Save Configuration
          </Button>
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
