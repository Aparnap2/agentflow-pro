import React, { useState } from 'react';

interface Agent {
  id: string;
  name: string;
  description: string;
  category: string;
  capabilities: string[];
  model: string;
  temperature: number;
  maxTokens: number;
  tools: string[];
  integrations: string[];
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  status: string;
  deployments: number;
  successRate: string;
  avgResponseTime: string;
  lastUpdated: string;
  version: string;
  performance: {
    accuracy: number;
    efficiency: number;
    reliability: number;
    userSatisfaction: number;
  };
  costPerTask: string;
  complexity: string;
}
import { 
  Bot, 
  Plus, 
  Settings, 
  Play, 
  MoreVertical,
  Users,
  Brain,
  Target,
  Factory,
  Code,
  DollarSign,
  UserCheck,
  TrendingUp,
  Headphones,
  Briefcase,
  PieChart,
  Palette,
  Building,
  CheckCircle,
  Clock,
  Activity,
  Search,
  Filter,
  Eye,
  Copy,
  Trash2,
  Download,
  Upload,
  BarChart} from 'lucide-react';

// Define the form state type
interface AgentFormState {
  name: string;
  description: string;
  category: string;
  capabilities: string[];
  model: string;
  temperature: number;
  maxTokens: number;
  tools: string[];
  integrations: string[];
}

