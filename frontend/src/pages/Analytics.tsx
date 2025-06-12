import React, { useState } from 'react';
import { 
  TrendingUp, 
  DollarSign, 
  Clock, 
  Target, 
  BarChart3, 
  PieChart, 
  Activity,
  Calendar,
  Download,
  Filter,
  Eye,
  Brain,
  Zap,
  Users,
  AlertCircle,
  CheckCircle,
  ArrowUp,
  ArrowDown
} from 'lucide-react';

const Analytics: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('all');

  const kpiData = [
    {
      label: 'Total Cost Savings',
      value: '$12,450',
      change: '+28%',
      changeType: 'positive',
      icon: DollarSign,
      description: 'Compared to manual processes',
      trend: [45, 52, 48, 61, 55, 67, 73]
    },
    {
      label: 'Time Saved',
      value: '156 hours',
      change: '+34%',
      changeType: 'positive',
      icon: Clock,
      description: 'This month vs last month',
      trend: [32, 38, 42, 45, 48, 52, 56]
    },
    {
      label: 'Task Success Rate',
      value: '94.2%',
      change: '+2.1%',
      changeType: 'positive',
      icon: Target,
      description: 'Average across all agents',
      trend: [88, 89, 91, 92, 93, 94, 94.2]
    },
    {
      label: 'ROI Generated',
      value: '340%',
      change: '+15%',
      changeType: 'positive',
      icon: TrendingUp,
      description: 'Return on AgentFlow investment',
      trend: [280, 295, 310, 320, 325, 335, 340]
    }
  ];

  const agentPerformance = [
    { 
      name: 'Customer Support Lead', 
      tasksCompleted: 128, 
      successRate: 97, 
      costSavings: 3200, 
      timeSpent: '45h',
      efficiency: 95,
      humanInterventions: 3,
      avgResponseTime: '0.9s',
      tokenUsage: 45000
    },
    { 
      name: 'Sales Prospector', 
      tasksCompleted: 89, 
      successRate: 91, 
      costSavings: 2800, 
      timeSpent: '32h',
      efficiency: 88,
      humanInterventions: 7,
      avgResponseTime: '1.4s',
      tokenUsage: 38000
    },
    { 
      name: 'Operations Manager', 
      tasksCompleted: 67, 
      successRate: 94, 
      costSavings: 4100, 
      timeSpent: '38h',
      efficiency: 92,
      humanInterventions: 2,
      avgResponseTime: '1.5s',
      tokenUsage: 52000
    },
    { 
      name: 'Marketing Manager', 
      tasksCompleted: 45, 
      successRate: 89, 
      costSavings: 1900, 
      timeSpent: '28h',
      efficiency: 85,
      humanInterventions: 12,
      avgResponseTime: '1.9s',
      tokenUsage: 41000
    },
    { 
      name: 'Finance Agent', 
      tasksCompleted: 78, 
      successRate: 98, 
      costSavings: 3500, 
      timeSpent: '35h',
      efficiency: 96,
      humanInterventions: 1,
      avgResponseTime: '1.2s',
      tokenUsage: 29000
    }
  ];

  const taskCategories = [
    { category: 'Customer Support', completed: 145, percentage: 32, color: 'bg-blue-500', growth: '+12%' },
    { category: 'Sales & Marketing', completed: 98, percentage: 22, color: 'bg-green-500', growth: '+8%' },
    { category: 'Operations', completed: 87, percentage: 19, color: 'bg-purple-500', growth: '+15%' },
    { category: 'Finance & Accounting', completed: 76, percentage: 17, color: 'bg-orange-500', growth: '+22%' },
    { category: 'Human Resources', completed: 45, percentage: 10, color: 'bg-red-500', growth: '+5%' }
  ];

  const costBreakdown = [
    { category: 'Token Usage', amount: 245, percentage: 45, color: 'bg-blue-500' },
    { category: 'API Calls', amount: 156, percentage: 28, color: 'bg-green-500' },
    { category: 'Storage', amount: 89, percentage: 16, color: 'bg-purple-500' },
    { category: 'Compute', amount: 67, percentage: 11, color: 'bg-orange-500' }
  ];

  const periods = [
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' }
  ];

  const renderMiniChart = (data: number[]) => {
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min;
    
    return (
      <div className="flex items-end space-x-1 h-8">
        {data.map((value, index) => (
          <div
            key={index}
            className="bg-blue-500 rounded-sm w-1"
            style={{
              height: `${range === 0 ? 50 : ((value - min) / range) * 100}%`,
              minHeight: '2px'
            }}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Advanced Analytics & ROI Tracking</h1>
          <p className="text-gray-600">Deep insights into your AI agents' performance and business impact</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {periods.map((period) => (
              <option key={period.value} value={period.value}>
                {period.label}
              </option>
            ))}
          </select>
          <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* Enhanced KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {kpiData.map((kpi, index) => (
          <div key={index} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gray-50 rounded-lg">
                <kpi.icon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex items-center space-x-2">
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-medium ${
                  kpi.changeType === 'positive' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {kpi.changeType === 'positive' ? <ArrowUp className="h-3 w-3 mr-1" /> : <ArrowDown className="h-3 w-3 mr-1" />}
                  {kpi.change}
                </div>
              </div>
            </div>
            <div className="mb-4">
              <p className="text-2xl font-bold text-gray-900 mb-1">{kpi.value}</p>
              <p className="text-sm font-medium text-gray-600 mb-1">{kpi.label}</p>
              <p className="text-xs text-gray-500">{kpi.description}</p>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">7-day trend</span>
              {renderMiniChart(kpi.trend)}
            </div>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-8 mb-8">
        {/* Enhanced Performance Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Performance Trends</h2>
            <div className="flex items-center space-x-2">
              <select
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">All Metrics</option>
                <option value="tasks">Tasks Completed</option>
                <option value="success">Success Rate</option>
                <option value="cost">Cost Efficiency</option>
              </select>
              <BarChart3 className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          <div className="h-64 flex items-end justify-between space-x-2">
            {[45, 67, 89, 123, 98, 134, 156].map((value, index) => (
              <div key={index} className="flex flex-col items-center space-y-2 flex-1">
                <div 
                  className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t-md transition-all duration-500 hover:from-blue-600 hover:to-blue-500 relative group"
                  style={{ height: `${(value / 156) * 100}%` }}
                >
                  <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                    {value}
                  </div>
                </div>
                <span className="text-xs text-gray-600">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Enhanced Task Distribution */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Task Distribution</h2>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            {taskCategories.map((category, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-900">{category.category}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-600">{category.completed}</span>
                    <span className="text-green-600 text-xs font-medium">{category.growth}</span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${category.color} transition-all duration-500`}
                    style={{ width: `${category.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Enhanced Agent Performance Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-8">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Detailed Agent Performance</h2>
            <div className="flex items-center space-x-2">
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </button>
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors">
                <Eye className="h-4 w-4 mr-2" />
                View Details
              </button>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agent</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tasks</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Efficiency</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cost Savings</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Response Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Human Interventions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {agentPerformance.map((agent, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="p-2 bg-blue-100 rounded-lg mr-3">
                        <Brain className="h-4 w-4 text-blue-600" />
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-900">{agent.name}</span>
                        <div className="text-xs text-gray-500">{agent.tokenUsage.toLocaleString()} tokens</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{agent.tasksCompleted}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm text-gray-900 mr-2">{agent.successRate}%</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${agent.successRate}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm text-gray-900 mr-2">{agent.efficiency}%</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            agent.efficiency >= 90 ? 'bg-green-500' : 
                            agent.efficiency >= 80 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${agent.efficiency}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                    ${agent.costSavings.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{agent.avgResponseTime}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm text-gray-900 mr-2">{agent.humanInterventions}</span>
                      {agent.humanInterventions > 5 ? (
                        <AlertCircle className="h-4 w-4 text-yellow-500" />
                      ) : (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                      Active
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cost Analysis Dashboard */}
      <div className="grid lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Breakdown</h3>
          <div className="space-y-4">
            {costBreakdown.map((item, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-900">{item.category}</span>
                  <span className="text-gray-600">${item.amount}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${item.color} transition-all duration-500`}
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">ROI Analysis</h3>
              <p className="text-gray-600">Your investment vs. traditional processes</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
              <p className="text-xl font-bold text-red-600">$4,200</p>
              <p className="text-sm text-gray-600 mt-1">Manual Cost</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
              <p className="text-xl font-bold text-blue-600">$149</p>
              <p className="text-sm text-gray-600 mt-1">AgentFlow Cost</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
              <p className="text-xl font-bold text-green-600">$4,051</p>
              <p className="text-sm text-gray-600 mt-1">Net Savings</p>
            </div>
          </div>
        </div>
      </div>

      {/* Predictive Analytics */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Predictive Insights</h3>
            <p className="text-gray-600">AI-powered forecasting and recommendations</p>
          </div>
          <Brain className="h-8 w-8 text-purple-600" />
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <h4 className="font-medium text-gray-900">Projected Savings</h4>
            </div>
            <p className="text-2xl font-bold text-green-600">$18,500</p>
            <p className="text-sm text-gray-600">Next 30 days</p>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center space-x-2 mb-2">
              <Zap className="h-5 w-5 text-blue-600" />
              <h4 className="font-medium text-gray-900">Efficiency Gain</h4>
            </div>
            <p className="text-2xl font-bold text-blue-600">+12%</p>
            <p className="text-sm text-gray-600">Expected improvement</p>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center space-x-2 mb-2">
              <Users className="h-5 w-5 text-purple-600" />
              <h4 className="font-medium text-gray-900">Optimal Team Size</h4>
            </div>
            <p className="text-2xl font-bold text-purple-600">8 agents</p>
            <p className="text-sm text-gray-600">Recommended for your workload</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;