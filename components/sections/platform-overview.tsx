import { StatCard } from "@/components/ui/stat-card"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Brain, Workflow, Users, Target, DollarSign, Activity, TrendingUp, Zap, Download, Plus } from "lucide-react"

interface PlatformOverviewProps {
  stats: {
    totalAgents: number
    activeWorkflows: number
    businessesServed: number
    tasksAutomated: number
    costSavings: number
    uptime: number
  }
}

export function PlatformOverview({ stats }: PlatformOverviewProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">AgentFlow Pro Platform</h2>
          <p className="text-muted-foreground">SMB & Startup Boring Task Automation</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export Data
          </Button>
          <Button size="sm" className="bg-gradient-to-r from-blue-600 to-purple-600">
            <Plus className="w-4 h-4 mr-2" />
            Quick Start
          </Button>
        </div>
      </div>

      {/* Platform Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          title="Active Agents"
          value={stats.totalAgents}
          description="Deployed agents"
          icon={Brain}
          color="blue"
          trend="+12% this month"
        />
        <StatCard
          title="Workflows"
          value={stats.activeWorkflows}
          description="Running workflows"
          icon={Workflow}
          color="green"
          trend="+8% this week"
        />
        <StatCard
          title="Businesses"
          value={stats.businessesServed}
          description="SMBs served"
          icon={Users}
          color="purple"
          trend="+23% this quarter"
        />
        <StatCard
          title="Tasks Automated"
          value={`${(stats.tasksAutomated / 1000).toFixed(1)}K`}
          description="Boring tasks eliminated"
          icon={Target}
          color="orange"
          trend="+156% this month"
        />
        <StatCard
          title="Cost Savings"
          value={`$${(stats.costSavings / 1000000).toFixed(1)}M`}
          description="Total savings"
          icon={DollarSign}
          color="green"
          trend="+34% this quarter"
        />
        <StatCard
          title="Uptime"
          value={`${stats.uptime}%`}
          description="System reliability"
          icon={Activity}
          color="blue"
          trend="99.9% SLA"
        />
      </div>

      {/* Architecture Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            AgentFlow Pro Architecture
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Simple Architecture Diagram */}
            <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-6">
              <div className="text-center space-y-6">
                {/* Co-Founder Agent */}
                <div>
                  <div className="w-48 h-16 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg flex items-center justify-center font-semibold mx-auto">
                    🤝 Co-Founder Agent
                    <br />
                    <span className="text-xs opacity-80">(Strategic Vision)</span>
                  </div>
                </div>

                {/* Arrow */}
                <div className="flex justify-center">
                  <div className="w-px h-8 bg-gray-400"></div>
                </div>

                {/* Manager Agent */}
                <div>
                  <div className="w-48 h-16 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg flex items-center justify-center font-semibold mx-auto">
                    👔 Manager Agent
                    <br />
                    <span className="text-xs opacity-80">(Workflow Coordination)</span>
                  </div>
                </div>

                {/* Arrow */}
                <div className="flex justify-center">
                  <div className="w-px h-8 bg-gray-400"></div>
                </div>

                {/* Specialist Agents */}
                <div>
                  <h4 className="font-semibold mb-4">Vertical Specialists</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="w-24 h-16 bg-green-500 text-white rounded-lg flex items-center justify-center text-xs font-semibold">
                      🎯 CRM
                    </div>
                    <div className="w-24 h-16 bg-orange-500 text-white rounded-lg flex items-center justify-center text-xs font-semibold">
                      📧 Email
                    </div>
                    <div className="w-24 h-16 bg-pink-500 text-white rounded-lg flex items-center justify-center text-xs font-semibold">
                      💰 Invoice
                    </div>
                    <div className="w-24 h-16 bg-teal-500 text-white rounded-lg flex items-center justify-center text-xs font-semibold">
                      📅 Schedule
                    </div>
                    <div className="w-24 h-16 bg-red-500 text-white rounded-lg flex items-center justify-center text-xs font-semibold">
                      📱 Social
                    </div>
                    <div className="w-24 h-16 bg-indigo-500 text-white rounded-lg flex items-center justify-center text-xs font-semibold">
                      👥 HR
                    </div>
                    <div className="w-24 h-16 bg-yellow-500 text-white rounded-lg flex items-center justify-center text-xs font-semibold">
                      📋 Admin
                    </div>
                    <div className="w-24 h-16 bg-purple-500 text-white rounded-lg flex items-center justify-center text-xs font-semibold">
                      ⭐ Review
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Technology Stack */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Technology Stack</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">LLM:</span>
                      <Badge variant="outline">Claude 3.5 Sonnet</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Orchestration:</span>
                      <Badge variant="outline">LangGraph</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Vector DB:</span>
                      <Badge variant="outline">Qdrant</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Memory:</span>
                      <Badge variant="outline">Graphiti + Neo4j</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Database:</span>
                      <Badge variant="outline">PostgreSQL</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Key Features</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Multi-tenant security</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Usage-based pricing</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Outcome tracking</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Form-based workflows</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Human-in-the-loop</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            Recent Platform Activity
            <Badge variant="secondary" className="ml-auto">
              Live
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="font-medium text-sm">CRM Agent processed 47 leads</p>
                <p className="text-xs text-muted-foreground">TechStartup Inc • 2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="font-medium text-sm">Invoice Agent sent 23 payment reminders</p>
                <p className="text-xs text-muted-foreground">SMB Solutions • 5 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="font-medium text-sm">Email Marketing Agent launched campaign</p>
                <p className="text-xs text-muted-foreground">Growth Co • 8 minutes ago</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
