import React, { useState } from 'react';
import { 
  Bot, 
  CheckCircle, 
  Clock, 
  Activity, 
  AlertCircle, 
  Zap, 
  FileText, 
  Terminal, 
  Layers, 
  Settings,
  Users,
  Eye,
  Pause,
  StopCircle,
  ChevronDown,
  ChevronRight,
  RefreshCw,
  Send,
  TrendingUp
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useDashboard } from '../hooks/useDashboard';

// Import types from the API service
import { Agent, LogEntry, Tool, Step } from '../services/api';

// Define types specific to the dashboard
interface DashboardMetrics {
  activeAgents: number;
  tasksCompleted: number;
  avgTaskTime?: number;
  [key: string]: any; // Allow additional properties
}

interface DashboardSystemHealth {
  status: 'operational' | 'degraded' | 'maintenance' | 'error';
  cpu: number;
  memory: number;
  disk: number;
  [key: string]: any; // Allow additional properties
}

interface DashboardStats {
  clickable: any;
  label: any;
  changeType: boolean;
  title: string;
  value: string | number;
  change: number;
  icon: string;
  color: string;
  link?: string;
}

type AgentStatus = 'working' | 'completed' | 'pending_approval' | 'idle' | 'error' | 'starting' | 'stopping' | 'offline';
type LogType = 'success' | 'warning' | 'error' | 'info' | 'active';

// Icon component mapping
const iconComponents: Record<string, React.ComponentType<{ className?: string }>> = {
  Bot,
  CheckCircle,
  Clock,
  Activity,
  AlertCircle,
  Zap,
  FileText,
  Terminal,
  Layers,
  Settings
};

