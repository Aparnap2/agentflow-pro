"use client"

import { useState } from "react"
import { AgentCard } from "@/components/ui/agent-card"
import { AgentConfigForm } from "@/components/forms/agent-config-form"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { agentTemplates, coreAgents } from "@/data/agent-templates"
import { Search, Plus } from "lucide-react"

export function AgentMarketplace() {
  const [searchTerm, setSearchTerm] = useState("")
  const [categoryFilter, setCategoryFilter] = useState("all")
  const [complexityFilter, setComplexityFilter] = useState("all")
  const [configuring, setConfiguring] = useState<string | null>(null)

  const filteredAgents = agentTemplates.filter((agent) => {
    const matchesSearch =
      agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = categoryFilter === "all" || agent.category === categoryFilter
    const matchesComplexity = complexityFilter === "all" || agent.complexity === complexityFilter

    return matchesSearch && matchesCategory && matchesComplexity
  })

  const handleDeploy = (agentId: string) => {
    setConfiguring(agentId)
  }

  const handleSaveConfig = (config: any) => {
    console.log("Saving agent config:", config)
    setConfiguring(null)
    // Here you would save the configuration and deploy the agent
  }

  if (configuring) {
    return <AgentConfigForm agentType={configuring} onSave={handleSaveConfig} onCancel={() => setConfiguring(null)} />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Agent Marketplace</h2>
          <p className="text-muted-foreground">Pre-built agents for SMB & startup boring task automation</p>
        </div>
        <Button size="sm" className="bg-gradient-to-r from-blue-600 to-purple-600">
          <Plus className="w-4 h-4 mr-2" />
          Custom Agent
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search agents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="core">Core Agents</SelectItem>
            <SelectItem value="specialist">Specialists</SelectItem>
          </SelectContent>
        </Select>
        <Select value={complexityFilter} onValueChange={setComplexityFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Complexity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Complexity</SelectItem>
            <SelectItem value="simple">Simple</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="advanced">Advanced</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Core Agents */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <h3 className="text-xl font-semibold">Core Agents</h3>
          <Badge variant="outline">Required</Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {coreAgents.map((agent) => (
            <div key={agent.id} className="p-4 border rounded-lg bg-slate-50 dark:bg-slate-900">
              <div className="flex items-center gap-3 mb-3">
                <div className="text-3xl">{agent.icon}</div>
                <div>
                  <h4 className="font-semibold">{agent.name}</h4>
                  <p className="text-sm text-muted-foreground">{agent.description}</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">{agent.role}</p>
              <Button size="sm" className="mt-3 w-full" disabled>
                Auto-deployed
              </Button>
            </div>
          ))}
        </div>
      </div>

      {/* Specialist Agents */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <h3 className="text-xl font-semibold">Specialist Agents</h3>
          <Badge variant="secondary">{filteredAgents.length} available</Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map((agent) => (
            <AgentCard
              key={agent.id}
              name={agent.name}
              description={agent.description}
              icon={agent.icon}
              status="inactive"
              tasksCompleted={0}
              successRate={0}
              monthlySavings={agent.estimatedSavings}
              onDeploy={() => handleDeploy(agent.id)}
              onConfigure={() => handleDeploy(agent.id)}
              onViewMetrics={() => console.log("View metrics for", agent.id)}
            />
          ))}
        </div>
      </div>

      {filteredAgents.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No agents found matching your criteria.</p>
          <Button
            variant="outline"
            className="mt-4"
            onClick={() => {
              setSearchTerm("")
              setCategoryFilter("all")
              setComplexityFilter("all")
            }}
          >
            Clear Filters
          </Button>
        </div>
      )}
    </div>
  )
}
