import React, { useState } from 'react';
import { 
  Send, 
  Bot, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  Zap,
  Activity,
  Pause,
  StopCircle,
  Eye,
  Settings,
  FileText,
  ChevronDown,
  ChevronRight,
  Terminal,
  Layers
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const [taskInput, setTaskInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [expandedAgent, setExpandedAgent] = useState<number | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null);

  const handleSubmitTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskInput.trim()) return;
    
    setIsSubmitting(true);
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      setTaskInput('');
    }, 2000);
  };

  const activeAgents = [
    { 
      id: 1,
      name: 'CEO Agent', 
      status: 'working', 
      task: 'Strategic planning for Q2 2024 product roadmap',
      progress: 75,
      currentStep: 'Analyzing market trends and competitor positioning',
      steps: [
        { name: 'Market Research', status: 'completed', duration: '45m', details: 'Analyzed 50+ competitor websites, pricing models' },
        { name: 'Trend Analysis', status: 'completed', duration: '32m', details: 'Processed industry reports, identified 3 key trends' },
        { name: 'Strategic Planning', status: 'active', duration: '18m', details: 'Creating roadmap framework, defining priorities' },
        { name: 'Resource Allocation', status: 'pending', duration: 'Est. 25m', details: 'Budget planning and team assignments' },
        { name: 'Final Review', status: 'pending', duration: 'Est. 15m', details: 'Quality check and recommendations' }
      ],
      tools: ['Web Scraper', 'Data Analyzer', 'Report Generator'],
      tokens: 2450,
      cost: '$0.45',
      efficiency: 94,
      logs: [
        { time: '14:32', action: 'Started market research phase', type: 'info' },
        { time: '14:45', action: 'Scraped competitor data from 15 websites', type: 'success' },
        { time: '15:12', action: 'Generated trend analysis report', type: 'success' },
        { time: '15:28', action: 'Currently building strategic framework', type: 'active' }
      ]
    },
    { 
      id: 2,
      name: 'Marketing Agent', 
      status: 'pending_approval', 
      task: 'Social media campaign for product launch',
      progress: 90,
      currentStep: 'Awaiting approval for campaign content',
      steps: [
        { name: 'Audience Research', status: 'completed', duration: '28m', details: 'Identified target demographics, preferences' },
        { name: 'Content Creation', status: 'completed', duration: '52m', details: 'Generated 20 posts, 5 video scripts' },
        { name: 'Campaign Strategy', status: 'completed', duration: '35m', details: 'Defined posting schedule, engagement tactics' },
        { name: 'Approval Review', status: 'active', duration: '12m', details: 'Waiting for human approval on content' },
        { name: 'Campaign Launch', status: 'pending', duration: 'Est. 10m', details: 'Schedule and publish approved content' }
      ],
      tools: ['Content Generator', 'Image Creator', 'Social Media API'],
      tokens: 3200,
      cost: '$0.58',
      efficiency: 88,
      logs: [
        { time: '13:15', action: 'Started audience analysis', type: 'info' },
        { time: '13:43', action: 'Generated 20 social media posts', type: 'success' },
        { time: '14:35', action: 'Created campaign strategy document', type: 'success' },
        { time: '14:47', action: 'Submitted content for approval', type: 'warning' }
      ],
      pendingApproval: {
        type: 'content_review',
        items: ['20 social media posts', '5 video scripts', 'Campaign timeline'],
        reason: 'Content contains brand messaging that requires approval'
      }
    },
    { 
      id: 3,
      name: 'Finance Agent', 
      status: 'completed', 
      task: 'Monthly budget analysis and forecasting',
      progress: 100,
      currentStep: 'Task completed successfully',
      steps: [
        { name: 'Data Collection', status: 'completed', duration: '22m', details: 'Gathered financial data from 5 sources' },
        { name: 'Expense Analysis', status: 'completed', duration: '38m', details: 'Categorized and analyzed all expenses' },
        { name: 'Forecast Modeling', status: 'completed', duration: '45m', details: 'Created 3-month projection models' },
        { name: 'Report Generation', status: 'completed', duration: '18m', details: 'Generated comprehensive financial report' },
        { name: 'Quality Check', status: 'completed', duration: '8m', details: 'Verified calculations and recommendations' }
      ],
      tools: ['Excel Processor', 'Financial Calculator', 'Report Builder'],
      tokens: 1890,
      cost: '$0.32',
      efficiency: 96,
      logs: [
        { time: '11:30', action: 'Connected to financial databases', type: 'info' },
        { time: '11:52', action: 'Processed 500+ transactions', type: 'success' },
        { time: '12:30', action: 'Generated forecast models', type: 'success' },
        { time: '12:48', action: 'Completed financial report', type: 'success' }
      ],
      output: {
        files: ['Monthly_Budget_Report.pdf', 'Forecast_Model.xlsx', 'Expense_Analysis.csv'],
        insights: ['15% cost reduction opportunity identified', 'Q2 revenue projection: +22%']
      }
    },
    { 
      id: 4,
      name: 'Support Agent', 
      status: 'working', 
      task: 'Customer inquiry batch processing',
      progress: 45,
      currentStep: 'Processing customer support tickets',
      steps: [
        { name: 'Ticket Triage', status: 'completed', duration: '15m', details: 'Categorized 45 support tickets by priority' },
        { name: 'Auto-Response', status: 'completed', duration: '12m', details: 'Sent automated responses to 28 tickets' },
        { name: 'Complex Resolution', status: 'active', duration: '25m', details: 'Handling 17 complex customer issues' },
        { name: 'Escalation Review', status: 'pending', duration: 'Est. 20m', details: 'Review tickets requiring human intervention' },
        { name: 'Follow-up', status: 'pending', duration: 'Est. 15m', details: 'Send follow-up messages to customers' }
      ],
      tools: ['Ticket System', 'Knowledge Base', 'Email API'],
      tokens: 1200,
      cost: '$0.19',
      efficiency: 92,
      logs: [
        { time: '15:45', action: 'Started processing 45 tickets', type: 'info' },
        { time: '16:00', action: 'Auto-resolved 28 simple inquiries', type: 'success' },
        { time: '16:15', action: 'Currently handling complex issues', type: 'active' },
        { time: '16:25', action: 'Escalated 3 tickets to human agents', type: 'warning' }
      ]
    }
  ];

  const stats = [
    { label: 'Active Agents', value: '8', icon: Bot, color: 'text-blue-600', trend: '+2', clickable: true },
    { label: 'Tasks Completed', value: '142', icon: CheckCircle, color: 'text-green-600', trend: '+15', clickable: true },
    { label: 'Cost Savings', value: '28%', icon: TrendingUp, color: 'text-emerald-600', trend: '+3%', clickable: true },
    { label: 'Time Saved', value: '45h', icon: Clock, color: 'text-purple-600', trend: '+8h', clickable: true }
  ];

  const handleAgentAction = (agentId: number, action: string) => {
    console.log(`${action} agent ${agentId}`);
    // Implement actual agent control logic
  };

  const handleApproval = (agentId: number, approved: boolean) => {
    console.log(`${approved ? 'Approved' : 'Rejected'} agent ${agentId}`);
    // Implement approval logic
  };

  const handleStatClick = (statLabel: string) => {
    console.log(`Clicked on ${statLabel}`);
    // Navigate to detailed view
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'working': return <div className="animate-spin rounded-full h-3 w-3 bg-blue-600"></div>;
      case 'completed': return <CheckCircle className="h-3 w-3 text-green-600" />;
      case 'pending_approval': return <AlertCircle className="h-3 w-3 text-yellow-600" />;
      default: return <Clock className="h-3 w-3 text-gray-600" />;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Real-time monitoring and control of your AI agent operations</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <div 
            key={index} 
            className={`bg-white p-6 rounded-xl shadow-sm border border-gray-200 transition-all duration-200 ${
              stat.clickable ? 'cursor-pointer hover:shadow-md hover:border-blue-300' : ''
            }`}
            onClick={() => stat.clickable && handleStatClick(stat.label)}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                <div className="flex items-center space-x-2">
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <span className="text-sm text-green-600 font-medium">{stat.trend}</span>
                </div>
              </div>
              <div className={`p-3 rounded-lg bg-gray-50`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Task Input */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Submit New Task</h2>
        <form onSubmit={handleSubmitTask} className="space-y-4">
          <div>
            <label htmlFor="task-input" className="block text-sm font-medium text-gray-700 mb-2">
              Describe what you need in natural language
            </label>
            <div className="relative">
              <textarea
                id="task-input"
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                placeholder="Example: Create a comprehensive marketing campaign for our new product launch, including social media content, email sequences, and lead generation strategy..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                rows={4}
                disabled={isSubmitting}
              />
              <button
                type="submit"
                disabled={!taskInput.trim() || isSubmitting}
                className="absolute bottom-3 right-3 inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Submit Task
                  </>
                )}
              </button>
            </div>
          </div>
          <p className="text-sm text-gray-500">
            Our AI will automatically analyze your request and assign it to the most suitable agent teams.
          </p>
        </form>
      </div>

      {/* Active Agents - Detailed View */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Active Agent Operations</h2>
          <div className="flex items-center space-x-2">
            <Activity className="h-5 w-5 text-green-500" />
            <span className="text-sm text-green-600 font-medium">All Systems Operational</span>
          </div>
        </div>
        
        <div className="space-y-6">
          {activeAgents.map((agent) => (
            <div key={agent.id} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Agent Header */}
              <div className="p-4 bg-gray-50 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${
                        agent.status === 'working' ? 'bg-blue-100' : 
                        agent.status === 'completed' ? 'bg-green-100' : 
                        agent.status === 'pending_approval' ? 'bg-yellow-100' : 'bg-gray-100'
                      }`}>
                        <Bot className={`h-5 w-5 ${
                          agent.status === 'working' ? 'text-blue-600' : 
                          agent.status === 'completed' ? 'text-green-600' : 
                          agent.status === 'pending_approval' ? 'text-yellow-600' : 'text-gray-600'
                        }`} />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                        <p className="text-sm text-gray-600">{agent.task}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(agent.status)}
                      <span className="text-sm font-medium text-gray-700">{agent.currentStep}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="text-right text-sm">
                      <div className="text-gray-600">Progress: <span className="font-medium">{agent.progress}%</span></div>
                      <div className="text-gray-600">Efficiency: <span className="font-medium text-green-600">{agent.efficiency}%</span></div>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                        className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                        title="View Details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleAgentAction(agent.id, 'pause')}
                        className="p-2 text-gray-400 hover:text-yellow-600 rounded-lg hover:bg-yellow-50 transition-colors"
                        title="Pause Agent"
                      >
                        <Pause className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleAgentAction(agent.id, 'stop')}
                        className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                        title="Stop Agent"
                      >
                        <StopCircle className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setExpandedAgent(expandedAgent === agent.id ? null : agent.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        {expandedAgent === agent.id ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        agent.status === 'completed' ? 'bg-green-500' :
                        agent.status === 'pending_approval' ? 'bg-yellow-500' :
                        'bg-blue-500'
                      }`}
                      style={{ width: `${agent.progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedAgent === agent.id && (
                <div className="p-4 space-y-6">
                  {/* Task Steps */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                      <Layers className="h-4 w-4 mr-2" />
                      Task Breakdown
                    </h4>
                    <div className="space-y-2">
                      {agent.steps.map((step, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full ${
                              step.status === 'completed' ? 'bg-green-500' :
                              step.status === 'active' ? 'bg-blue-500 animate-pulse' :
                              'bg-gray-300'
                            }`}></div>
                            <div>
                              <span className="text-sm font-medium text-gray-900">{step.name}</span>
                              <p className="text-xs text-gray-600">{step.details}</p>
                            </div>
                          </div>
                          <span className="text-xs text-gray-500">{step.duration}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Tools & Resources */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                      <Settings className="h-4 w-4 mr-2" />
                      Active Tools
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {agent.tools.map((tool, index) => (
                        <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Activity Logs */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                      <Terminal className="h-4 w-4 mr-2" />
                      Activity Log
                    </h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {agent.logs.map((log, index) => (
                        <div key={index} className="flex items-start space-x-3 text-sm">
                          <span className="text-gray-500 font-mono text-xs">{log.time}</span>
                          <div className={`w-2 h-2 rounded-full mt-1.5 ${
                            log.type === 'success' ? 'bg-green-500' :
                            log.type === 'warning' ? 'bg-yellow-500' :
                            log.type === 'active' ? 'bg-blue-500' :
                            'bg-gray-400'
                          }`}></div>
                          <span className="text-gray-700">{log.action}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Performance Metrics */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-lg font-bold text-gray-900">{agent.tokens.toLocaleString()}</div>
                      <div className="text-xs text-gray-600">Tokens Used</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-lg font-bold text-green-600">{agent.cost}</div>
                      <div className="text-xs text-gray-600">Total Cost</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-lg font-bold text-blue-600">{agent.efficiency}%</div>
                      <div className="text-xs text-gray-600">Efficiency</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Approval Section */}
              {agent.status === 'pending_approval' && agent.pendingApproval && (
                <div className="p-4 bg-yellow-50 border-t border-yellow-200">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-semibold text-yellow-800">Approval Required</h4>
                        <p className="text-sm text-yellow-700 mt-1">{agent.pendingApproval.reason}</p>
                        <div className="mt-2">
                          <p className="text-xs text-yellow-600 font-medium">Items for review:</p>
                          <ul className="text-xs text-yellow-600 mt-1">
                            {agent.pendingApproval.items.map((item, index) => (
                              <li key={index}>• {item}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleApproval(agent.id, false)}
                        className="px-4 py-2 text-sm font-medium text-red-700 bg-red-100 rounded-lg hover:bg-red-200 transition-colors"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleApproval(agent.id, true)}
                        className="px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition-colors"
                      >
                        Approve
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Output Section for Completed Tasks */}
              {agent.status === 'completed' && agent.output && (
                <div className="p-4 bg-green-50 border-t border-green-200">
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="text-sm font-semibold text-green-800">Task Completed</h4>
                      <div className="mt-2 space-y-2">
                        <div>
                          <p className="text-xs text-green-600 font-medium">Generated Files:</p>
                          <div className="flex flex-wrap gap-2 mt-1">
                            {agent.output.files.map((file, index) => (
                              <button
                                key={index}
                                className="text-xs text-green-700 bg-green-100 px-2 py-1 rounded hover:bg-green-200 transition-colors"
                              >
                                <FileText className="h-3 w-3 inline mr-1" />
                                {file}
                              </button>
                            ))}
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-green-600 font-medium">Key Insights:</p>
                          <ul className="text-xs text-green-700 mt-1">
                            {agent.output.insights.map((insight, index) => (
                              <li key={index}>• {insight}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button 
            onClick={() => console.log('Navigate to Agent Studio')}
            className="flex items-center justify-center space-x-2 p-4 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-200"
          >
            <Bot className="h-5 w-5 text-blue-600" />
            <span className="font-medium text-gray-900">Configure Agents</span>
          </button>
          <button 
            onClick={() => console.log('Navigate to Integrations')}
            className="flex items-center justify-center space-x-2 p-4 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-200"
          >
            <Zap className="h-5 w-5 text-purple-600" />
            <span className="font-medium text-gray-900">Add Integration</span>
          </button>
          <button 
            onClick={() => console.log('Navigate to Analytics')}
            className="flex items-center justify-center space-x-2 p-4 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-200"
          >
            <TrendingUp className="h-5 w-5 text-green-600" />
            <span className="font-medium text-gray-900">View Analytics</span>
          </button>
          <button 
            onClick={() => console.log('Navigate to Monitoring')}
            className="flex items-center justify-center space-x-2 p-4 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-200"
          >
            <Activity className="h-5 w-5 text-red-600" />
            <span className="font-medium text-gray-900">System Monitor</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;