const Dashboard: React.FC = () => {
  // Dashboard state
  const { 
    metrics, 
    systemHealth, 
    activeAgents = [], 
    recentTasks = [],
    stats = [],
    loading,
    error,
    refresh: refreshDashboard,
    submitTask,
    controlAgent,
    handleApproval
  } = useDashboard();
  
  // Local state
  const [taskInput, setTaskInput] = useState('');
  const [_selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Handle task submission
  const handleSubmitTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskInput.trim()) return;
    
    setIsSubmitting(true);
    try {
      await submitTask({
        description: taskInput,
        priority: 1,
        metadata: {
          source: 'dashboard',
          ui_origin: 'task_input'
        }
      });
      setTaskInput('');
      toast.success('Task submitted successfully!');
    } catch (err) {
      console.error('Error submitting task:', err);
      toast.error('Failed to submit task. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle agent action with confirmation
  const handleAgentActionWithConfirm = async (agentId: string, action: string) => {
    if (window.confirm(`Are you sure you want to ${action} this agent?`)) {
      try {
        await controlAgent(agentId, action);
        toast.success(`Agent ${action}ed successfully`);
        refreshDashboard();
      } catch (err) {
        toast.error(`Failed to ${action} agent`);
      }
    }
  };
  
  // Toggle agent details
  const toggleAgentDetails = (agentId: string) => {
    setExpandedAgent(expandedAgent === agentId ? null : agentId);
  };

  // Handle refresh
  const handleRefresh = async () => {
    try {
      await refreshDashboard();
      toast.success('Dashboard refreshed');
    } catch (err) {
      toast.error('Failed to refresh dashboard');
    }
  };

  // Loading state
  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-lg font-medium text-gray-700">Loading dashboard...</p>
          <p className="text-sm text-gray-500 mt-1">This may take a moment</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertCircle className="h-5 w-5 text-red-500" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
              <div className="mt-4">
                <button
                  type="button"
                  onClick={refresh}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Status colors and icons mapping
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-500';
      case 'working':
      case 'in_progress':
        return 'text-blue-500';
      case 'pending':
      case 'pending_approval':
        return 'text-yellow-500';
      case 'error':
      case 'failed':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    const iconMap: Record<string, JSX.Element> = {
      working: <div className="h-2.5 w-2.5 rounded-full bg-blue-500 animate-pulse"></div>,
      completed: <CheckCircle className="h-3.5 w-3.5 text-green-500" />,
      pending_approval: <AlertCircle className="h-3.5 w-3.5 text-yellow-500" />,
      idle: <Clock className="h-3.5 w-3.5 text-gray-500" />,
      starting: <div className="h-2.5 w-2.5 rounded-full bg-blue-400 animate-pulse"></div>,
      stopping: <div className="h-2.5 w-2.5 rounded-full bg-yellow-400"></div>,
      error: <AlertCircle className="h-3.5 w-3.5 text-red-500" />,
      offline: <div className="h-2.5 w-2.5 rounded-full bg-gray-400"></div>
    };
    return iconMap[status] || <div className="h-2.5 w-2.5 rounded-full bg-gray-300"></div>;
  };

  // Get status display text
  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      working: 'In Progress',
      completed: 'Completed',
      pending_approval: 'Pending Approval',
      idle: 'Idle',
      starting: 'Starting...',
      stopping: 'Stopping...',
      error: 'Error',
      offline: 'Offline',
    };
    return statusMap[status] || status;
  };

  // Render step status with proper typing
  const renderStepStatus = (step: Step) => {
    const statusIcons = {
      completed: <CheckCircle className="h-4 w-4 text-green-500" />,
      active: <Activity className="h-4 w-4 text-blue-500" />,
      pending: <Clock className="h-4 w-4 text-yellow-500" />,
      failed: <AlertCircle className="h-4 w-4 text-red-500" />,
      in_progress: <Activity className="h-4 w-4 text-blue-500 animate-pulse" />
    };
    
    return statusIcons[step.status] || statusIcons.pending;
  };

  // Stats grid data with proper typing
  const statsData: DashboardStats[] = [
    { 
      label: 'Active Agents', 
      value: metrics?.activeAgents?.toString() || '0', 
      icon: 'users',
      color: 'text-blue-600',
      change: 2,
      changeType: 'increase',
      clickable: true 
    },
    { 
      label: 'Tasks Completed', 
      value: metrics?.tasksCompleted?.toString() || '0', 
      icon: 'check-circle',
      color: 'text-green-600',
      change: 15,
      changeType: 'increase',
      clickable: true 
    },
    { 
      label: 'Avg. Task Time', 
      value: metrics?.avgTaskTime ? `${metrics.avgTaskTime}m` : 'N/A', 
      icon: 'clock',
      color: 'text-yellow-600',
      change: 5,
      changeType: 'decrease',
      clickable: true 
    },
    {
      label: 'System Status',
      value: systemHealth?.status || 'Loading...',
      icon: 'activity',
      color: systemHealth?.status === 'operational' ? 'text-green-600' :
        systemHealth?.status === 'degraded' ? 'text-yellow-600' :
          systemHealth?.status === 'maintenance' ? 'text-blue-600' : 'text-red-600',
      clickable: true,
      changeType: false,
      title: '',
      change: 0
    }
  ] as const;
  
  // Handle stat click
  const handleStatClick = (stat: DashboardStats) => {
    if (!stat.clickable) return;
    
    switch (stat.label) {
      case 'Active Agents':
        // Filter or navigate to agents view
        console.log('Viewing active agents');
        break;
      case 'Tasks Completed':
        // Navigate to tasks view
        console.log('Viewing completed tasks');
        break;
      case 'Avg. Task Time':
        // Show task time analytics
        console.log('Viewing task time analytics');
        break;
      case 'System Status':
        // Show system health details
        console.log('Viewing system health details');
        break;
    }
  };

  // Render tools list
  const renderTools = (tools: Tool[] | string[] | undefined) => {
    if (!tools || tools.length === 0) return <span className="text-gray-400">No tools configured</span>;
    
    return (
      <div className="flex flex-wrap gap-2">
        {tools.map((tool, index) => (
          <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {typeof tool === 'string' ? tool : tool.name}
          </span>
        ))}
      </div>
    );
  };
  
  // Use the function to avoid unused warning
  const _renderTools = renderTools;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Real-time monitoring and control of your AI agent operations</p>
        </div>
        <button
          onClick={handleRefresh}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          disabled={loading}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statsData.map((stat, index) => {
          const getIcon = () => {
            switch(stat.icon) {
              case 'users':
                return <Users className="h-6 w-6 text-blue-600" />;
              case 'check-circle':
                return <CheckCircle className="h-6 w-6 text-green-600" />;
              case 'clock':
                return <Clock className="h-6 w-6 text-yellow-600" />;
              case 'activity':
                return <Activity className="h-6 w-6 text-purple-600" />;
              default:
                return <Activity className="h-6 w-6 text-gray-600" />;
            }
          };
          
          return (
            <div 
              key={index}
              className={`bg-white p-6 rounded-xl shadow-sm border border-gray-200 transition-all duration-200 ${
                stat.clickable ? 'cursor-pointer hover:shadow-md hover:border-blue-300' : ''
              }`}
              onClick={() => stat.clickable && handleStatClick(stat)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <div className="flex items-center space-x-2">
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                    {stat.change !== undefined && stat.changeType && (
                      <span className={`text-sm ${
                        stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                      } font-medium`}>
                        {stat.changeType === 'increase' ? '+' : '-'}{stat.change}%
                      </span>
                    )}
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-gray-50">
                  {getIcon()}
                </div>
              </div>
            </div>
          );
        })}
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
        </div>
      </div>
      
      <div className="space-y-6">
        {activeAgents.map((agent: Agent) => (
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
                      onClick={() => toggleAgentDetails(agent.id)}
                      className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                      title="View Details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleAgentActionWithConfirm(agent.id, 'pause')}
                      className="p-2 text-gray-400 hover:text-yellow-600 rounded-lg hover:bg-yellow-50 transition-colors"
                      title="Pause Agent"
                    >
                      <Pause className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleAgentActionWithConfirm(agent.id, 'stop')}
                      className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                      title="Stop Agent"
                    >
                      <StopCircle className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => toggleAgentDetails(agent.id)}
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
                    {agent.steps && agent.steps.map((step: Step, index: number) => (
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
                  {renderTools(agent.tools)}
                </div>

                {/* Activity Logs */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                    <Terminal className="h-4 w-4 mr-2" />
                    Activity Log
                  </h4>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {agent.logs && agent.logs.map((log: LogEntry, index: number) => (
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
                          {agent.pendingApproval?.items.map((item: string, index: number) => (
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
                          {agent.output?.files.map((file: string, index: number) => (
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
                          {agent.output?.insights.map((insight: string, index: number) => (
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