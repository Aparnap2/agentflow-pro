import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Plus, 
  Settings, 
  Play, 
  Pause, 
  MoreVertical,
  Users,
  Zap,
  Brain,
  Target,
  Edit3,
  AlertCircle,
  Loader
} from 'lucide-react';
import { useAgents } from '../hooks/useApi';

const AgentStudio: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  interface AgentData {
    name: string;
    role: string;
    goal: string;
    backstory: string;
    verbose: boolean;
    allow_delegation: boolean;
    tools: string[];
    llm_config: {
      model: string;
    };
  }

  const [newAgentData, setNewAgentData] = useState<AgentData>({
    name: '',
    role: '',
    goal: '',
    backstory: '',
    verbose: false,
    allow_delegation: false,
    tools: [],
    llm_config: { model: 'gemini-pro' }
  });

  // Use the custom hook to fetch agents from the API
  const { agents, loading, error, fetchAgents, createAgent, processTask } = useAgents();

  // Map backend agents to UI format
  const agentTemplates = agents.map(agent => ({
    id: agent.id,
    name: agent.name,
    description: agent.goal,
    category: agent.role,
    capabilities: agent.tools || [],
    status: 'active',
    tasksCompleted: 0,
    successRate: '0%'
  }));

  // If no agents are loaded yet, use some default categories
  const categories = ['All', 'Strategic & Managerial', 'Customer & Sales', 'Content & Marketing', 'Operations & Finance'];
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Get unique categories from the agents
  useEffect(() => {
    if (agents.length > 0) {
      const uniqueCategories = ['All', ...new Set(agents.map(agent => agent.role))];
      // We don't need to update the categories state here as it would cause a re-render loop
    }
  }, [agents]);

  const filteredAgents = selectedCategory === 'All' 
    ? agentTemplates 
    : agentTemplates.filter(agent => agent.category === selectedCategory);
    
  const handleCreateAgent = async () => {
    try {
      await createAgent(newAgentData);
      setShowCreateModal(false);
      setNewAgentData({
        name: '',
        role: '',
        goal: '',
        backstory: '',
        verbose: false,
        allow_delegation: false,
        tools: [],
        llm_config: { model: 'gemini-pro' }
      });
    } catch (err) {
      console.error('Failed to create agent:', err);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Agent Studio</h1>
          <p className="text-gray-600">Configure and manage your AI agent teams</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Custom Agent
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
          <AlertCircle className="h-5 w-5 text-red-500 mr-3 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-medium text-red-800">Error loading agents</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button 
              onClick={fetchAgents}
              className="mt-2 text-sm font-medium text-red-600 hover:text-red-800"
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div className="mb-8">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <Loader className="h-8 w-8 text-blue-500 animate-spin" />
          <span className="ml-3 text-gray-600">Loading agents...</span>
        </div>
      )}

      {/* Empty state */}
      {!loading && agentTemplates.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-xl border border-gray-200">
          <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No agents found</h3>
          <p className="text-gray-600 mb-6">You haven't created any agents yet.</p>
          <button 
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create your first agent
          </button>
        </div>
      )}

      {/* Agent Grid */}
      {!loading && agentTemplates.length > 0 && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {filteredAgents.map((agent) => (
            <div key={agent.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`p-3 rounded-lg ${
                      agent.status === 'active' ? 'bg-green-100' : 
                      agent.status === 'paused' ? 'bg-yellow-100' : 'bg-gray-100'
                    }`}>
                      <Bot className={`h-6 w-6 ${
                        agent.status === 'active' ? 'text-green-600' : 
                        agent.status === 'paused' ? 'text-yellow-600' : 'text-gray-600'
                      }`} />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                      <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">{agent.category}</span>
                    </div>
                  </div>
                  <div className="relative">
                    <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
                      <MoreVertical className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                <p className="text-gray-600 mb-4 text-sm">{agent.description}</p>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Tasks Completed:</span>
                    <span className="font-medium text-gray-900">{agent.tasksCompleted}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Success Rate:</span>
                    <span className="font-medium text-green-600">{agent.successRate}</span>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Capabilities:</p>
                  <div className="flex flex-wrap gap-1">
                    {agent.capabilities.map((capability: string | number | boolean | React.ReactElement<any, string | React.JSXElementConstructor<any>> | Iterable<React.ReactNode> | React.ReactPortal | null | undefined, index: React.Key | null | undefined) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                      >
                        {capability}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    agent.status === 'active' ? 'bg-green-100 text-green-800' : 
                    agent.status === 'paused' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {agent.status === 'active' && <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>}
                    {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
                      <Settings className="h-4 w-4" />
                    </button>
                    <button 
                      onClick={() => processTask(agent.id, "Hello, what can you do?", {})}
                      className={`p-2 rounded-lg transition-colors ${
                        agent.status === 'active' 
                          ? 'text-yellow-600 hover:bg-yellow-50' 
                          : 'text-green-600 hover:bg-green-50'
                      }`}
                    >
                      {agent.status === 'active' ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Agent Configuration Panel */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Configuration</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center p-6 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer">
            <Brain className="h-8 w-8 text-blue-600 mx-auto mb-3" />
            <h3 className="font-medium text-gray-900 mb-2">Training & Learning</h3>
            <p className="text-sm text-gray-600">Configure agent knowledge base and learning parameters</p>
          </div>
          <div className="text-center p-6 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-colors cursor-pointer">
            <Zap className="h-8 w-8 text-purple-600 mx-auto mb-3" />
            <h3 className="font-medium text-gray-900 mb-2">Integrations</h3>
            <p className="text-sm text-gray-600">Connect agents to your existing tools and APIs</p>
          </div>
          <div className="text-center p-6 border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors cursor-pointer">
            <Target className="h-8 w-8 text-green-600 mx-auto mb-3" />
            <h3 className="font-medium text-gray-900 mb-2">Goals & KPIs</h3>
            <p className="text-sm text-gray-600">Set performance targets and success metrics</p>
          </div>
          <div className="text-center p-6 border border-gray-200 rounded-lg hover:border-orange-300 hover:bg-orange-50 transition-colors cursor-pointer">
            <Edit3 className="h-8 w-8 text-orange-600 mx-auto mb-3" />
            <h3 className="font-medium text-gray-900 mb-2">Custom Rules</h3>
            <p className="text-sm text-gray-600">Define custom behavior rules and constraints</p>
          </div>
        </div>
      </div>

      {/* Team Collaboration */}
      <div className="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Agent Team Collaboration</h3>
            <p className="text-gray-600">Configure how your agents work together on complex tasks</p>
          </div>
          <Users className="h-8 w-8 text-purple-600" />
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Hierarchical Teams</h4>
            <p className="text-sm text-gray-600">Set up supervisor-worker relationships for complex projects</p>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Peer Collaboration</h4>
            <p className="text-sm text-gray-600">Enable agents to work together as equals on shared tasks</p>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Knowledge Sharing</h4>
            <p className="text-sm text-gray-600">Allow agents to share insights and learnings across teams</p>
          </div>
        </div>
      </div>
      {/* Create Agent Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Create New Agent</h2>
                <button 
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Agent Name</label>
                  <input
                    type="text"
                    value={newAgentData.name}
                    onChange={(e) => setNewAgentData({...newAgentData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Research Assistant"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                  <input
                    type="text"
                    value={newAgentData.role}
                    onChange={(e) => setNewAgentData({...newAgentData, role: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Researcher"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Goal</label>
                  <textarea
                    value={newAgentData.goal}
                    onChange={(e) => setNewAgentData({...newAgentData, goal: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="e.g., Find and analyze information on specific topics"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Backstory (Optional)</label>
                  <textarea
                    value={newAgentData.backstory}
                    onChange={(e) => setNewAgentData({...newAgentData, backstory: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={2}
                    placeholder="e.g., A dedicated researcher with expertise in data analysis"
                  />
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="verbose"
                      checked={newAgentData.verbose}
                      onChange={(e) => setNewAgentData({...newAgentData, verbose: e.target.checked})}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="verbose" className="ml-2 block text-sm text-gray-700">Verbose Mode</label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="delegation"
                      checked={newAgentData.allow_delegation}
                      onChange={(e) => setNewAgentData({...newAgentData, allow_delegation: e.target.checked})}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="delegation" className="ml-2 block text-sm text-gray-700">Allow Delegation</label>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tools</label>
                  <div className="flex flex-wrap gap-2 p-3 border border-gray-300 rounded-md">
                    {['web_search', 'knowledge_base', 'data_analysis', 'code_interpreter', 'file_manager'].map((tool) => (
                      <div key={tool} className="flex items-center">
                        <input
                          type="checkbox"
                          id={`tool-${tool}`}
                          checked={newAgentData.tools.includes(tool)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setNewAgentData({
                                ...newAgentData, 
                                tools: [...newAgentData.tools, tool]
                              });
                            } else {
                              setNewAgentData({
                                ...newAgentData,
                                tools: newAgentData.tools.filter(t => t !== tool)
                              });
                            }
                          }}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor={`tool-${tool}`} className="ml-2 block text-sm text-gray-700">
                          {tool.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">LLM Model</label>
                  <select
                    value={newAgentData.llm_config.model}
                    onChange={(e) => setNewAgentData({
                      ...newAgentData,
                      llm_config: {...newAgentData.llm_config, model: e.target.value}
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="gemini-pro">Gemini Pro</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="claude-3-opus">Claude 3 Opus</option>
                    <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                  </select>
                </div>
              </div>
              
              <div className="mt-8 flex justify-end space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateAgent}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Create Agent
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentStudio;