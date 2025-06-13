import React, { useState } from 'react';
import { 
  TrendingUp, 
  DollarSign, 
  Clock, 
  Users, 
  Filter, 
  Download, 
  ChevronDown, 
  ChevronUp, 
  Brain, 
  CheckCircle, 
  AlertTriangle,
  Activity,
  PieChart,
  BarChart3,
  Zap,
  ArrowUp,
  ArrowDown,
  Calendar
} from 'lucide-react';
import { AnalyticsData as AnalyticsDataType } from '../services/api';
import { useAnalytics } from '../hooks/useAnalytics';
import { toast } from 'react-hot-toast'; 

// Define types for our data
type ChangeType = 'positive' | 'negative' | 'neutral';

type AgentStatus = 'online' | 'offline' | 'busy';

interface KpiData {
  label: string;
  value: string | number;
  change: string;
  changeType: ChangeType;
  description: string;
  trend: number[];
}

interface AgentPerformance {
  id: string;
  name: string;
  tasksCompleted: number;
  successRate: number;
  costSavings: number;
  timeSpent: string;
  efficiency: number;
  humanInterventions: number;
  avgResponseTime: string;
  tokenUsage: number;
  avatar?: string;
  status: AgentStatus;
  role?: string;
}

interface TaskCategory {
  id: string;
  category: string;
  completed: number;
  percentage: number;
  growth: string;
  color: string;
  trend: number[];
}

interface CostBreakdown {
  id: string;
  category: string;
  amount: number;
  percentage: number;
  color: string;
  trend: number[];
}

type AnalyticsData = AnalyticsDataType;

