import React, { useState } from 'react';
import { 
  Users, 
  Settings, 
  BarChart3, 
  Database, 
  Activity, 
  AlertTriangle,
  CheckCircle,
  DollarSign,
  Bot,
  Eye,
  Edit,
  Trash2,
  Plus,
  Search,
  Download,
  RefreshCw,
  UserPlus,
  Lock,
  Unlock} from 'lucide-react';

const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedUser, setSelectedUser] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const systemOverview = {
    totalUsers: 1247,
    activeUsers: 892,
    totalAgents: 15420,
    activeAgents: 8934,
    totalOrchestrations: 3456,
    runningOrchestrations: 234,
    systemHealth: 98.5,
    uptime: '99.9%',
    totalRevenue: 145670,
    monthlyGrowth: 23.5,
    supportTickets: 45,
    criticalAlerts: 3
  };

  const users = [
    {
      id: 1,
      name: 'Sarah Chen',
      email: 'sarah@techstart.com',
      company: 'TechStart Inc.',
      plan: 'Professional',
      status: 'active',
      lastLogin: '2 hours ago',
      agentsDeployed: 12,
      monthlyUsage: '$149',
      joinDate: '2024-01-15',
      totalTasks: 1456,
      successRate: 94.2,
      role: 'admin'
    },
    {
      id: 2,
      name: 'Michael Rodriguez',
      email: 'mike@growthlab.io',
      company: 'GrowthLab',
      plan: 'Enterprise',
      status: 'active',
      lastLogin: '1 day ago',
      agentsDeployed: 25,
      monthlyUsage: '$499',
      joinDate: '2023-11-08',
      totalTasks: 3421,
      successRate: 96.8,
      role: 'user'
    },
    {
      id: 3,
      name: 'Emily Johnson',
      email: 'emily@startup.co',
      company: 'Startup Co.',
      plan: 'Starter',
      status: 'trial',
      lastLogin: '3 hours ago',
      agentsDeployed: 3,
      monthlyUsage: '$0',
      joinDate: '2024-03-01',
      totalTasks: 89,
      successRate: 87.5,
      role: 'user'
    },
    {
      id: 4,
      name: 'David Kim',
      email: 'david@innovate.com',
      company: 'Innovate Corp',
      plan: 'Professional',
      status: 'suspended',
      lastLogin: '1 week ago',
      agentsDeployed: 8,
      monthlyUsage: '$149',
      joinDate: '2023-09-22',
      totalTasks: 892,
      successRate: 91.3,
      role: 'user'
    }
  ];

  const agentTemplates = [
    {
      id: 1,
      name: 'CEO Agent',
      category: 'Executive',
      deployments: 234,
      successRate: 96.2,
      avgCost: '$0.45',
      status: 'active',
      version: '2.1.0',
      lastUpdated: '2 days ago'
    },
    {
      id: 2,
      name: 'Marketing Agent',
      category: 'Marketing',
      deployments: 567,
      successRate: 89.7,
      avgCost: '$0.33',
      status: 'active',
      version: '3.1.4',
      lastUpdated: '1 week ago'
    },
    {
      id: 3,
      name: 'Finance Agent',
      category: 'Finance',
      deployments: 345,
      successRate: 98.1,
      avgCost: '$0.22',
      status: 'active',
      version: '4.1.2',
      lastUpdated: '3 days ago'
    }
  ];

  const systemAlerts = [
    {
      id: 1,
      type: 'critical',
      message: 'High memory usage detected on orchestration server',
      timestamp: '5 minutes ago',
      status: 'active',
      details: 'Memory usage at 89% on server cluster-node-3'
    },
    {
      id: 2,
      type: 'warning',
      message: 'API rate limit approaching for OpenRouter',
      timestamp: '15 minutes ago',
      status: 'active',
      details: 'Current usage: 85% of monthly allocation'
    },
    {
      id: 3,
      type: 'info',
      message: 'Scheduled maintenance completed successfully',
      timestamp: '2 hours ago',
      status: 'resolved',
      details: 'Database optimization and index rebuilding completed'
    }
  ];

  const revenueData = [
    { month: 'Jan', revenue: 98500, users: 1050 },
    { month: 'Feb', revenue: 112300, users: 1156 },
    { month: 'Mar', revenue: 125600, users: 1247 },
    { month: 'Apr', revenue: 138900, users: 1342 },
    { month: 'May', revenue: 145670, users: 1398 }
  ];

  const systemResources = [
    { name: 'CPU Usage', current: 45, max: 100, unit: '%', status: 'normal' },
    { name: 'Memory', current: 6.8, max: 16, unit: 'GB', status: 'normal' },
    { name: 'Storage', current: 2.1, max: 10, unit: 'TB', status: 'normal' },
    { name: 'Network I/O', current: 125, max: 1000, unit: 'MB/s', status: 'normal' },
    { name: 'Database Connections', current: 234, max: 1000, unit: '', status: 'normal' },
    { name: 'Active Sessions', current: 892, max: 5000, unit: '', status: 'normal' }
  ];

  const tabs = [
    { id: 'overview', name: 'System Overview', icon: BarChart3 },
    { id: 'users', name: 'User Management', icon: Users },
    { id: 'agents', name: 'Agent Templates', icon: Bot },
    { id: 'billing', name: 'Billing & Revenue', icon: DollarSign },
    { id: 'system', name: 'System Health', icon: Activity },
    { id: 'settings', name: 'Platform Settings', icon: Settings }
  ];

  const handleUserAction = (userId: number, action: string) => {
    console.log(`${action} user ${userId}`);
  };

  const handleAgentAction = (agentId: number, action: string) => {
    console.log(`${action} agent template ${agentId}`);
  };

  const handleSystemAction = (action: string) => {
    console.log(`System action: ${action}`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'trial': return 'text-blue-600 bg-blue-100';
      case 'suspended': return 'text-red-600 bg-red-100';
      case 'inactive': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'critical': return 'text-red-600 bg-red-100 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'info': return 'text-blue-600 bg-blue-100 border-blue-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.company.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || user.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Panel</h1>
          <p className="text-gray-600">Platform administration and system management</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => handleSystemAction('backup')}
            className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            Backup
          </button>
          <button 
            onClick={() => handleSystemAction('maintenance')}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Settings className="h-4 w-4 mr-2" />
            Maintenance
          </button>
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
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* System Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Users</p>
                  <p className="text-2xl font-bold text-gray-900">{systemOverview.totalUsers.toLocaleString()}</p>
                  <p className="text-xs text-green-600 mt-1">+{systemOverview.monthlyGrowth}% this month</p>
                </div>
                <Users className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Agents</p>
                  <p className="text-2xl font-bold text-gray-900">{systemOverview.activeAgents.toLocaleString()}</p>
                  <p className="text-xs text-blue-600 mt-1">{systemOverview.totalAgents.toLocaleString()} total</p>
                </div>
                <Bot className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
                  <p className="text-2xl font-bold text-gray-900">${systemOverview.totalRevenue.toLocaleString()}</p>
                  <p className="text-xs text-green-600 mt-1">+{systemOverview.monthlyGrowth}% growth</p>
                </div>
                <DollarSign className="h-8 w-8 text-emerald-600" />
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">System Health</p>
                  <p className="text-2xl font-bold text-gray-900">{systemOverview.systemHealth}%</p>
                  <p className="text-xs text-green-600 mt-1">{systemOverview.uptime} uptime</p>
                </div>
                <Activity className="h-8 w-8 text-purple-600" />
              </div>
            </div>
          </div>

          {/* System Alerts */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">System Alerts</h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">{systemAlerts.filter(a => a.status === 'active').length} active</span>
                <button 
                  onClick={() => handleSystemAction('clear_alerts')}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Clear All
                </button>
              </div>
            </div>
            <div className="space-y-3">
              {systemAlerts.map((alert) => (
                <div key={alert.id} className={`p-4 rounded-lg border ${getAlertColor(alert.type)}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      {alert.type === 'critical' && <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />}
                      {alert.type === 'warning' && <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />}
                      {alert.type === 'info' && <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />}
                      <div>
                        <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                        <p className="text-xs text-gray-600 mt-1">{alert.details}</p>
                        <p className="text-xs text-gray-500 mt-2">{alert.timestamp}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      alert.status === 'active' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {alert.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Revenue Chart */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Revenue Trends</h2>
            <div className="h-64 flex items-end justify-between space-x-2">
              {revenueData.map((data, index) => (
                <div key={index} className="flex flex-col items-center space-y-2 flex-1">
                  <div 
                    className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t-md transition-all duration-500 hover:from-blue-600 hover:to-blue-500 relative group"
                    style={{ height: `${(data.revenue / Math.max(...revenueData.map(d => d.revenue))) * 100}%` }}
                  >
                    <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                      ${data.revenue.toLocaleString()}
                    </div>
                  </div>
                  <span className="text-xs text-gray-600">{data.month}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="space-y-6">
          {/* User Management Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="trial">Trial</option>
                <option value="suspended">Suspended</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
            <button 
              onClick={() => console.log('Add new user')}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              Add User
            </button>
          </div>

          {/* Users Table */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usage</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Login</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-600 font-medium text-sm">
                              {user.name.split(' ').map(n => n[0]).join('')}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{user.name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                            <div className="text-xs text-gray-400">{user.company}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                          {user.plan}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(user.status)}`}>
                          {user.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>{user.agentsDeployed} agents</div>
                        <div className="text-xs text-gray-500">{user.monthlyUsage}/month</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>{user.totalTasks.toLocaleString()} tasks</div>
                        <div className="text-xs text-green-600">{user.successRate}% success</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.lastLogin}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleUserAction(user.id, 'view')}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleUserAction(user.id, 'edit')}
                            className="text-gray-600 hover:text-gray-900"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleUserAction(user.id, user.status === 'active' ? 'suspend' : 'activate')}
                            className={user.status === 'active' ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}
                          >
                            {user.status === 'active' ? <Lock className="h-4 w-4" /> : <Unlock className="h-4 w-4" />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'agents' && (
        <div className="space-y-6">
          {/* Agent Templates Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Agent Template Management</h2>
            <button 
              onClick={() => console.log('Create new agent template')}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Template
            </button>
          </div>

          {/* Agent Templates Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agentTemplates.map((agent) => (
              <div key={agent.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                    <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">{agent.category}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleAgentAction(agent.id, 'edit')}
                      className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleAgentAction(agent.id, 'delete')}
                      className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Deployments:</span>
                    <span className="font-medium text-gray-900">{agent.deployments}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Success Rate:</span>
                    <span className="font-medium text-green-600">{agent.successRate}%</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Avg Cost:</span>
                    <span className="font-medium text-purple-600">{agent.avgCost}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Version:</span>
                    <span className="font-medium text-gray-900">{agent.version}</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(agent.status)}`}>
                      {agent.status}
                    </span>
                    <span className="text-xs text-gray-500">Updated {agent.lastUpdated}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="space-y-6">
          {/* System Resources */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">System Resources</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {systemResources.map((resource, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">{resource.name}</span>
                    <span className="text-sm text-gray-600">
                      {resource.current.toLocaleString()}{resource.unit} / {resource.max.toLocaleString()}{resource.unit}
                    </span>
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

          {/* System Actions */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">System Actions</h2>
            <div className="grid md:grid-cols-3 gap-4">
              <button 
                onClick={() => handleSystemAction('restart_services')}
                className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <RefreshCw className="h-5 w-5 text-blue-600" />
                <span className="font-medium text-gray-900">Restart Services</span>
              </button>
              <button 
                onClick={() => handleSystemAction('clear_cache')}
                className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Database className="h-5 w-5 text-green-600" />
                <span className="font-medium text-gray-900">Clear Cache</span>
              </button>
              <button 
                onClick={() => handleSystemAction('export_logs')}
                className="flex items-center justify-center space-x-2 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Download className="h-5 w-5 text-purple-600" />
                <span className="font-medium text-gray-900">Export Logs</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;