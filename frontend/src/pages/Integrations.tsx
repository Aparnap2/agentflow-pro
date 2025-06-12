import React, { useState } from 'react';
import { 
  Zap, 
  CheckCircle, 
  Settings, 
  Plus, 
  ExternalLink,
  Shield,
  AlertCircle,
  Search,
  Filter
} from 'lucide-react';

const Integrations: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const integrations = [
    {
      id: 'slack',
      name: 'Slack',
      description: 'Direct communication, notifications, and agent control within Slack',
      category: 'Communication',
      status: 'connected',
      icon: '💬',
      features: ['Real-time notifications', 'Command interface', 'Status updates'],
      popularity: 'high'
    },
    {
      id: 'salesforce',
      name: 'Salesforce CRM',
      description: 'Sync leads, opportunities, and customer data automatically',
      category: 'CRM',
      status: 'available',
      icon: '🎯',
      features: ['Lead sync', 'Opportunity management', 'Contact updates'],
      popularity: 'high'
    },
    {
      id: 'hubspot',
      name: 'HubSpot',
      description: 'Marketing automation and customer relationship management',
      category: 'CRM',
      status: 'connected',
      icon: '🧲',
      features: ['Contact management', 'Email campaigns', 'Analytics'],
      popularity: 'high'
    },
    {
      id: 'mailchimp',
      name: 'Mailchimp',
      description: 'Email marketing campaigns and audience management',
      category: 'Marketing',
      status: 'available',
      icon: '📧',
      features: ['Email automation', 'Audience segmentation', 'Campaign analytics'],
      popularity: 'medium'
    },
    {
      id: 'stripe',
      name: 'Stripe',
      description: 'Payment processing and subscription management',
      category: 'Finance',
      status: 'connected',
      icon: '💳',
      features: ['Payment tracking', 'Invoice generation', 'Subscription metrics'],
      popularity: 'high'
    },
    {
      id: 'quickbooks',
      name: 'QuickBooks',
      description: 'Accounting and financial data synchronization',
      category: 'Finance',
      status: 'available',
      icon: '📊',
      features: ['Expense tracking', 'Invoice sync', 'Financial reporting'],
      popularity: 'medium'
    },
    {
      id: 'google-workspace',
      name: 'Google Workspace',
      description: 'Gmail, Drive, Calendar, and Docs integration',
      category: 'Productivity',
      status: 'connected',
      icon: '🔧',
      features: ['Email management', 'Document access', 'Calendar sync'],
      popularity: 'high'
    },
    {
      id: 'trello',
      name: 'Trello',
      description: 'Project management and task organization',
      category: 'Project Management',
      status: 'available',
      icon: '📋',
      features: ['Board management', 'Card automation', 'Progress tracking'],
      popularity: 'medium'
    },
    {
      id: 'asana',
      name: 'Asana',
      description: 'Team collaboration and project tracking',
      category: 'Project Management',
      status: 'available',
      icon: '✅',
      features: ['Task automation', 'Team coordination', 'Progress reports'],
      popularity: 'medium'
    },
    {
      id: 'shopify',
      name: 'Shopify',
      description: 'E-commerce store management and order processing',
      category: 'E-commerce',
      status: 'available',
      icon: '🛒',
      features: ['Order processing', 'Inventory sync', 'Customer support'],
      popularity: 'high'
    }
  ];

  const categories = ['All', 'Communication', 'CRM', 'Marketing', 'Finance', 'Productivity', 'Project Management', 'E-commerce'];

  const filteredIntegrations = integrations.filter(integration => {
    const matchesSearch = integration.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         integration.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || integration.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const connectedCount = integrations.filter(i => i.status === 'connected').length;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Integration Hub</h1>
        <p className="text-gray-600">Connect your AI agents to the tools and services you already use</p>
        <div className="mt-4 flex items-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-gray-600">{connectedCount} Connected</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
            <span className="text-gray-600">{integrations.length - connectedCount} Available</span>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="mb-8 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search integrations..."
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

      {/* Integration Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {filteredIntegrations.map((integration) => (
          <div key={integration.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{integration.icon}</div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{integration.name}</h3>
                  <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full">{integration.category}</span>
                </div>
              </div>
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
                integration.status === 'connected' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {integration.status === 'connected' ? (
                  <>
                    <CheckCircle className="h-3 w-3" />
                    <span>Connected</span>
                  </>
                ) : (
                  <span>Available</span>
                )}
              </div>
            </div>

            <p className="text-gray-600 text-sm mb-4">{integration.description}</p>

            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Key Features:</p>
              <ul className="space-y-1">
                {integration.features.map((feature, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-center">
                    <div className="w-1 h-1 bg-blue-500 rounded-full mr-2"></div>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="flex items-center space-x-2">
                {integration.popularity === 'high' && (
                  <span className="text-xs px-2 py-1 bg-orange-100 text-orange-800 rounded-full font-medium">Popular</span>
                )}
                <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
                  <ExternalLink className="h-4 w-4" />
                </button>
              </div>
              <div className="flex items-center space-x-2">
                {integration.status === 'connected' ? (
                  <button className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
                    <Settings className="h-4 w-4" />
                  </button>
                ) : (
                  <button className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
                    <Plus className="h-3 w-3 mr-1" />
                    Connect
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Security Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <Shield className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Enterprise-Grade Security</h3>
            <p className="text-blue-800 mb-4">
              All integrations use secure OAuth 2.0 authentication and encrypted data transmission. 
              Your sensitive information is protected with bank-level security standards.
            </p>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm text-blue-800">End-to-end encryption</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm text-blue-800">GDPR compliant</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm text-blue-800">SOC 2 certified</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Integration */}
      <div className="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Need a Custom Integration?</h3>
            <p className="text-gray-600">We can build custom integrations for your specific tools and workflows</p>
          </div>
          <Zap className="h-8 w-8 text-purple-600" />
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">API Integration</h4>
            <p className="text-sm text-gray-600 mb-3">Connect any REST or GraphQL API to your agent workflows</p>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">Learn more →</button>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Webhook Support</h4>
            <p className="text-sm text-gray-600 mb-3">Receive real-time data from your tools via webhooks</p>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">Contact us →</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Integrations;