const Analytics: React.FC = () => {
  // State for UI controls
  const [selectedMetric, setSelectedMetric] = useState('all');
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  
  // Use the analytics hook
  const {
    data: analyticsData,
    loading,
    error,
    selectedPeriod,
    setSelectedPeriod,
    exportData
  } = useAnalytics<AnalyticsData>();
  
  // Handle export
  const handleExport = async () => {
    try {
      await exportData();
      toast.success('Data exported successfully');
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Failed to export data');
    }
  };
  
  // Toggle agent details
  const toggleAgentDetails = (agentId: string) => {
    setExpandedAgent(expandedAgent === agentId ? null : agentId);
  };
  
  // Format utility functions will be defined after the component's main logic
  
  // Loading state
  if (loading && !analyticsData) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-red-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">
                {error}. <button onClick={() => setSelectedPeriod(selectedPeriod)} className="text-blue-600 hover:text-blue-800 font-medium">Try again</button>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // If no data is available yet, show loading
  if (!analyticsData) return null;
  
  // Destructure data for easier access
  const { kpis, agentPerformance, taskCategories, costBreakdown } = analyticsData;
  
  // Period options for filtering
  const periodOptions = [
    { value: '24h', label: 'Last 24 hours' },
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' },
    { value: 'all', label: 'All Time' }
  ] as const;
  
  // Type for period values - used in handlePeriodChange
  type Period = typeof periodOptions[number]['value'];
  
  // Handle period change with type safety
  const handlePeriodChange = (period: Period) => {
    setSelectedPeriod(period);
  };

  // Get status color for agent
  const getStatusColor = (status: AgentStatus): string => {
    switch (status) {
      case 'online':
        return 'bg-green-500';
      case 'busy':
        return 'bg-yellow-500';
      case 'offline':
        return 'bg-gray-400';
      default:
        return 'bg-gray-400';
    }
  };

  // Format currency
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount);
  };

  // Format percentage
  const formatPercentage = (value: number): string => {
    return `${Math.round(value * 10) / 10}%`;
  };

  // Format time
  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
        <div className="flex space-x-4">
          <div className="relative">
            <select
              value={selectedPeriod}
              onChange={(e) => handlePeriodChange(e.target.value as Period)}
              className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              disabled={loading}
            >
              {periodOptions.map((period) => (
                <option key={period.value} value={period.value}>
                  {period.label}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={handleExport}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={loading}
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {kpis?.map((kpi, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">{kpi.label}</p>
                <p className="mt-1 text-2xl font-semibold text-gray-900">
                  {kpi.value}
                </p>
              </div>
              <div className="p-2 rounded-full bg-blue-100">
                {getIcon(kpi.label)}
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                kpi.changeType === 'positive' 
                  ? 'bg-green-100 text-green-800' 
                  : kpi.changeType === 'negative' 
                    ? 'bg-red-100 text-red-800' 
                    : 'bg-gray-100 text-gray-800'
              }`}>
                {kpi.change}
                {kpi.changeType === 'positive' ? (
                  <ArrowUp className="ml-0.5 h-3 w-3" />
                ) : kpi.changeType === 'negative' ? (
                  <ArrowDown className="ml-0.5 h-3 w-3" />
                ) : null}
              </span>
              <span className="ml-2 text-sm text-gray-500">
                vs previous period
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Agent Performance */}
      <div className="bg-white shadow rounded-lg mb-8">
        <div className="px-6 py-5 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-medium text-gray-900">Agent Performance</h2>
            <div className="flex items-center">
              <Filter className="h-4 w-4 text-gray-400 mr-2" />
              <select
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value)}
                className="text-sm border-0 focus:ring-0 focus:ring-offset-0 p-0"
              >
                <option value="all">All Metrics</option>
                <option value="efficiency">Efficiency</option>
                <option value="success">Success Rate</option>
                <option value="cost">Cost Savings</option>
              </select>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Agent
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tasks Completed
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Success Rate
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cost Savings
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Efficiency
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="relative px-6 py-3">
                  <span className="sr-only">View</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {agentPerformance?.map((agent) => (
                <React.Fragment key={agent.id}>
                  <tr className="hover:bg-gray-50 cursor-pointer" onClick={() => toggleAgentDetails(agent.id)}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          {agent.avatar ? (
                            <img className="h-10 w-10 rounded-full" src={agent.avatar} alt={agent.name} />
                          ) : (
                            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <span className="text-blue-600 font-medium">
                                {agent.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                              </span>
                            </div>
                          )}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{agent.name}</div>
                          {agent.role && (
                            <div className="text-sm text-gray-500">{agent.role}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{agent.tasksCompleted}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatPercentage(agent.successRate)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(agent.costSavings)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatPercentage(agent.efficiency)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        {agent.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {expandedAgent === agent.id ? (
                        <ChevronUp className="h-5 w-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-gray-400" />
                      )}
                    </td>
                  </tr>
                  {expandedAgent === agent.id && (
                    <tr className="bg-gray-50">
                      <td colSpan={7} className="px-6 py-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                          <div className="bg-white p-4 rounded-lg shadow">
                            <h3 className="text-sm font-medium text-gray-500">Human Interventions</h3>
                            <p className="mt-1 text-2xl font-semibold text-gray-900">
                              {agent.humanInterventions}
                            </p>
                          </div>
                          <div className="bg-white p-4 rounded-lg shadow">
                            <h3 className="text-sm font-medium text-gray-500">Avg. Response Time</h3>
                            <p className="mt-1 text-2xl font-semibold text-gray-900">
                              {agent.avgResponseTime}
                            </p>
                          </div>
                          <div className="bg-white p-4 rounded-lg shadow">
                            <h3 className="text-sm font-medium text-gray-500">Token Usage</h3>
                            <p className="mt-1 text-2xl font-semibold text-gray-900">
                              {agent.tokenUsage.toLocaleString()}
                            </p>
                          </div>
                          <div className="bg-white p-4 rounded-lg shadow">
                            <h3 className="text-sm font-medium text-gray-500">Time Spent</h3>
                            <p className="mt-1 text-2xl font-semibold text-gray-900">
                              {agent.timeSpent}
                            </p>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Task Categories and Cost Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Task Categories */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Task Categories</h2>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            {taskCategories?.map((category) => (
              <div key={category.id} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-gray-900">{category.category}</span>
                  <span className="text-gray-500">{category.completed} tasks</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${category.color}`}
                    style={{ width: `${category.percentage}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{category.percentage}% of total</span>
                  <span className={`${category.growth.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                    {category.growth} from last period
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cost Breakdown */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Cost Breakdown</h2>
            <BarChart3 className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            {costBreakdown?.map((item) => (
              <div key={item.id} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-gray-900">{item.category}</span>
                  <span className="text-gray-900">{formatCurrency(item.amount)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${item.color}`}
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500">
                  {item.percentage}% of total costs
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to get icon based on KPI label
function getIcon(label: string) {
  switch (label.toLowerCase()) {
    case 'total tasks':
      return <Activity className="h-5 w-5 text-blue-600" />;
    case 'cost savings':
      return <DollarSign className="h-5 w-5 text-green-600" />;
    case 'avg. response time':
      return <Clock className="h-5 w-5 text-yellow-600" />;
    case 'success rate':
      return <CheckCircle className="h-5 w-5 text-purple-600" />;
    default:
      return <TrendingUp className="h-5 w-5 text-gray-600" />;
  }
}

export default Analytics;