const AgentFactory: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [newAgentForm, setNewAgentForm] = useState<AgentFormState>({
    name: '',
    description: '',
    category: '',
    capabilities: [],
    model: 'gemini',
    temperature: 0.7,
    maxTokens: 2048,
    tools: [],
    integrations: []
  });

  // Helper function to ensure all agent templates have the required properties
  const createAgentTemplate = (
template: Omit<Agent, 'model' | 'temperature' | 'maxTokens' | 'tools' | 'integrations' | 'performance' | 'id' | 'icon' | 'color' | 'status' | 'deployments' | 'successRate' | 'avgResponseTime' | 'lastUpdated' | 'version' | 'costPerTask' | 'complexity'> &
  Partial<Pick<Agent, 'id' | 'icon' | 'color' | 'status' | 'deployments' | 'successRate' | 'avgResponseTime' | 'lastUpdated' | 'version' | 'costPerTask' | 'complexity' | 'tools' | 'integrations' | 'performance'>>, _p0?: unknown, _p1?: unknown, _p2?: unknown, _p3?: unknown, _p4?: unknown, _p5?: unknown, _p6?: unknown, _p7?: unknown, _p8?: unknown, _p9?: unknown, _p10?: unknown, _p11?: unknown, _p12?: unknown  ): Agent => {
    const now = new Date().toISOString();
    return {
      ...template,
      id: template.id || `agent-${Math.random().toString(36).substr(2, 9)}`,
      model: 'gpt-4',
      temperature: 0.7,
      maxTokens: 2048,
      tools: template.tools || [],
      integrations: template.integrations || [],
      icon: template.icon || Bot,
      color: template.color || 'gray',
      status: template.status || 'active',
      deployments: template.deployments || 0,
      successRate: template.successRate || '0%',
      avgResponseTime: template.avgResponseTime || '0s',
      lastUpdated: template.lastUpdated || now,
      version: template.version || '1.0.0',
      costPerTask: template.costPerTask || '$0.00',
      complexity: template.complexity || 'Medium',
      performance: template.performance || {
        accuracy: 0,
        efficiency: 0,
        reliability: 0,
        userSatisfaction: 0
      }
    };
  };

  // Base agent template with all required fields
  const baseAgentTemplate = {
    icon: Bot,
    color: 'gray',
    status: 'active',
    deployments: 0,
    successRate: '0%',
    avgResponseTime: '0s',
    lastUpdated: new Date().toISOString(),
    version: '1.0.0',
    costPerTask: '$0.00',
    complexity: 'Medium',
    performance: {
      accuracy: 0,
      efficiency: 0,
      reliability: 0,
      userSatisfaction: 0
    }
  };

  // Create agent templates using the createAgentTemplate function
  const agentTemplates: Agent[] = [
    createAgentTemplate({
      ...baseAgentTemplate,
      id: 'ceo_agent',
      name: 'CEO Agent',
      description: 'Strategic decision making, high-level planning, and executive oversight',
      category: 'Executive',
      icon: Building,
      color: 'purple',
      capabilities: ['Strategic Planning', 'Decision Making', 'Executive Leadership', 'Vision Setting'],
      status: 'active',
      deployments: 5,
      successRate: '98%',
      avgResponseTime: '1.2s',
      costPerTask: '$1.25',
      complexity: 'High',
      tools: ['Decision Matrix', 'SWOT Analyzer', 'Market Analysis'],
      integrations: ['Slack', 'Notion', 'Google Workspace'],
      lastUpdated: '2 days ago',
      version: '2.1.0',
      performance: {
        accuracy: 95,
        efficiency: 92,
        reliability: 97,
        userSatisfaction: 94
      }
    }),
    createAgentTemplate( {
      id: 'cofounder_agent',
      name: 'Co-Founder Agent',
      description: 'Product strategy, market analysis, and business development',
      category: 'Executive',
      icon: Users,
      color: 'indigo',
      capabilities: ['Product Strategy', 'Market Analysis', 'Business Development', 'Partnership Management', 'Investor Relations'],
      status: 'active',
      deployments: 8,
      successRate: '94%',
      avgResponseTime: '1.8s',
      costPerTask: '$0.38',
      complexity: 'High',
      tools: ['Market Intelligence', 'Competitor Analysis', 'Partnership CRM'],
      integrations: ['HubSpot', 'LinkedIn', 'Zoom'],
      lastUpdated: '1 week ago',
      version: '1.8.2',
      performance: {
        accuracy: 94,
        efficiency: 92,
        reliability: 96,
        userSatisfaction: 93
      },
    }),
    {
      id: 'manager_agent',
      name: 'Manager Agent',
      description: 'Team coordination, project management, and operational oversight',
      category: 'Management',
      icon: Briefcase,
      color: 'blue',
      capabilities: ['Team Management', 'Project Coordination', 'Resource Allocation', 'Performance Tracking', 'Meeting Management'],
      status: 'active',
      deployments: 25,
      successRate: '92%',
      avgResponseTime: '1.5s',
      costPerTask: '$0.28',
      complexity: 'Medium',
      tools: ['Project Management', 'Team Analytics', 'Resource Planner'],
      integrations: ['Asana', 'Trello', 'Microsoft Teams'],
      lastUpdated: '3 days ago',
      version: '3.2.1',
      performance: {
        accuracy: 92,
        efficiency: 90,
        reliability: 94,
        userSatisfaction: 91
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'strategic_agent',
      name: 'Strategic Agent',
      description: 'Long-term planning, competitive analysis, and strategic initiatives',
      category: 'Strategy',
      icon: Target,
      color: 'emerald',
      capabilities: ['Strategic Planning', 'Competitive Analysis', 'Market Research', 'SWOT Analysis', 'Roadmap Planning'],
      status: 'active',
      deployments: 15,
      successRate: '95%',
      avgResponseTime: '3.2s',
      costPerTask: '$0.52',
      complexity: 'High',
      tools: ['Strategic Framework', 'Market Scanner', 'Competitive Intelligence'],
      integrations: ['Google Analytics', 'SEMrush', 'Tableau'],
      lastUpdated: '5 days ago',
      version: '2.0.3',
      performance: {
        accuracy: 95,
        efficiency: 88,
        reliability: 97,
        userSatisfaction: 94
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'finance_agent',
      name: 'Finance Agent',
      description: 'Financial analysis, budgeting, forecasting, and reporting',
      category: 'Finance',
      icon: DollarSign,
      color: 'green',
      capabilities: ['Financial Analysis', 'Budget Planning', 'Forecasting', 'Risk Assessment', 'Compliance Monitoring'],
      status: 'active',
      deployments: 18,
      successRate: '98%',
      avgResponseTime: '1.2s',
      costPerTask: '$0.22',
      complexity: 'Medium',
      tools: ['Financial Calculator', 'Budget Analyzer', 'Risk Assessor'],
      integrations: ['QuickBooks', 'Stripe', 'Xero'],
      lastUpdated: '1 day ago',
      version: '4.1.2',
      performance: {
        accuracy: 98,
        efficiency: 96,
        reliability: 99,
        userSatisfaction: 97
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'hr_agent',
      name: 'HR Agent',
      description: 'Human resources management, recruitment, and employee relations',
      category: 'Human Resources',
      icon: UserCheck,
      color: 'pink',
      capabilities: ['Recruitment', 'Employee Relations', 'Policy Management', 'Training Coordination', 'Benefits Administration'],
      status: 'active',
      deployments: 22,
      successRate: '91%',
      avgResponseTime: '1.8s',
      costPerTask: '$0.31',
      complexity: 'Medium',
      tools: ['Recruitment Platform', 'Employee Database', 'Policy Manager'],
      integrations: ['BambooHR', 'LinkedIn Recruiter', 'Workday'],
      lastUpdated: '4 days ago',
      version: '2.5.1',
      performance: {
        accuracy: 91,
        efficiency: 89,
        reliability: 93,
        userSatisfaction: 90
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'hr_agent_performance',
      name: 'HR Performance Agent',
      description: 'Performance evaluation, goal setting, and employee development',
      category: 'Human Resources',
      icon: TrendingUp,
      color: 'orange',
      capabilities: ['Performance Reviews', 'Goal Setting', 'Development Planning', 'Feedback Management', '360 Reviews'],
      status: 'active',
      deployments: 14,
      successRate: '93%',
      avgResponseTime: '2.1s',
      costPerTask: '$0.35',
      complexity: 'Medium',
      tools: ['Performance Tracker', 'Goal Manager', 'Feedback Collector'],
      integrations: ['15Five', 'Lattice', 'Culture Amp'],
      lastUpdated: '6 days ago',
      version: '1.9.0',
      performance: {
        accuracy: 93,
        efficiency: 87,
        reliability: 95,
        userSatisfaction: 92
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'hr_agent_leave',
      name: 'HR Leave Management Agent',
      description: 'Leave requests, attendance tracking, and time-off management',
      category: 'Human Resources',
      icon: Clock,
      color: 'yellow',
      capabilities: ['Leave Processing', 'Attendance Tracking', 'Policy Enforcement', 'Calendar Management', 'Approval Workflows'],
      status: 'active',
      deployments: 19,
      successRate: '97%',
      avgResponseTime: '0.8s',
      costPerTask: '$0.18',
      complexity: 'Low',
      tools: ['Leave Calculator', 'Attendance Monitor', 'Calendar Sync'],
      integrations: ['Google Calendar', 'Outlook', 'Toggl'],
      lastUpdated: '2 days ago',
      version: '3.0.1',
      performance: {
        accuracy: 97,
        efficiency: 95,
        reliability: 98,
        userSatisfaction: 96
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'hr_agent_training',
      name: 'HR Training Agent',
      description: 'Training programs, skill development, and learning management',
      category: 'Human Resources',
      icon: Brain,
      color: 'purple',
      capabilities: ['Training Design', 'Skill Assessment', 'Learning Paths', 'Progress Tracking', 'Certification Management'],
      status: 'active',
      deployments: 11,
      successRate: '89%',
      avgResponseTime: '2.5s',
      costPerTask: '$0.42',
      complexity: 'Medium',
      tools: ['Learning Management System', 'Skill Assessor', 'Training Scheduler'],
      integrations: ['Coursera', 'Udemy', 'LinkedIn Learning'],
      lastUpdated: '1 week ago',
      version: '2.2.3',
      performance: {
        accuracy: 89,
        efficiency: 85,
        reliability: 91,
        userSatisfaction: 88
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'marketing_agent',
      name: 'Marketing Agent',
      description: 'Campaign management, content creation, and brand strategy',
      category: 'Marketing',
      icon: TrendingUp,
      color: 'red',
      capabilities: ['Campaign Management', 'Content Creation', 'Brand Strategy', 'Market Analysis', 'Social Media Management'],
      status: 'active',
      deployments: 28,
      successRate: '90%',
      avgResponseTime: '1.9s',
      costPerTask: '$0.33',
      complexity: 'Medium',
      tools: ['Content Generator', 'Campaign Manager', 'Analytics Dashboard'],
      integrations: ['Mailchimp', 'Hootsuite', 'Google Ads'],
      lastUpdated: '3 days ago',
      version: '3.1.4',
      performance: {
        accuracy: 90,
        efficiency: 88,
        reliability: 92,
        userSatisfaction: 89
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'sales_agent',
      name: 'Sales Agent',
      description: 'Lead generation, customer outreach, and sales pipeline management',
      category: 'Sales',
      icon: Target,
      color: 'blue',
      capabilities: ['Lead Generation', 'Customer Outreach', 'Pipeline Management', 'Deal Closing', 'CRM Management'],
      status: 'active',
      deployments: 32,
      successRate: '88%',
      avgResponseTime: '1.4s',
      costPerTask: '$0.26',
      complexity: 'Medium',
      tools: ['Lead Finder', 'Email Sequencer', 'Pipeline Tracker'],
      integrations: ['Salesforce', 'HubSpot', 'Pipedrive'],
      lastUpdated: '2 days ago',
      version: '4.0.2',
      performance: {
        accuracy: 88,
        efficiency: 91,
        reliability: 89,
        userSatisfaction: 87
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'support_agent',
      name: 'Support Agent',
      description: 'Customer support, issue resolution, and help desk management',
      category: 'Support',
      icon: Headphones,
      color: 'teal',
      capabilities: ['Issue Resolution', 'Customer Communication', 'Ticket Management', 'Knowledge Base', 'Escalation Management'],
      status: 'active',
      deployments: 45,
      successRate: '94%',
      avgResponseTime: '0.9s',
      costPerTask: '$0.19',
      complexity: 'Low',
      tools: ['Ticket System', 'Knowledge Base', 'Chat Interface'],
      integrations: ['Zendesk', 'Intercom', 'Freshdesk'],
      lastUpdated: '1 day ago',
      version: '5.2.1',
      performance: {
        accuracy: 94,
        efficiency: 93,
        reliability: 96,
        userSatisfaction: 95
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'dev_agent',
      name: 'Development Agent',
      description: 'Code generation, testing, debugging, and technical documentation',
      category: 'Development',
      icon: Code,
      color: 'gray',
      capabilities: ['Code Generation', 'Testing', 'Debugging', 'Documentation', 'Code Review'],
      status: 'active',
      deployments: 16,
      successRate: '92%',
      avgResponseTime: '2.8s',
      costPerTask: '$0.48',
      complexity: 'High',
      tools: ['Code Generator', 'Test Runner', 'Documentation Builder'],
      integrations: ['GitHub', 'GitLab', 'Jira'],
      lastUpdated: '5 days ago',
      version: '2.8.0',
      performance: {
        accuracy: 92,
        efficiency: 86,
        reliability: 94,
        userSatisfaction: 90
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'design_agent',
      name: 'Design Agent',
      description: 'UI/UX design, visual assets, and design system management',
      category: 'Design',
      icon: Palette,
      color: 'pink',
      capabilities: ['UI/UX Design', 'Visual Assets', 'Design Systems', 'Prototyping', 'User Research'],
      status: 'active',
      deployments: 9,
      successRate: '87%',
      avgResponseTime: '3.5s',
      costPerTask: '$0.55',
      complexity: 'High',
      tools: ['Design Generator', 'Prototype Builder', 'Asset Manager'],
      integrations: ['Figma', 'Sketch', 'Adobe Creative Suite'],
      lastUpdated: '1 week ago',
      version: '1.6.2',
      performance: {
        accuracy: 87,
        efficiency: 83,
        reliability: 89,
        userSatisfaction: 86
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    },
    {
      id: 'analytics_agent',
      name: 'Analytics Agent',
      description: 'Data analysis, reporting, insights generation, and visualization',
      category: 'Analytics',
      icon: PieChart,
      color: 'indigo',
      capabilities: ['Data Analysis', 'Report Generation', 'Insights', 'Visualization', 'Predictive Analytics'],
      status: 'active',
      deployments: 21,
      successRate: '96%',
      avgResponseTime: '2.2s',
      costPerTask: '$0.39',
      complexity: 'Medium',
      tools: ['Data Processor', 'Chart Generator', 'Insight Engine'],
      integrations: ['Google Analytics', 'Tableau', 'Power BI'],
      lastUpdated: '4 days ago',
      version: '3.4.1',
      performance: {
        accuracy: 96,
        efficiency: 94,
        reliability: 97,
        userSatisfaction: 95
      },
      model: '',
      temperature: 0,
      maxTokens: 0
    }
  ];

  const categories = ['All', 'Executive', 'Management', 'Strategy', 'Finance', 'Human Resources', 'Marketing', 'Sales', 'Support', 'Development', 'Design', 'Analytics'];

  const filteredAgents = agentTemplates.filter(agent => {
    const matchesCategory = selectedCategory === 'All' || agent.category === selectedCategory;
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.capabilities.some(cap => cap.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const getColorClasses = (color: string) => {
    const colorMap: { [key: string]: { bg: string; text: string; border: string } } = {
      purple: { bg: 'bg-purple-100', text: 'text-purple-600', border: 'border-purple-200' },
      indigo: { bg: 'bg-indigo-100', text: 'text-indigo-600', border: 'border-indigo-200' },
      blue: { bg: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-200' },
      emerald: { bg: 'bg-emerald-100', text: 'text-emerald-600', border: 'border-emerald-200' },
      green: { bg: 'bg-green-100', text: 'text-green-600', border: 'border-green-200' },
      pink: { bg: 'bg-pink-100', text: 'text-pink-600', border: 'border-pink-200' },
      orange: { bg: 'bg-orange-100', text: 'text-orange-600', border: 'border-orange-200' },
      yellow: { bg: 'bg-yellow-100', text: 'text-yellow-600', border: 'border-yellow-200' },
      red: { bg: 'bg-red-100', text: 'text-red-600', border: 'border-red-200' },
      teal: { bg: 'bg-teal-100', text: 'text-teal-600', border: 'border-teal-200' },
      gray: { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-200' }
    };
    return colorMap[color] || colorMap.blue;
  };

  const handleCreateAgent = () => {
    // Create a new agent with form data and default values
    const newAgent: Agent = {
      ...newAgentForm,
      id: `agent-${Math.random().toString(36).substr(2, 9)}`, // Generate a unique ID
      icon: Bot, // Default icon
      color: 'blue', // Default color
      status: 'inactive',
      deployments: 0,
      successRate: '0%',
      avgResponseTime: '0s',
      lastUpdated: new Date().toISOString(),
      version: '1.0.0',
      performance: {
        accuracy: 0,
        efficiency: 0,
        reliability: 0,
        userSatisfaction: 0
      },
      costPerTask: '$0.00',
      complexity: 'medium'
    };

    console.log('Creating agent:', newAgent);
    setShowCreateModal(false);
    
    // Reset the form
    setNewAgentForm({
      name: '',
      description: '',
      category: '',
      capabilities: [],
      model: 'gemini',
      temperature: 0.7,
      maxTokens: 2048,
      tools: [],
      integrations: []
    });
  };

  const handleAgentAction = (agentId: string, action: string) => {
    console.log(`${action} agent ${agentId}`);
  };

  const handleCloneAgent = (agent: Agent) => {
    // Clone only the form-relevant properties
    const { 
      name, 
      description, 
      category, 
      capabilities, 
      model, 
      temperature, 
      maxTokens, 
      tools, 
      integrations 
    } = agent;
    
    setNewAgentForm({
      name: `${name} (Copy)`,
      description,
      category,
      capabilities: [...capabilities],
      model,
      temperature,
      maxTokens,
      tools: [...tools],
      integrations: [...integrations]
    });
    setShowCreateModal(true);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Agent Factory</h1>
          <p className="text-gray-600">Create, deploy, and manage specialized AI agents for your business needs</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => console.log('Import agent')}
            className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Upload className="h-4 w-4 mr-2" />
            Import Agent
          </button>
          <button 
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Create Custom Agent
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Agents</p>
              <p className="text-2xl font-bold text-gray-900">{agentTemplates.length}</p>
              <p className="text-xs text-green-600 mt-1">+3 this week</p>
            </div>
            <Factory className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Deployments</p>
              <p className="text-2xl font-bold text-gray-900">{agentTemplates.reduce((sum, agent) => sum + agent.deployments, 0)}</p>
              <p className="text-xs text-green-600 mt-1">+15% this month</p>
            </div>
            <Activity className="h-8 w-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">93.2%</p>
              <p className="text-xs text-green-600 mt-1">+2.1% improvement</p>
            </div>
            <CheckCircle className="h-8 w-8 text-emerald-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Cost/Task</p>
              <p className="text-2xl font-bold text-gray-900">$0.34</p>
              <p className="text-xs text-red-600 mt-1">-8% cost reduction</p>
            </div>
            <DollarSign className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="mb-8 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search agents by name, description, or capabilities..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-gray-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents.map((agent) => {
          const colors = getColorClasses(agent.color);
          return (
            <div key={agent.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`p-3 rounded-lg ${colors.bg}`}>
                      <agent.icon className={`h-6 w-6 ${colors.text}`} />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">{agent.category}</span>
                        <span className="text-xs text-gray-500">v{agent.version}</span>
                      </div>
                    </div>
                  </div>
                  <div className="relative">
                    <button 
                      onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                      className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                    >
                      <MoreVertical className="h-5 w-5" />
                    </button>
                    {selectedAgent === agent.id && (
                      <div className="absolute right-0 top-10 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                        <div className="py-1">
                          <button 
                            onClick={() => handleAgentAction(agent.id, 'view')}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            View Details
                          </button>
                          <button 
                            onClick={() => handleCloneAgent(agent)}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <Copy className="h-4 w-4 mr-2" />
                            Clone Agent
                          </button>
                          <button 
                            onClick={() => handleAgentAction(agent.id, 'export')}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Export Config
                          </button>
                          <button 
                            onClick={() => handleAgentAction(agent.id, 'analytics')}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <BarChart className="h-4 w-4 mr-2" />
                            View Analytics
                          </button>
                          <hr className="my-1" />
                          <button 
                            onClick={() => handleAgentAction(agent.id, 'delete')}
                            className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete Agent
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <p className="text-gray-600 mb-4 text-sm">{agent.description}</p>

                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                  <div>
                    <span className="text-gray-600">Deployments:</span>
                    <span className="font-medium text-gray-900 ml-1">{agent.deployments}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Success Rate:</span>
                    <span className="font-medium text-green-600 ml-1">{agent.successRate}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Avg Response:</span>
                    <span className="font-medium text-gray-900 ml-1">{agent.avgResponseTime}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Cost/Task:</span>
                    <span className="font-medium text-purple-600 ml-1">{agent.costPerTask}</span>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-gray-700">Complexity:</p>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      agent.complexity === 'High' ? 'bg-red-100 text-red-800' :
                      agent.complexity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {agent.complexity}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {agent.capabilities.slice(0, 3).map((capability, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                      >
                        {capability}
                      </span>
                    ))}
                    {agent.capabilities.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                        +{agent.capabilities.length - 3} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Performance Indicators */}
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Performance:</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Accuracy:</span>
                      <span className="font-medium">{agent.performance.accuracy}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Efficiency:</span>
                      <span className="font-medium">{agent.performance.efficiency}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Reliability:</span>
                      <span className="font-medium">{agent.performance.reliability}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Satisfaction:</span>
                      <span className="font-medium">{agent.performance.userSatisfaction}%</span>
                    </div>
                  </div>
                </div>

                {/* Tools & Integrations */}
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Tools & Integrations:</p>
                  <div className="flex flex-wrap gap-1">
                    {agent.tools.slice(0, 2).map((tool, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md">
                        {tool}
                      </span>
                    ))}
                    {agent.integrations.slice(0, 2).map((integration, index) => (
                      <span key={index} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-md">
                        {integration}
                      </span>
                    ))}
                    {(agent.tools.length + agent.integrations.length) > 4 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                        +{(agent.tools.length + agent.integrations.length) - 4} more
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <div className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                      Active
                    </div>
                    <span className="text-xs text-gray-500">Updated {agent.lastUpdated}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button 
                      onClick={() => handleAgentAction(agent.id, 'configure')}
                      className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                      title="Configure"
                    >
                      <Settings className="h-4 w-4" />
                    </button>
                    <button 
                      onClick={() => handleAgentAction(agent.id, 'deploy')}
                      className="p-2 text-gray-400 hover:text-green-600 rounded-lg hover:bg-green-50 transition-colors"
                      title="Deploy"
                    >
                      <Play className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Create Agent Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowCreateModal(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
                    <Bot className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                      Create Custom Agent
                    </h3>
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Agent Name</label>
                          <input
                            type="text"
                            value={newAgentForm.name}
                            onChange={(e) => setNewAgentForm({...newAgentForm, name: e.target.value})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="e.g., Custom Sales Agent"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                          <select
                            value={newAgentForm.category}
                            onChange={(e) => setNewAgentForm({...newAgentForm, category: e.target.value})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">Select a category</option>
                            {categories.slice(1).map(cat => (
                              <option key={cat} value={cat}>{cat}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <textarea
                          value={newAgentForm.description}
                          onChange={(e) => setNewAgentForm({...newAgentForm, description: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          rows={3}
                          placeholder="Describe what this agent will do..."
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">AI Model</label>
                          <select
                            value={newAgentForm.model}
                            onChange={(e) => setNewAgentForm({...newAgentForm, model: e.target.value})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="gemini">Google Gemini</option>
                            <option value="deepseek">Deepseek v3</option>
                            <option value="qwen">Qwen</option>
                            <option value="gpt-4">GPT-4</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Temperature</label>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={newAgentForm.temperature}
                            onChange={(e) => setNewAgentForm({...newAgentForm, temperature: parseFloat(e.target.value)})}
                            className="w-full"
                          />
                          <div className="text-xs text-gray-500 text-center">{newAgentForm.temperature}</div>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Max Tokens</label>
                        <input
                          type="number"
                          value={newAgentForm.maxTokens}
                          onChange={(e) => setNewAgentForm({...newAgentForm, maxTokens: parseInt(e.target.value)})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          min="256"
                          max="8192"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Capabilities (comma-separated)</label>
                        <input
                          type="text"
                          placeholder="e.g., Data Analysis, Report Generation, Visualization"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          onChange={(e) => setNewAgentForm({
                            ...newAgentForm, 
                            capabilities: e.target.value.split(',').map(cap => cap.trim()).filter(cap => cap)
                          })}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  onClick={handleCreateAgent}
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Create Agent
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentFactory;