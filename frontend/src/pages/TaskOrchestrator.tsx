import React, { useState } from 'react';
import { 
  Brain, 
  Send, 
  Bot, 
  Zap, 
  Users, 
  Target, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  Pause,
  StopCircle,
  Eye,
  GitBranch,
  Layers,
  FileText,
  TrendingUp,
  BarChart3,
  ChevronDown,
  ChevronRight,
  Download,
  RefreshCw,
  Search} from 'lucide-react';
import { useCrews } from '../hooks/useApi';

const TaskOrchestrator: React.FC = () => {
  const [taskInput, setTaskInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedPattern, setSelectedPattern] = useState('hierarchical');
  const [expandedTask, setExpandedTask] = useState<number | null>(null);
  const [] = useState<string | null>(null);
  const [orchestrationMode, setOrchestrationMode] = useState('auto');
  const [searchTerm, setSearchTerm] = useState('');
  const [taskResult, setTaskResult] = useState<any>(null);
  
  // Use the custom hook to fetch crews from the API
  const { crews, executeTask } = useCrews();

  const orchestrationPatterns = [
    {
      id: 'hierarchical',
      name: 'Hierarchical (Orchestrator-Delegator)',
      description: 'High-level coordinator decomposes tasks and delegates to specialized workers',
      icon: GitBranch,
      color: 'blue',
      bestFor: 'Complex multi-step projects, strategic planning',
      example: 'Market research → Analysis → Strategy → Implementation plan'
    },
    {
      id: 'router',
      name: 'Router (Intelligent Dispatcher)',
      description: 'Central dispatcher routes tasks to most appropriate specialized teams',
      icon: Target,
      color: 'green',
      bestFor: 'Customer support, content categorization, triage',
      example: 'Support ticket → Technical/Billing/General → Specialist agent'
    },
    {
      id: 'supervisor',
      name: 'Supervisor (Oversight & Review)',
      description: 'Oversight agent monitors quality and compiles final outputs',
      icon: Eye,
      color: 'purple',
      bestFor: 'Quality assurance, compliance, report generation',
      example: 'Multiple workers → Quality check → Final compilation'
    },
    {
      id: 'collaborative',
      name: 'Collaborative (Peer-to-Peer)',
      description: 'Agents work together as equals, sharing information and responsibilities',
      icon: Users,
      color: 'orange',
      bestFor: 'Creative projects, brainstorming, cross-functional tasks',
      example: 'Design + Marketing + Sales → Collaborative campaign creation'
    }
  ];

  const activeOrchestrations = [
    {
      id: 1,
      title: 'Comprehensive Market Analysis for Q2 Product Launch',
      pattern: 'hierarchical',
      status: 'running',
      progress: 65,
      startTime: '2 hours ago',
      estimatedCompletion: '45 minutes',
      coordinator: 'Strategic Planning Orchestrator',
      activeAgents: 5,
      totalAgents: 8,
      currentPhase: 'Competitive Analysis & Trend Research',
      phases: [
        { name: 'Task Decomposition', status: 'completed', duration: '5m', agents: ['Orchestrator'] },
        { name: 'Market Research', status: 'completed', duration: '35m', agents: ['Research Agent', 'Data Collector'] },
        { name: 'Competitive Analysis', status: 'active', duration: '25m', agents: ['Analyst Agent', 'Web Scraper'] },
        { name: 'Trend Analysis', status: 'active', duration: '20m', agents: ['Trend Analyst'] },
        { name: 'Strategy Formulation', status: 'pending', duration: 'Est. 30m', agents: ['Strategic Planner'] },
        { name: 'Report Compilation', status: 'pending', duration: 'Est. 15m', agents: ['Report Generator'] },
        { name: 'Quality Review', status: 'pending', duration: 'Est. 10m', agents: ['Supervisor Agent'] }
      ],
      agentActivities: [
        { agent: 'Research Agent', task: 'Analyzing industry reports and market data', status: 'completed', progress: 100 },
        { agent: 'Data Collector', task: 'Gathering competitor pricing and features', status: 'completed', progress: 100 },
        { agent: 'Analyst Agent', task: 'Processing competitive landscape data', status: 'active', progress: 75 },
        { agent: 'Web Scraper', task: 'Extracting competitor website information', status: 'active', progress: 60 },
        { agent: 'Trend Analyst', task: 'Identifying market trends and opportunities', status: 'active', progress: 45 }
      ],
      metrics: {
        tokensUsed: 15420,
        apiCalls: 234,
        cost: '$2.85',
        efficiency: 92
      },
      outputs: [
        { name: 'Market_Research_Summary.pdf', status: 'completed', size: '2.3 MB' },
        { name: 'Competitor_Analysis.xlsx', status: 'in_progress', size: '1.8 MB' },
        { name: 'Trend_Report.docx', status: 'pending', size: 'TBD' }
      ]
    },
    {
      id: 2,
      title: 'Customer Support Ticket Resolution Batch',
      pattern: 'router',
      status: 'running',
      progress: 80,
      startTime: '1 hour ago',
      estimatedCompletion: '20 minutes',
      coordinator: 'Support Router Agent',
      activeAgents: 4,
      totalAgents: 6,
      currentPhase: 'Complex Issue Resolution',
      phases: [
        { name: 'Ticket Intake & Triage', status: 'completed', duration: '8m', agents: ['Router Agent'] },
        { name: 'Category Classification', status: 'completed', duration: '12m', agents: ['Classifier Agent'] },
        { name: 'Simple Issue Resolution', status: 'completed', duration: '25m', agents: ['General Support', 'FAQ Bot'] },
        { name: 'Complex Issue Routing', status: 'active', duration: '15m', agents: ['Technical Support', 'Billing Specialist'] },
        { name: 'Quality Check', status: 'pending', duration: 'Est. 10m', agents: ['QA Agent'] }
      ],
      agentActivities: [
        { agent: 'Router Agent', task: 'Monitoring overall ticket flow', status: 'active', progress: 100 },
        { agent: 'Technical Support', task: 'Resolving API integration issues', status: 'active', progress: 70 },
        { agent: 'Billing Specialist', task: 'Processing payment disputes', status: 'active', progress: 85 },
        { agent: 'General Support', task: 'Handling standard inquiries', status: 'completed', progress: 100 }
      ],
      metrics: {
        tokensUsed: 8920,
        apiCalls: 156,
        cost: '$1.45',
        efficiency: 95
      },
      outputs: [
        { name: 'Resolved_Tickets_Report.pdf', status: 'in_progress', size: '1.2 MB' },
        { name: 'Escalation_Summary.xlsx', status: 'pending', size: 'TBD' }
      ]
    },
    {
      id: 3,
      title: 'Social Media Campaign Creation & Review',
      pattern: 'collaborative',
      status: 'pending_approval',
      progress: 90,
      startTime: '3 hours ago',
      estimatedCompletion: 'Awaiting approval',
      coordinator: 'Campaign Collaboration Hub',
      activeAgents: 3,
      totalAgents: 4,
      currentPhase: 'Final Review & Approval',
      phases: [
        { name: 'Creative Brainstorming', status: 'completed', duration: '45m', agents: ['Creative Agent', 'Brand Agent'] },
        { name: 'Content Creation', status: 'completed', duration: '60m', agents: ['Content Creator', 'Designer Agent'] },
        { name: 'Cross-Review & Refinement', status: 'completed', duration: '30m', agents: ['All Agents'] },
        { name: 'Campaign Strategy Alignment', status: 'completed', duration: '25m', agents: ['Strategy Agent'] },
        { name: 'Final Approval', status: 'pending_approval', duration: 'Waiting', agents: ['Human Reviewer'] }
      ],
      agentActivities: [
        { agent: 'Creative Agent', task: 'Campaign concept development completed', status: 'completed', progress: 100 },
        { agent: 'Content Creator', task: 'Generated 20 social media posts', status: 'completed', progress: 100 },
        { agent: 'Designer Agent', task: 'Created visual assets and graphics', status: 'completed', progress: 100 },
        { agent: 'Strategy Agent', task: 'Aligned campaign with business goals', status: 'completed', progress: 100 }
      ],
      metrics: {
        tokensUsed: 12340,
        apiCalls: 189,
        cost: '$2.15',
        efficiency: 88
      },
      outputs: [
        { name: 'Campaign_Strategy.pdf', status: 'completed', size: '3.1 MB' },
        { name: 'Social_Media_Content.zip', status: 'completed', size: '15.2 MB' },
        { name: 'Visual_Assets.zip', status: 'completed', size: '8.7 MB' }
      ],
      pendingApproval: {
        items: ['Campaign messaging', 'Visual brand compliance', 'Budget allocation'],
        reason: 'Brand guidelines review required'
      }
    }
  ];

  const systemMetrics = {
    activeOrchestrations: 3,
    totalAgents: 24,
    tasksInQueue: 8,
    avgProcessingTime: '1.2s',
    successRate: '94.2%',
    costEfficiency: '+28%'
  };

  const handleTaskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskInput.trim()) return;
    
    setIsProcessing(true);
    setTaskResult(null);
    
    try {
      // If we have crews, use the first one, otherwise use a default ID
      const crewId = crews.length > 0 ? crews[0].crew_id : 'default_crew';
      
      // Execute the task with the selected crew
      const result = await executeTask(crewId, taskInput, {
        pattern: selectedPattern,
        mode: orchestrationMode
      });
      
      setTaskResult(result);
      console.log('Task execution result:', result);
    } catch (err) {
      console.error('Error executing task:', err);
      setTaskResult({
        success: false,
        error: err instanceof Error ? err.message : 'Unknown error occurred',
        execution_time_ms: 0
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePatternSelect = (patternId: string) => {
    setSelectedPattern(patternId);
  };

  const handleOrchestrationAction = (id: number, action: string) => {
    console.log(`${action} orchestration ${id}`);
  };

  const handleApproval = (id: number, approved: boolean) => {
    console.log(`${approved ? 'Approved' : 'Rejected'} orchestration ${id}`);
  };

  const getPatternColor = (patternId: string) => {
    const pattern = orchestrationPatterns.find(p => p.id === patternId);
    const colorMap: { [key: string]: string } = {
      blue: 'text-blue-600 bg-blue-100',
      green: 'text-green-600 bg-green-100',
      purple: 'text-purple-600 bg-purple-100',
      orange: 'text-orange-600 bg-orange-100'
    };
    return colorMap[pattern?.color || 'blue'];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'completed': return 'text-green-600 bg-green-100';
      case 'pending_approval': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const filteredOrchestrations = activeOrchestrations.filter(orch =>
    orch.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    orch.pattern.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Natural Language Task Orchestrator</h1>
          <p className="text-gray-600">Intelligent task decomposition and multi-agent coordination powered by Gemini + LangGraph</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Mode:</span>
            <select
              value={orchestrationMode}
              onChange={(e: { target: { value: any; }; }) => setOrchestrationMode(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="auto">Auto-Select Pattern</option>
              <option value="manual">Manual Pattern Selection</option>
              <option value="hybrid">Hybrid Mode</option>
            </select>
          </div>
          <button 
            onClick={() => console.log('View orchestration history')}
            className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Clock className="h-4 w-4 mr-2" />
            History
          </button>
        </div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-8">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Orchestrations</p>
              <p className="text-2xl font-bold text-blue-600">{systemMetrics.activeOrchestrations}</p>
            </div>
            <Brain className="h-6 w-6 text-blue-600" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Agents</p>
              <p className="text-2xl font-bold text-green-600">{systemMetrics.totalAgents}</p>
            </div>
            <Bot className="h-6 w-6 text-green-600" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Queue</p>
              <p className="text-2xl font-bold text-orange-600">{systemMetrics.tasksInQueue}</p>
            </div>
            <Clock className="h-6 w-6 text-orange-600" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Processing</p>
              <p className="text-2xl font-bold text-purple-600">{systemMetrics.avgProcessingTime}</p>
            </div>
            <Zap className="h-6 w-6 text-purple-600" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-emerald-600">{systemMetrics.successRate}</p>
            </div>
            <CheckCircle className="h-6 w-6 text-emerald-600" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cost Efficiency</p>
              <p className="text-2xl font-bold text-green-600">{systemMetrics.costEfficiency}</p>
            </div>
            <TrendingUp className="h-6 w-6 text-green-600" />
          </div>
        </div>
      </div>

      {/* Task Input Interface */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Natural Language Task Input</h2>
        <form onSubmit={handleTaskSubmit} className="space-y-4">
          <div>
            <label htmlFor="task-input" className="block text-sm font-medium text-gray-700 mb-2">
              Describe your complex task in natural language
            </label>
            <div className="relative">
              <textarea
                id="task-input"
                value={taskInput}
                onChange={(e: { target: { value: any; }; }) => setTaskInput(e.target.value)}
                placeholder="Example: Create a comprehensive go-to-market strategy for our new SaaS product, including competitive analysis, pricing strategy, marketing campaigns, sales enablement materials, and launch timeline with budget allocation..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                rows={4}
                disabled={isProcessing}
              />
              <button
                type="submit"
                disabled={!taskInput.trim() || isProcessing}
                className="absolute bottom-3 right-3 inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Orchestrating...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Orchestrate Task
                  </>
                )}
              </button>
            </div>
          </div>
          
          {orchestrationMode === 'manual' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Select Orchestration Pattern
              </label>
              <div className="grid md:grid-cols-2 gap-4">
                {orchestrationPatterns.map((pattern) => (
                  <div
                    key={pattern.id}
                    onClick={() => handlePatternSelect(pattern.id)}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedPattern === pattern.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`p-2 rounded-lg ${getPatternColor(pattern.id)}`}>
                        <pattern.icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{pattern.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{pattern.description}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          <strong>Best for:</strong> {pattern.bestFor}
                        </p>
                        <p className="text-xs text-blue-600 mt-1">
                          <strong>Example:</strong> {pattern.example}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          <p className="text-sm text-gray-500">
            Our AI will automatically analyze your request, select the optimal orchestration pattern, 
            decompose the task into subtasks, and coordinate specialized agent teams for parallel execution.
          </p>
        </form>
      </div>

      {/* Active Orchestrations */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Active Orchestrations</h2>
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search orchestrations..."
                value={searchTerm}
                onChange={(e: { target: { value: any; }; }) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button 
              onClick={() => console.log('Refresh orchestrations')}
              className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {filteredOrchestrations.map((orchestration) => (
            <div key={orchestration.id} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Orchestration Header */}
              <div className="p-4 bg-gray-50 border-b border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{orchestration.title}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPatternColor(orchestration.pattern)}`}>
                        {orchestrationPatterns.find(p => p.id === orchestration.pattern)?.name}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(orchestration.status)}`}>
                        {orchestration.status.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <span>Coordinator: {orchestration.coordinator}</span>
                      <span>Agents: {orchestration.activeAgents}/{orchestration.totalAgents}</span>
                      <span>Started: {orchestration.startTime}</span>
                      <span>ETA: {orchestration.estimatedCompletion}</span>
                    </div>
                    <p className="text-sm text-blue-600 font-medium mt-1">{orchestration.currentPhase}</p>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <div className="text-right text-sm">
                      <div className="text-gray-600">Progress: <span className="font-medium">{orchestration.progress}%</span></div>
                      <div className="text-gray-600">Cost: <span className="font-medium text-green-600">{orchestration.metrics.cost}</span></div>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => setExpandedTask(expandedTask === orchestration.id ? null : orchestration.id)}
                        className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                        title="View Details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleOrchestrationAction(orchestration.id, 'pause')}
                        className="p-2 text-gray-400 hover:text-yellow-600 rounded-lg hover:bg-yellow-50 transition-colors"
                        title="Pause Orchestration"
                      >
                        <Pause className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleOrchestrationAction(orchestration.id, 'stop')}
                        className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                        title="Stop Orchestration"
                      >
                        <StopCircle className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setExpandedTask(expandedTask === orchestration.id ? null : orchestration.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        {expandedTask === orchestration.id ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        orchestration.status === 'completed' ? 'bg-green-500' :
                        orchestration.status === 'pending_approval' ? 'bg-yellow-500' :
                        orchestration.status === 'error' ? 'bg-red-500' :
                        'bg-blue-500'
                      }`}
                      style={{ width: `${orchestration.progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedTask === orchestration.id && (
                <div className="p-4 space-y-6">
                  {/* Orchestration Phases */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                      <Layers className="h-4 w-4 mr-2" />
                      Orchestration Phases
                    </h4>
                    <div className="space-y-2">
                      {orchestration.phases.map((phase, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full ${
                              phase.status === 'completed' ? 'bg-green-500' :
                              phase.status === 'active' ? 'bg-blue-500 animate-pulse' :
                              phase.status === 'pending_approval' ? 'bg-yellow-500' :
                              'bg-gray-300'
                            }`}></div>
                            <div>
                              <span className="text-sm font-medium text-gray-900">{phase.name}</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {phase.agents.map((agent, agentIndex) => (
                                  <span key={agentIndex} className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                                    {agent}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                          <span className="text-xs text-gray-500">{phase.duration}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Agent Activities */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                      <Bot className="h-4 w-4 mr-2" />
                      Agent Activities
                    </h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      {orchestration.agentActivities.map((activity, index) => (
                        <div key={index} className="p-3 border border-gray-200 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-900">{activity.agent}</span>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(activity.status)}`}>
                              {activity.status}
                            </span>
                          </div>
                          <p className="text-xs text-gray-600 mb-2">{activity.task}</p>
                          <div className="flex items-center justify-between">
                            <div className="w-16 bg-gray-200 rounded-full h-1.5">
                              <div
                                className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                                style={{ width: `${activity.progress}%` }}
                              ></div>
                            </div>
                            <span className="text-xs text-gray-500">{activity.progress}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Metrics & Outputs */}
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                        <BarChart3 className="h-4 w-4 mr-2" />
                        Performance Metrics
                      </h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                          <div className="text-lg font-bold text-gray-900">{orchestration.metrics.tokensUsed.toLocaleString()}</div>
                          <div className="text-xs text-gray-600">Tokens Used</div>
                        </div>
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                          <div className="text-lg font-bold text-blue-600">{orchestration.metrics.apiCalls}</div>
                          <div className="text-xs text-gray-600">API Calls</div>
                        </div>
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                          <div className="text-lg font-bold text-green-600">{orchestration.metrics.cost}</div>
                          <div className="text-xs text-gray-600">Total Cost</div>
                        </div>
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                          <div className="text-lg font-bold text-purple-600">{orchestration.metrics.efficiency}%</div>
                          <div className="text-xs text-gray-600">Efficiency</div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                        <FileText className="h-4 w-4 mr-2" />
                        Generated Outputs
                      </h4>
                      <div className="space-y-2">
                        {orchestration.outputs.map((output, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                            <div className="flex items-center space-x-2">
                              <FileText className="h-4 w-4 text-gray-400" />
                              <div>
                                <span className="text-sm font-medium text-gray-900">{output.name}</span>
                                <div className="text-xs text-gray-500">{output.size}</div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                output.status === 'completed' ? 'bg-green-100 text-green-800' :
                                output.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {output.status.replace('_', ' ')}
                              </span>
                              {output.status === 'completed' && (
                                <button 
                                  onClick={() => console.log(`Download ${output.name}`)}
                                  className="p-1 text-gray-400 hover:text-blue-600 rounded"
                                >
                                  <Download className="h-3 w-3" />
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Approval Section */}
              {orchestration.status === 'pending_approval' && orchestration.pendingApproval && (
                <div className="p-4 bg-yellow-50 border-t border-yellow-200">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-semibold text-yellow-800">Human Approval Required</h4>
                        <p className="text-sm text-yellow-700 mt-1">{orchestration.pendingApproval.reason}</p>
                        <div className="mt-2">
                          <p className="text-xs text-yellow-600 font-medium">Items for review:</p>
                          <ul className="text-xs text-yellow-600 mt-1">
                            {orchestration.pendingApproval.items.map((item, index) => (
                              <li key={index}>• {item}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleApproval(orchestration.id, false)}
                        className="px-4 py-2 text-sm font-medium text-red-700 bg-red-100 rounded-lg hover:bg-red-200 transition-colors"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleApproval(orchestration.id, true)}
                        className="px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition-colors"
                      >
                        Approve
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Orchestration Patterns Reference */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Multi-Agent Orchestration Patterns</h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {orchestrationPatterns.map((pattern) => (
            <div key={pattern.id} className="bg-white p-4 rounded-lg border border-gray-200">
              <div className={`p-2 rounded-lg ${getPatternColor(pattern.id)} w-fit mb-3`}>
                <pattern.icon className="h-5 w-5" />
              </div>
              <h4 className="font-medium text-gray-900 mb-2">{pattern.name}</h4>
              <p className="text-sm text-gray-600 mb-2">{pattern.description}</p>
              <p className="text-xs text-gray-500">
                <strong>Best for:</strong> {pattern.bestFor}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TaskOrchestrator;