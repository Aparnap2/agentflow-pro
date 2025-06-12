import React, { useState } from 'react';
import { 
  Database, 
  Brain, 
  Search, 
  Filter, 
  Plus, 
  Edit, 
  Trash2, 
  Eye,
  Download,
  Settings,
  MessageSquare,
  FileText,
  Zap,
  Target,
  Layers,
  GitBranch,
  Network,
  BarChart3,
  TrendingUp,
  ArrowRight,
  ChevronDown,
  ChevronRight,
  Shield} from 'lucide-react';

const MemoryHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState('knowledge');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMemoryType, setSelectedMemoryType] = useState('all');
  const [expandedMemory, setExpandedMemory] = useState<number | null>(null);
  const [selectedAgent, setSelectedAgent] = useState('all');

  const memoryStats = {
    totalMemories: 15420,
    activeContexts: 234,
    knowledgeBase: 8934,
    conversationalMemory: 4521,
    proceduralMemory: 1965,
    storageUsed: 2.8,
    storageLimit: 10,
    avgRetrievalTime: '0.3s',
    memoryAccuracy: 96.8
  };

  const knowledgeBase = [
    {
      id: 1,
      title: 'Company Product Documentation',
      type: 'document',
      category: 'Product Knowledge',
      size: '15.2 MB',
      entries: 1247,
      lastUpdated: '2 hours ago',
      agent: 'Product Manager Agent',
      status: 'active',
      accuracy: 98.5,
      usage: 342,
      tags: ['product', 'documentation', 'features', 'specifications'],
      description: 'Comprehensive product documentation including features, specifications, and user guides',
      source: 'Internal Documentation System',
      vectorEmbeddings: 15420,
      lastAccessed: '5 minutes ago'
    },
    {
      id: 2,
      title: 'Customer Support Knowledge Base',
      type: 'faq',
      category: 'Support',
      size: '8.7 MB',
      entries: 892,
      lastUpdated: '1 day ago',
      agent: 'Support Agent',
      status: 'active',
      accuracy: 94.2,
      usage: 567,
      tags: ['support', 'troubleshooting', 'faq', 'customer-service'],
      description: 'Frequently asked questions and troubleshooting guides for customer support',
      source: 'Support Ticket Analysis',
      vectorEmbeddings: 8934,
      lastAccessed: '12 minutes ago'
    },
    {
      id: 3,
      title: 'Market Research Database',
      type: 'research',
      category: 'Market Intelligence',
      size: '23.4 MB',
      entries: 2156,
      lastUpdated: '3 hours ago',
      agent: 'Strategic Planner Agent',
      status: 'updating',
      accuracy: 91.7,
      usage: 189,
      tags: ['market-research', 'competitors', 'trends', 'analysis'],
      description: 'Comprehensive market research data including competitor analysis and industry trends',
      source: 'Web Scraping & Industry Reports',
      vectorEmbeddings: 21560,
      lastAccessed: '1 hour ago'
    },
    {
      id: 4,
      title: 'Legal & Compliance Guidelines',
      type: 'policy',
      category: 'Legal',
      size: '12.1 MB',
      entries: 456,
      lastUpdated: '1 week ago',
      agent: 'Legal Agent',
      status: 'active',
      accuracy: 99.1,
      usage: 78,
      tags: ['legal', 'compliance', 'policies', 'regulations'],
      description: 'Legal guidelines, compliance requirements, and policy documentation',
      source: 'Legal Department',
      vectorEmbeddings: 4560,
      lastAccessed: '2 days ago'
    }
  ];

  const conversationalMemory = [
    {
      id: 1,
      agentName: 'CEO Agent',
      conversationId: 'conv_2024_001',
      context: 'Strategic planning discussion for Q2 2024',
      keyPoints: [
        'Focus on market expansion in European markets',
        'Budget allocation for new product development',
        'Hiring plan for engineering team',
        'Partnership opportunities with tech companies'
      ],
      lastInteraction: '2 hours ago',
      interactions: 45,
      sentiment: 'positive',
      priority: 'high',
      status: 'active',
      memoryStrength: 95,
      tags: ['strategy', 'planning', 'expansion', 'budget']
    },
    {
      id: 2,
      agentName: 'Marketing Agent',
      conversationId: 'conv_2024_002',
      context: 'Campaign planning for product launch',
      keyPoints: [
        'Target audience: SMB decision makers',
        'Budget: $50k for digital marketing',
        'Timeline: 6-week campaign duration',
        'Key messaging: efficiency and cost savings'
      ],
      lastInteraction: '4 hours ago',
      interactions: 23,
      sentiment: 'neutral',
      priority: 'medium',
      status: 'active',
      memoryStrength: 87,
      tags: ['marketing', 'campaign', 'launch', 'smb']
    },
    {
      id: 3,
      agentName: 'Support Agent',
      conversationId: 'conv_2024_003',
      context: 'Customer escalation handling procedures',
      keyPoints: [
        'Escalation criteria for technical issues',
        'Response time requirements: <2 hours',
        'Customer satisfaction tracking',
        'Integration with CRM system'
      ],
      lastInteraction: '1 day ago',
      interactions: 67,
      sentiment: 'concerned',
      priority: 'high',
      status: 'archived',
      memoryStrength: 92,
      tags: ['support', 'escalation', 'procedures', 'crm']
    }
  ];

  const proceduralMemory = [
    {
      id: 1,
      name: 'Customer Onboarding Workflow',
      type: 'workflow',
      agent: 'HR Agent',
      steps: 12,
      successRate: 94.5,
      avgDuration: '45 minutes',
      lastExecuted: '3 hours ago',
      executions: 234,
      status: 'optimized',
      description: 'Complete workflow for onboarding new customers including account setup and training',
      triggers: ['new_customer_signup', 'trial_conversion'],
      outputs: ['welcome_email', 'account_credentials', 'training_schedule']
    },
    {
      id: 2,
      name: 'Invoice Processing Procedure',
      type: 'procedure',
      agent: 'Finance Agent',
      steps: 8,
      successRate: 98.2,
      avgDuration: '12 minutes',
      lastExecuted: '1 hour ago',
      executions: 567,
      status: 'active',
      description: 'Automated invoice processing including validation, approval, and payment scheduling',
      triggers: ['invoice_received', 'payment_due'],
      outputs: ['payment_schedule', 'approval_notification', 'accounting_entry']
    },
    {
      id: 3,
      name: 'Content Creation Pipeline',
      type: 'pipeline',
      agent: 'Marketing Agent',
      steps: 15,
      successRate: 89.7,
      avgDuration: '2.5 hours',
      lastExecuted: '6 hours ago',
      executions: 89,
      status: 'active',
      description: 'End-to-end content creation process from ideation to publication',
      triggers: ['content_request', 'campaign_launch'],
      outputs: ['blog_post', 'social_media_content', 'email_newsletter']
    }
  ];

  const memoryConnections = [
    {
      id: 1,
      source: 'Product Documentation',
      target: 'Customer Support KB',
      strength: 0.85,
      type: 'semantic',
      description: 'Product features linked to support solutions'
    },
    {
      id: 2,
      source: 'Market Research',
      target: 'Strategic Planning',
      strength: 0.92,
      type: 'contextual',
      description: 'Market insights inform strategic decisions'
    },
    {
      id: 3,
      source: 'Customer Conversations',
      target: 'Product Feedback',
      strength: 0.78,
      type: 'experiential',
      description: 'Customer feedback influences product development'
    }
  ];

  const tabs = [
    { id: 'knowledge', name: 'Knowledge Base', icon: Database, count: knowledgeBase.length },
    { id: 'conversations', name: 'Conversational Memory', icon: MessageSquare, count: conversationalMemory.length },
    { id: 'procedures', name: 'Procedural Memory', icon: Settings, count: proceduralMemory.length },
    { id: 'connections', name: 'Memory Connections', icon: Network, count: memoryConnections.length },
    { id: 'analytics', name: 'Memory Analytics', icon: BarChart3, count: null }
  ];

  const handleMemoryAction = (action: string, id?: number) => {
    console.log(`Memory action: ${action}`, id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'updating': return 'text-blue-600 bg-blue-100';
      case 'archived': return 'text-gray-600 bg-gray-100';
      case 'optimized': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'document': return FileText;
      case 'faq': return MessageSquare;
      case 'research': return BarChart3;
      case 'policy': return Shield;
      case 'workflow': return GitBranch;
      case 'procedure': return Settings;
      case 'pipeline': return Layers;
      default: return Database;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600';
      case 'neutral': return 'text-gray-600';
      case 'concerned': return 'text-yellow-600';
      case 'negative': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const filteredKnowledge = knowledgeBase.filter(item =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Memory Hub</h1>
          <p className="text-gray-600">Persistent context and knowledge management powered by Graphiti MCP</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => handleMemoryAction('optimize')}
            className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Brain className="h-4 w-4 mr-2" />
            Optimize
          </button>
          <button 
            onClick={() => handleMemoryAction('backup')}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            Backup
          </button>
        </div>
      </div>

      {/* Memory Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Memories</p>
              <p className="text-2xl font-bold text-gray-900">{memoryStats.totalMemories.toLocaleString()}</p>
              <p className="text-xs text-blue-600 mt-1">{memoryStats.activeContexts} active contexts</p>
            </div>
            <Database className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Storage Used</p>
              <p className="text-2xl font-bold text-gray-900">{memoryStats.storageUsed} GB</p>
              <p className="text-xs text-gray-600 mt-1">of {memoryStats.storageLimit} GB limit</p>
            </div>
            <div className="w-8 h-8 relative">
              <div className="w-full h-full bg-gray-200 rounded-full">
                <div
                  className="h-full bg-green-500 rounded-full transition-all duration-300"
                  style={{ width: `${(memoryStats.storageUsed / memoryStats.storageLimit) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Retrieval Time</p>
              <p className="text-2xl font-bold text-gray-900">{memoryStats.avgRetrievalTime}</p>
              <p className="text-xs text-green-600 mt-1">Average response time</p>
            </div>
            <Zap className="h-8 w-8 text-yellow-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Memory Accuracy</p>
              <p className="text-2xl font-bold text-gray-900">{memoryStats.memoryAccuracy}%</p>
              <p className="text-xs text-green-600 mt-1">Retrieval accuracy</p>
            </div>
            <Target className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.name}</span>
                {tab.count !== null && (
                  <span className="bg-gray-100 text-gray-600 px-2 py-1 text-xs rounded-full">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search memories, contexts, or knowledge..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-gray-400" />
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Agents</option>
            <option value="ceo">CEO Agent</option>
            <option value="marketing">Marketing Agent</option>
            <option value="support">Support Agent</option>
            <option value="finance">Finance Agent</option>
          </select>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'knowledge' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Knowledge Base</h2>
            <button 
              onClick={() => handleMemoryAction('add_knowledge')}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Knowledge
            </button>
          </div>

          <div className="grid gap-6">
            {filteredKnowledge.map((item) => {
              const TypeIcon = getTypeIcon(item.type);
              return (
                <div key={item.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start space-x-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                          <TypeIcon className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">{item.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                            <span>{item.category}</span>
                            <span>•</span>
                            <span>{item.size}</span>
                            <span>•</span>
                            <span>{item.entries.toLocaleString()} entries</span>
                            <span>•</span>
                            <span>Updated {item.lastUpdated}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(item.status)}`}>
                          {item.status}
                        </span>
                        <button
                          onClick={() => setExpandedMemory(expandedMemory === item.id ? null : item.id)}
                          className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          {expandedMemory === item.id ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                        </button>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {item.tags.map((tag, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                          #{tag}
                        </span>
                      ))}
                    </div>

                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div className="text-center">
                        <div className="font-medium text-gray-900">{item.accuracy}%</div>
                        <div className="text-gray-600">Accuracy</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-gray-900">{item.usage}</div>
                        <div className="text-gray-600">Usage Count</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-gray-900">{item.vectorEmbeddings.toLocaleString()}</div>
                        <div className="text-gray-600">Embeddings</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-gray-900">{item.lastAccessed}</div>
                        <div className="text-gray-600">Last Accessed</div>
                      </div>
                    </div>

                    {expandedMemory === item.id && (
                      <div className="mt-6 pt-6 border-t border-gray-200">
                        <div className="grid md:grid-cols-2 gap-6">
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-3">Memory Details</h4>
                            <div className="space-y-2 text-sm">
                              <div className="flex justify-between">
                                <span className="text-gray-600">Source:</span>
                                <span className="text-gray-900">{item.source}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Agent:</span>
                                <span className="text-gray-900">{item.agent}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Type:</span>
                                <span className="text-gray-900 capitalize">{item.type}</span>
                              </div>
                            </div>
                          </div>
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-3">Actions</h4>
                            <div className="flex flex-wrap gap-2">
                              <button 
                                onClick={() => handleMemoryAction('view', item.id)}
                                className="inline-flex items-center px-3 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
                              >
                                <Eye className="h-3 w-3 mr-1" />
                                View
                              </button>
                              <button 
                                onClick={() => handleMemoryAction('edit', item.id)}
                                className="inline-flex items-center px-3 py-1 text-xs font-medium text-gray-600 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
                              >
                                <Edit className="h-3 w-3 mr-1" />
                                Edit
                              </button>
                              <button 
                                onClick={() => handleMemoryAction('download', item.id)}
                                className="inline-flex items-center px-3 py-1 text-xs font-medium text-green-600 bg-green-50 rounded hover:bg-green-100 transition-colors"
                              >
                                <Download className="h-3 w-3 mr-1" />
                                Export
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {activeTab === 'conversations' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Conversational Memory</h2>
            <button 
              onClick={() => handleMemoryAction('clear_old_conversations')}
              className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear Old
            </button>
          </div>

          <div className="grid gap-6">
            {conversationalMemory.map((memory) => (
              <div key={memory.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start space-x-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <MessageSquare className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{memory.agentName}</h3>
                      <p className="text-sm text-gray-600">{memory.context}</p>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <span>ID: {memory.conversationId}</span>
                        <span>•</span>
                        <span>{memory.interactions} interactions</span>
                        <span>•</span>
                        <span>Last: {memory.lastInteraction}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(memory.status)}`}>
                      {memory.status}
                    </span>
                    <span className={`text-sm font-medium ${getSentimentColor(memory.sentiment)}`}>
                      {memory.sentiment}
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Key Points:</h4>
                  <ul className="space-y-1">
                    {memory.keyPoints.map((point, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start">
                        <div className="w-1 h-1 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-2">
                    {memory.tags.map((tag, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                        #{tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="text-center">
                      <div className="font-medium text-gray-900">{memory.memoryStrength}%</div>
                      <div className="text-gray-600">Strength</div>
                    </div>
                    <div className="text-center">
                      <div className={`font-medium ${
                        memory.priority === 'high' ? 'text-red-600' :
                        memory.priority === 'medium' ? 'text-yellow-600' :
                        'text-green-600'
                      }`}>
                        {memory.priority}
                      </div>
                      <div className="text-gray-600">Priority</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'procedures' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Procedural Memory</h2>
            <button 
              onClick={() => handleMemoryAction('create_procedure')}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Procedure
            </button>
          </div>

          <div className="grid gap-6">
            {proceduralMemory.map((procedure) => {
              const TypeIcon = getTypeIcon(procedure.type);
              return (
                <div key={procedure.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-purple-100 rounded-lg">
                        <TypeIcon className="h-5 w-5 text-purple-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{procedure.name}</h3>
                        <p className="text-sm text-gray-600">{procedure.description}</p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                          <span>{procedure.agent}</span>
                          <span>•</span>
                          <span>{procedure.steps} steps</span>
                          <span>•</span>
                          <span>Last executed: {procedure.lastExecuted}</span>
                        </div>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(procedure.status)}`}>
                      {procedure.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-4 gap-4 mb-4 text-sm">
                    <div className="text-center">
                      <div className="font-medium text-gray-900">{procedure.successRate}%</div>
                      <div className="text-gray-600">Success Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium text-gray-900">{procedure.avgDuration}</div>
                      <div className="text-gray-600">Avg Duration</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium text-gray-900">{procedure.executions}</div>
                      <div className="text-gray-600">Executions</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium text-gray-900">{procedure.type}</div>
                      <div className="text-gray-600">Type</div>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-2">Triggers:</h4>
                      <div className="flex flex-wrap gap-1">
                        {procedure.triggers.map((trigger, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-md">
                            {trigger}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-2">Outputs:</h4>
                      <div className="flex flex-wrap gap-1">
                        {procedure.outputs.map((output, index) => (
                          <span key={index} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-md">
                            {output}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {activeTab === 'connections' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Memory Connections</h2>
            <button 
              onClick={() => handleMemoryAction('analyze_connections')}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Network className="h-4 w-4 mr-2" />
              Analyze
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Memory Network Graph</h3>
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Network className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600">Interactive memory network visualization</p>
                <p className="text-sm text-gray-500">Showing relationships between knowledge bases, conversations, and procedures</p>
              </div>
            </div>
          </div>

          <div className="grid gap-4">
            {memoryConnections.map((connection) => (
              <div key={connection.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-sm font-medium text-gray-900">{connection.source}</div>
                    <ArrowRight className="h-4 w-4 text-gray-400" />
                    <div className="text-sm font-medium text-gray-900">{connection.target}</div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-sm text-gray-600">
                      Strength: <span className="font-medium">{(connection.strength * 100).toFixed(0)}%</span>
                    </div>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      {connection.type}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-2">{connection.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-gray-900">Memory Analytics</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Memory Usage Trends</h3>
              <div className="h-48 bg-gray-50 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">Memory usage over time</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Retrieval Performance</h3>
              <div className="h-48 bg-gray-50 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <TrendingUp className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">Response time and accuracy metrics</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Memory Health Score</h3>
            <div className="grid md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">A+</div>
                <div className="text-sm text-gray-600">Overall Health</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">96.8%</div>
                <div className="text-sm text-gray-600">Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">0.3s</div>
                <div className="text-sm text-gray-600">Avg Retrieval</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600">28%</div>
                <div className="text-sm text-gray-600">Storage Used</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MemoryHub;