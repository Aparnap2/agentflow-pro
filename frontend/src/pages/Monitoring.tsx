import React, { useState } from 'react';
import { 
  Eye, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Zap,
  Brain,
  Shield,
  TrendingUp,
  TrendingDown,
  Pause,
  StopCircle,
  RefreshCw,
  Download,
  Bell,
  Settings,
  FileText,
  BarChart3,
  ChevronDown,
  ChevronRight,
  Search,
  Trash2
} from 'lucide-react';

const Monitoring: React.FC = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [humanInterventionMode, setHumanInterventionMode] = useState(true);
  const [expandedAgent, setExpandedAgent] = useState<number | null>(null);
  const [selectedLog, setSelectedLog] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const systemMetrics = [
    { 
      label: 'System Health', 
      value: '98.5%', 
      status: 'healthy', 
      icon: Activity, 
      trend: 'up',
      details: 'All services operational',
      lastUpdate: '2 minutes ago'
    },
    { 
      label: 'Active Agents', 
      value: '24', 
      status: 'normal', 
      icon: Brain, 
      trend: 'stable',
      details: '18 working, 6 idle',
      lastUpdate: '1 minute ago'
    },
    { 
      label: 'Tasks in Queue', 
      value: '12', 
      status: 'normal', 
      icon: Clock, 
      trend: 'down',
      details: '8 high priority, 4 normal',
      lastUpdate: '30 seconds ago'
    },
    { 
      label: 'Response Time', 
      value: '1.2s', 
      status: 'good', 
      icon: Zap, 
      trend: 'up',
      details: 'Average across all agents',
      lastUpdate: '1 minute ago'
    }
  ];

  const agentActivities = [
    {
      id: 1,
      agentName: 'CEO Agent',
      task: 'Strategic planning for Q2 2024',
      status: 'running',
      progress: 75,
      startTime: '2 hours ago',
      estimatedCompletion: '30 minutes',
      humanIntervention: false,
      priority: 'high',
      tokens: 2450,
      cost: '$0.45',
      cpuUsage: 45,
      memoryUsage: 2.1,
      apiCalls: 156,
      currentOperation: 'Analyzing market trends',
      logs: [
        { time: '16:45:23', level: 'INFO', message: 'Started market research phase', details: 'Initialized web scraping for competitor analysis' },
        { time: '16:47:12', level: 'SUCCESS', message: 'Scraped 15 competitor websites', details: 'Extracted pricing data and feature comparisons' },
        { time: '16:52:08', level: 'INFO', message: 'Processing industry reports', details: 'Analyzing 5 industry trend reports from Q1 2024' },
        { time: '16:55:34', level: 'WARNING', message: 'Rate limit approaching', details: 'API calls: 145/150 per minute' },
        { time: '16:58:12', level: 'SUCCESS', message: 'Generated trend analysis', details: 'Identified 3 key market trends for strategic planning' }
      ],
      performance: {
        accuracy: 94,
        speed: 88,
        efficiency: 92,
        reliability: 96
      }
    },
    {
      id: 2,
      agentName: 'Finance Agent',
      task: 'Monthly budget analysis and forecasting',
      status: 'completed',
      progress: 100,
      startTime: '4 hours ago',
      estimatedCompletion: 'Completed',
      humanIntervention: false,
      priority: 'medium',
      tokens: 1890,
      cost: '$0.32',
      cpuUsage: 0,
      memoryUsage: 0,
      apiCalls: 89,
      currentOperation: 'Task completed',
      logs: [
        { time: '13:30:15', level: 'INFO', message: 'Connected to financial databases', details: 'Established secure connections to 3 data sources' },
        { time: '13:35:42', level: 'SUCCESS', message: 'Data extraction completed', details: 'Retrieved 500+ transactions from last month' },
        { time: '13:48:19', level: 'INFO', message: 'Running expense categorization', details: 'ML model categorizing transactions by type' },
        { time: '14:12:33', level: 'SUCCESS', message: 'Forecast model generated', details: 'Created 3-month projection with 95% confidence' },
        { time: '14:25:07', level: 'SUCCESS', message: 'Report generation completed', details: 'Generated PDF report with visualizations' }
      ],
      performance: {
        accuracy: 98,
        speed: 92,
        efficiency: 96,
        reliability: 99
      },
      output: ['Monthly_Budget_Report.pdf', 'Forecast_Model.xlsx']
    },
    {
      id: 3,
      agentName: 'Marketing Agent',
      task: 'Social media campaign optimization',
      status: 'pending_approval',
      progress: 90,
      startTime: '1 hour ago',
      estimatedCompletion: 'Awaiting approval',
      humanIntervention: true,
      priority: 'medium',
      tokens: 3200,
      cost: '$0.58',
      cpuUsage: 15,
      memoryUsage: 1.2,
      apiCalls: 234,
      currentOperation: 'Waiting for content approval',
      logs: [
        { time: '15:30:45', level: 'INFO', message: 'Started campaign analysis', details: 'Analyzing current social media performance' },
        { time: '15:45:12', level: 'SUCCESS', message: 'Generated 20 post variations', details: 'Created content for Instagram, Twitter, LinkedIn' },
        { time: '16:12:28', level: 'INFO', message: 'A/B testing scenarios created', details: 'Designed 3 different campaign approaches' },
        { time: '16:25:55', level: 'WARNING', message: 'Content flagged for review', details: 'Brand messaging requires human approval' },
        { time: '16:30:18', level: 'INFO', message: 'Submitted for approval', details: 'Waiting for marketing team review' }
      ],
      performance: {
        accuracy: 89,
        speed: 85,
        efficiency: 88,
        reliability: 91
      },
      pendingItems: ['20 social media posts', '3 campaign strategies', 'Budget allocation plan']
    },
    {
      id: 4,
      agentName: 'Support Agent',
      task: 'Customer inquiry batch processing',
      status: 'running',
      progress: 45,
      startTime: '30 minutes ago',
      estimatedCompletion: '1 hour',
      humanIntervention: false,
      priority: 'low',
      tokens: 1200,
      cost: '$0.19',
      cpuUsage: 32,
      memoryUsage: 1.8,
      apiCalls: 67,
      currentOperation: 'Processing complex inquiries',
      logs: [
        { time: '16:30:12', level: 'INFO', message: 'Started ticket processing', details: 'Processing 45 customer support tickets' },
        { time: '16:35:28', level: 'SUCCESS', message: 'Auto-resolved 28 tickets', details: 'Simple inquiries handled automatically' },
        { time: '16:42:15', level: 'INFO', message: 'Handling complex issues', details: 'Processing 17 tickets requiring detailed responses' },
        { time: '16:48:33', level: 'WARNING', message: 'Escalation required', details: '3 tickets need human agent intervention' },
        { time: '16:52:07', level: 'INFO', message: 'Continuing processing', details: '14 tickets remaining in complex queue' }
      ],
      performance: {
        accuracy: 92,
        speed: 94,
        efficiency: 90,
        reliability: 95
      }
    },
    {
      id: 5,
      agentName: 'HR Agent',
      task: 'Employee onboarding documentation',
      status: 'error',
      progress: 25,
      startTime: '3 hours ago',
      estimatedCompletion: 'Error - requires intervention',
      humanIntervention: true,
      priority: 'high',
      tokens: 890,
      cost: '$0.15',
      cpuUsage: 0,
      memoryUsage: 0,
      apiCalls: 23,
      currentOperation: 'Stopped due to API error',
      logs: [
        { time: '14:15:30', level: 'INFO', message: 'Started onboarding process', details: 'Processing new employee documentation' },
        { time: '14:22:45', level: 'SUCCESS', message: 'Generated welcome packet', details: 'Created personalized onboarding materials' },
        { time: '14:35:12', level: 'ERROR', message: 'API connection failed', details: 'Unable to connect to HR management system' },
        { time: '14:36:08', level: 'ERROR', message: 'Retry attempts exhausted', details: 'Failed after 3 connection attempts' },
        { time: '14:37:22', level: 'ERROR', message: 'Task halted', details: 'Manual intervention required to resolve API issue' }
      ],
      performance: {
        accuracy: 85,
        speed: 70,
        efficiency: 60,
        reliability: 75
      },
      error: 'HR Management System API connection timeout'
    }
  ];

  const alerts = [
    {
      id: 1,
      type: 'warning',
      message: 'Marketing Agent requires approval for campaign changes',
      timestamp: '5 minutes ago',
      agent: 'Marketing Agent',
      severity: 'medium',
      details: 'Content contains brand messaging that requires human review before publication',
      action: 'Review pending content in approval queue'
    },
    {
      id: 2,
      type: 'error',
      message: 'HR Agent encountered API rate limit - task paused',
      timestamp: '15 minutes ago',
      agent: 'HR Agent',
      severity: 'high',
      details: 'Connection to HR Management System failed after multiple retry attempts',
      action: 'Check API credentials and system status'
    },
    {
      id: 3,
      type: 'info',
      message: 'Finance Agent completed monthly analysis ahead of schedule',
      timestamp: '1 hour ago',
      agent: 'Finance Agent',
      severity: 'low',
      details: 'Budget analysis and forecasting completed 30 minutes early with 98% accuracy',
      action: 'Review generated reports in dashboard'
    },
    {
      id: 4,
      type: 'warning',
      message: 'System approaching token usage limit',
      timestamp: '2 hours ago',
      agent: 'System',
      severity: 'medium',
      details: 'Current usage: 85% of monthly token allocation',
      action: 'Consider upgrading plan or optimizing agent efficiency'
    }
  ];

  const resourceUsage = [
    { resource: 'CPU Usage', current: 45, max: 100, unit: '%', status: 'normal', trend: 'stable' },
    { resource: 'Memory', current: 6.2, max: 16, unit: 'GB', status: 'normal', trend: 'up' },
    { resource: 'API Calls/min', current: 1250, max: 5000, unit: '', status: 'normal', trend: 'down' },
    { resource: 'Token Usage', current: 125000, max: 500000, unit: '', status: 'normal', trend: 'up' },
    { resource: 'Storage', current: 2.8, max: 10, unit: 'GB', status: 'normal', trend: 'stable' },
    { resource: 'Network I/O', current: 45, max: 100, unit: 'MB/s', status: 'normal', trend: 'stable' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'completed': return 'text-green-600 bg-green-100';
      case 'pending_approval': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'paused': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR': return 'text-red-600 bg-red-100';
      case 'WARNING': return 'text-yellow-600 bg-yellow-100';
      case 'SUCCESS': return 'text-green-600 bg-green-100';
      case 'INFO': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const handleAgentAction = (agentId: number, action: string) => {
    console.log(`${action} agent ${agentId}`);
  };

  const handleApproval = (agentId: number, approved: boolean) => {
    console.log(`${approved ? 'Approved' : 'Rejected'} agent ${agentId}`);
  };

  const handleSystemAction = (action: string) => {
    console.log(`System action: ${action}`);
  };

  const filteredAgents = agentActivities.filter(agent =>
    agent.agentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    agent.task.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Real-Time Monitoring</h1>
          <p className="text-gray-600">Complete visibility and control over your AI agent operations</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Human-in-Loop:</span>
            <button
              onClick={() => setHumanInterventionMode(!humanInterventionMode)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                humanInterventionMode ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  humanInterventionMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          <button 
            onClick={() => handleSystemAction('refresh')}
            className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </button>
          <button 
            onClick={() => handleSystemAction('export')}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            Export Logs
          </button>
        </div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {systemMetrics.map((metric, index) => (
          <div 
            key={index} 
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => console.log(`View details for ${metric.label}`)}
          >
            <div className="flex items-center justify-between mb-2">
              <metric.icon className={`h-6 w-6 ${
                metric.status === 'healthy' || metric.status === 'good' ? 'text-green-600' : 
                metric.status === 'normal' ? 'text-blue-600' : 'text-red-600'
              }`} />
              <div className="flex items-center">
                {metric.trend === 'up' && <TrendingUp className="h-4 w-4 text-green-500" />}
                {metric.trend === 'down' && <TrendingDown className="h-4 w-4 text-red-500" />}
                {metric.trend === 'stable' && <div className="h-4 w-4 bg-gray-400 rounded-full" />}
              </div>
            </div>
            <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
            <p className="text-sm text-gray-600">{metric.label}</p>
            <div className="mt-2 text-xs text-gray-500">
              <div>{metric.details}</div>
              <div>Updated {metric.lastUpdate}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Alerts Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">System Alerts</h2>
          <div className="flex items-center space-x-2">
            <Bell className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-600">{alerts.length} active</span>
            <button 
              onClick={() => console.log('Clear all alerts')}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Clear All
            </button>
          </div>
        </div>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div 
              key={alert.id} 
              className={`p-4 rounded-lg border-l-4 cursor-pointer hover:bg-opacity-80 transition-colors ${
                alert.type === 'error' ? 'bg-red-50 border-red-400' :
                alert.type === 'warning' ? 'bg-yellow-50 border-yellow-400' :
                'bg-blue-50 border-blue-400'
              }`}
              onClick={() => console.log(`View alert details: ${alert.id}`)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  {alert.type === 'error' && <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />}
                  {alert.type === 'warning' && <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />}
                  {alert.type === 'info' && <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />}
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                    <p className="text-xs text-gray-600 mt-1">{alert.details}</p>
                    <p className="text-xs text-gray-500 mt-2">{alert.agent} • {alert.timestamp}</p>
                    <p className="text-xs text-blue-600 mt-1 font-medium">Action: {alert.action}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    alert.severity === 'high' ? 'bg-red-100 text-red-800' :
                    alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {alert.severity}
                  </span>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      console.log(`Dismiss alert ${alert.id}`);
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8 mb-8">
        {/* Agent Activities */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Agent Activities</h2>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search agents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
              </select>
            </div>
          </div>
          
          <div className="space-y-4">
            {filteredAgents.map((activity) => (
              <div key={activity.id} className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-medium text-gray-900">{activity.agentName}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(activity.status)}`}>
                          {activity.status.replace('_', ' ')}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(activity.priority)}`}>
                          {activity.priority}
                        </span>
                        {activity.humanIntervention && (
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-800">
                            Human Review
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{activity.task}</p>
                      <p className="text-xs text-blue-600 font-medium">{activity.currentOperation}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500 mt-2">
                        <span>Started: {activity.startTime}</span>
                        <span>ETA: {activity.estimatedCompletion}</span>
                        <span>Cost: {activity.cost}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => setExpandedAgent(expandedAgent === activity.id ? null : activity.id)}
                        className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                        title="View Details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleAgentAction(activity.id, 'pause')}
                        className="p-2 text-gray-400 hover:text-yellow-600 rounded-lg hover:bg-yellow-50 transition-colors"
                        title="Pause Agent"
                      >
                        <Pause className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleAgentAction(activity.id, 'stop')}
                        className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                        title="Stop Agent"
                      >
                        <StopCircle className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setExpandedAgent(expandedAgent === activity.id ? null : activity.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        {expandedAgent === activity.id ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-medium">{activity.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          activity.status === 'completed' ? 'bg-green-500' :
                          activity.status === 'error' ? 'bg-red-500' :
                          activity.status === 'pending_approval' ? 'bg-yellow-500' :
                          'bg-blue-500'
                        }`}
                        style={{ width: `${activity.progress}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Resource Usage */}
                  <div className="grid grid-cols-4 gap-4 text-xs">
                    <div className="text-center">
                      <div className="font-medium text-gray-900">{activity.cpuUsage}%</div>
                      <div className="text-gray-600">CPU</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium text-gray-900">{activity.memoryUsage}GB</div>
                      <div className="text-gray-600">Memory</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium text-gray-900">{activity.apiCalls}</div>
                      <div className="text-gray-600">API Calls</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium text-gray-900">{activity.tokens.toLocaleString()}</div>
                      <div className="text-gray-600">Tokens</div>
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedAgent === activity.id && (
                  <div className="border-t border-gray-200 p-4 bg-gray-50">
                    <div className="grid md:grid-cols-2 gap-6">
                      {/* Performance Metrics */}
                      <div>
                        <h4 className="text-sm font-semibold text-gray-900 mb-3">Performance Metrics</h4>
                        <div className="space-y-2">
                          {Object.entries(activity.performance).map(([key, value]) => (
                            <div key={key} className="flex items-center justify-between">
                              <span className="text-sm text-gray-600 capitalize">{key}</span>
                              <div className="flex items-center space-x-2">
                                <div className="w-16 bg-gray-200 rounded-full h-2">
                                  <div
                                    className={`h-2 rounded-full ${
                                      value >= 90 ? 'bg-green-500' :
                                      value >= 70 ? 'bg-yellow-500' :
                                      'bg-red-500'
                                    }`}
                                    style={{ width: `${value}%` }}
                                  ></div>
                                </div>
                                <span className="text-sm font-medium text-gray-900">{value}%</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Activity Logs */}
                      <div>
                        <h4 className="text-sm font-semibold text-gray-900 mb-3">Recent Activity</h4>
                        <div className="space-y-2 max-h-40 overflow-y-auto">
                          {activity.logs.slice(-5).map((log, index) => (
                            <div 
                              key={index} 
                              className="flex items-start space-x-2 text-xs cursor-pointer hover:bg-white p-2 rounded"
                              onClick={() => setSelectedLog(selectedLog === `${activity.id}-${index}` ? null : `${activity.id}-${index}`)}
                            >
                              <span className="text-gray-500 font-mono">{log.time}</span>
                              <span className={`px-1 py-0.5 rounded text-xs font-medium ${getLogLevelColor(log.level)}`}>
                                {log.level}
                              </span>
                              <span className="text-gray-700 flex-1">{log.message}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Error Details */}
                    {activity.status === 'error' && activity.error && (
                      <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex items-start space-x-2">
                          <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-red-800">Error Details</p>
                            <p className="text-sm text-red-700 mt-1">{activity.error}</p>
                            <button 
                              onClick={() => handleAgentAction(activity.id, 'retry')}
                              className="mt-2 px-3 py-1 text-xs font-medium text-red-700 bg-red-100 rounded hover:bg-red-200 transition-colors"
                            >
                              Retry Task
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Approval Section */}
                    {activity.status === 'pending_approval' && activity.pendingItems && (
                      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-2">
                            <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5" />
                            <div>
                              <p className="text-sm font-medium text-yellow-800">Approval Required</p>
                              <p className="text-sm text-yellow-700 mt-1">The following items need your review:</p>
                              <ul className="text-sm text-yellow-700 mt-2 space-y-1">
                                {activity.pendingItems.map((item, index) => (
                                  <li key={index} className="flex items-center space-x-2">
                                    <div className="w-1 h-1 bg-yellow-600 rounded-full"></div>
                                    <span>{item}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleApproval(activity.id, false)}
                              className="px-3 py-1 text-sm font-medium text-red-700 bg-red-100 rounded hover:bg-red-200 transition-colors"
                            >
                              Reject
                            </button>
                            <button
                              onClick={() => handleApproval(activity.id, true)}
                              className="px-3 py-1 text-sm font-medium text-green-700 bg-green-100 rounded hover:bg-green-200 transition-colors"
                            >
                              Approve
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Output Files */}
                    {activity.status === 'completed' && activity.output && (
                      <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-start space-x-2">
                          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-green-800">Task Completed</p>
                            <p className="text-sm text-green-700 mt-1">Generated files:</p>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {activity.output.map((file, index) => (
                                <button
                                  key={index}
                                  onClick={() => console.log(`Download ${file}`)}
                                  className="inline-flex items-center px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded hover:bg-green-200 transition-colors"
                                >
                                  <FileText className="h-3 w-3 mr-1" />
                                  {file}
                                </button>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Resource Usage */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">System Resources</h2>
          <div className="space-y-6">
            {resourceUsage.map((resource, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{resource.resource}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">
                      {resource.current.toLocaleString()}{resource.unit} / {resource.max.toLocaleString()}{resource.unit}
                    </span>
                    {resource.trend === 'up' && <TrendingUp className="h-3 w-3 text-red-500" />}
                    {resource.trend === 'down' && <TrendingDown className="h-3 w-3 text-green-500" />}
                    {resource.trend === 'stable' && <div className="h-3 w-3 bg-gray-400 rounded-full" />}
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      (resource.current / resource.max) > 0.8 ? 'bg-red-500' :
                      (resource.current / resource.max) > 0.6 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${(resource.current / resource.max) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">System Control Panel</h3>
            <p className="text-gray-600">Emergency controls and system management</p>
          </div>
          <Shield className="h-8 w-8 text-blue-600" />
        </div>
        <div className="grid md:grid-cols-4 gap-4">
          <button 
            onClick={() => handleSystemAction('pause_all')}
            className="flex items-center justify-center space-x-2 p-4 bg-white rounded-lg hover:bg-yellow-50 transition-colors border border-gray-200 hover:border-yellow-300"
          >
            <Pause className="h-5 w-5 text-yellow-600" />
            <span className="font-medium text-gray-900">Pause All Agents</span>
          </button>
          <button 
            onClick={() => handleSystemAction('emergency_stop')}
            className="flex items-center justify-center space-x-2 p-4 bg-white rounded-lg hover:bg-red-50 transition-colors border border-gray-200 hover:border-red-300"
          >
            <StopCircle className="h-5 w-5 text-red-600" />
            <span className="font-medium text-gray-900">Emergency Stop</span>
          </button>
          <button 
            onClick={() => handleSystemAction('system_settings')}
            className="flex items-center justify-center space-x-2 p-4 bg-white rounded-lg hover:bg-blue-50 transition-colors border border-gray-200 hover:border-blue-300"
          >
            <Settings className="h-5 w-5 text-blue-600" />
            <span className="font-medium text-gray-900">System Settings</span>
          </button>
          <button 
            onClick={() => handleSystemAction('performance_report')}
            className="flex items-center justify-center space-x-2 p-4 bg-white rounded-lg hover:bg-green-50 transition-colors border border-gray-200 hover:border-green-300"
          >
            <BarChart3 className="h-5 w-5 text-green-600" />
            <span className="font-medium text-gray-900">Generate Report</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Monitoring;