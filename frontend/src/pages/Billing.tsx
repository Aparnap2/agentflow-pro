import React, { useState } from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  Download, 
  Eye,
  CheckCircle,
  Target,
  ArrowUp,
  ArrowDown} from 'lucide-react';

const Billing: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [selectedPlan, setSelectedPlan] = useState('professional');
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [billingCycle, setBillingCycle] = useState('monthly');

  const currentSubscription = {
    plan: 'Professional',
    price: 149,
    cycle: 'monthly',
    nextBilling: '2024-04-15',
    status: 'active',
    agentsIncluded: 10,
    tasksIncluded: 500,
    agentsUsed: 7,
    tasksUsed: 342,
    overage: {
      agents: 0,
      tasks: 0,
      cost: 0
    }
  };

  const usageMetrics = {
    currentMonth: {
      totalCost: 149.00,
      basePlan: 149.00,
      overageCost: 0.00,
      tokensUsed: 125000,
      apiCalls: 8934,
      agentHours: 45.2,
      tasksCompleted: 342,
      successRate: 94.2,
      costPerTask: 0.44
    },
    previousMonth: {
      totalCost: 149.00,
      basePlan: 149.00,
      overageCost: 0.00,
      tokensUsed: 98000,
      apiCalls: 7234,
      agentHours: 38.7,
      tasksCompleted: 289,
      successRate: 91.8,
      costPerTask: 0.52
    }
  };

  const billingHistory = [
    {
      id: 1,
      date: '2024-03-15',
      amount: 149.00,
      status: 'paid',
      plan: 'Professional',
      period: 'March 2024',
      invoice: 'INV-2024-003',
      paymentMethod: '**** 4242'
    },
    {
      id: 2,
      date: '2024-02-15',
      amount: 149.00,
      status: 'paid',
      plan: 'Professional',
      period: 'February 2024',
      invoice: 'INV-2024-002',
      paymentMethod: '**** 4242'
    },
    {
      id: 3,
      date: '2024-01-15',
      amount: 49.00,
      status: 'paid',
      plan: 'Starter',
      period: 'January 2024',
      invoice: 'INV-2024-001',
      paymentMethod: '**** 4242'
    }
  ];

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      price: { monthly: 49, yearly: 490 },
      agents: 3,
      tasks: 100,
      features: [
        'Basic AI Agent Teams',
        'Standard Integrations',
        'Email Support',
        'Basic Analytics',
        'Community Access'
      ],
      popular: false
    },
    {
      id: 'professional',
      name: 'Professional',
      price: { monthly: 149, yearly: 1490 },
      agents: 10,
      tasks: 500,
      features: [
        'Advanced AI Agent Teams',
        'Premium Integrations',
        'Priority Support',
        'Advanced Analytics',
        'Custom Agent Training',
        'API Access',
        'White-label Options'
      ],
      popular: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: { monthly: 499, yearly: 4990 },
      agents: 'Unlimited',
      tasks: 'Unlimited',
      features: [
        'Unlimited AI Agents',
        'Custom Integrations',
        'Dedicated Support',
        'Advanced Security',
        'SLA Guarantees',
        'On-premise Deployment',
        'Custom Development'
      ],
      popular: false
    }
  ];

  const usageBreakdown = [
    { category: 'Agent Orchestration', cost: 89.40, percentage: 60, tokens: 75000, description: 'Core agent processing and coordination' },
    { category: 'External API Calls', cost: 35.76, percentage: 24, tokens: 0, description: 'Third-party integrations and data fetching' },
    { category: 'Data Storage', cost: 14.90, percentage: 10, tokens: 0, description: 'Vector database and persistent memory' },
    { category: 'Compute Resources', cost: 8.94, percentage: 6, tokens: 0, description: 'Processing power and infrastructure' }
  ];

  const costOptimizations = [
    {
      id: 1,
      title: 'Optimize Token Usage',
      description: 'Reduce token consumption by 15-20% through prompt optimization',
      potentialSavings: 18.50,
      effort: 'Low',
      impact: 'Medium',
      status: 'recommended'
    },
    {
      id: 2,
      title: 'Enable Semantic Caching',
      description: 'Cache similar queries to reduce redundant API calls',
      potentialSavings: 25.30,
      effort: 'Medium',
      impact: 'High',
      status: 'available'
    },
    {
      id: 3,
      title: 'Upgrade to Annual Billing',
      description: 'Save 17% by switching to annual billing cycle',
      potentialSavings: 300.00,
      effort: 'Low',
      impact: 'High',
      status: 'available'
    }
  ];

  const handlePlanChange = (planId: string) => {
    setSelectedPlan(planId);
    setShowUpgradeModal(true);
  };

  const handleBillingAction = (action: string, id?: number) => {
    console.log(`Billing action: ${action}`, id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'text-green-600 bg-green-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const calculateSavings = (current: number, previous: number) => {
    const change = ((current - previous) / previous) * 100;
    return {
      percentage: Math.abs(change).toFixed(1),
      isPositive: change < 0,
      direction: change < 0 ? 'down' : 'up'
    };
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Billing & Usage</h1>
          <p className="text-gray-600">Manage your subscription, track usage, and optimize costs</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
            <option value="year">Last Year</option>
          </select>
          <button 
            onClick={() => handleBillingAction('download_invoice')}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            Download Invoice
          </button>
        </div>
      </div>

      {/* Current Subscription */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Current Subscription</h2>
          <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(currentSubscription.status)}`}>
            {currentSubscription.status}
          </span>
        </div>
        
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{currentSubscription.plan}</div>
            <div className="text-sm text-gray-600">Current Plan</div>
            <div className="text-lg font-semibold text-gray-900 mt-1">${currentSubscription.price}/{currentSubscription.cycle}</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{currentSubscription.agentsUsed}/{currentSubscription.agentsIncluded}</div>
            <div className="text-sm text-gray-600">Agents Used</div>
            <div className="w-full bg-green-200 rounded-full h-2 mt-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentSubscription.agentsUsed / currentSubscription.agentsIncluded) * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{currentSubscription.tasksUsed}/{currentSubscription.tasksIncluded}</div>
            <div className="text-sm text-gray-600">Tasks This Month</div>
            <div className="w-full bg-purple-200 rounded-full h-2 mt-2">
              <div
                className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentSubscription.tasksUsed / currentSubscription.tasksIncluded) * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">{currentSubscription.nextBilling}</div>
            <div className="text-sm text-gray-600">Next Billing</div>
            <button 
              onClick={() => handleBillingAction('manage_payment')}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-1"
            >
              Manage Payment
            </button>
          </div>
        </div>
      </div>

      {/* Usage Metrics */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { 
            label: 'Total Cost', 
            current: usageMetrics.currentMonth.totalCost, 
            previous: usageMetrics.previousMonth.totalCost,
            format: 'currency',
            icon: DollarSign,
            color: 'blue'
          },
          { 
            label: 'Tasks Completed', 
            current: usageMetrics.currentMonth.tasksCompleted, 
            previous: usageMetrics.previousMonth.tasksCompleted,
            format: 'number',
            icon: CheckCircle,
            color: 'green'
          },
          { 
            label: 'Cost per Task', 
            current: usageMetrics.currentMonth.costPerTask, 
            previous: usageMetrics.previousMonth.costPerTask,
            format: 'currency',
            icon: Target,
            color: 'purple'
          },
          { 
            label: 'Success Rate', 
            current: usageMetrics.currentMonth.successRate, 
            previous: usageMetrics.previousMonth.successRate,
            format: 'percentage',
            icon: TrendingUp,
            color: 'emerald'
          }
        ].map((metric, index) => {
          const savings = calculateSavings(metric.current, metric.previous);
          return (
            <div key={index} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <metric.icon className={`h-6 w-6 text-${metric.color}-600`} />
                <div className="flex items-center space-x-1">
                  {savings.direction === 'down' ? <ArrowDown className="h-3 w-3 text-green-500" /> : <ArrowUp className="h-3 w-3 text-red-500" />}
                  <span className={`text-xs font-medium ${savings.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                    {savings.percentage}%
                  </span>
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {metric.format === 'currency' ? `$${metric.current.toFixed(2)}` :
                 metric.format === 'percentage' ? `${metric.current}%` :
                 metric.current.toLocaleString()}
              </p>
              <p className="text-sm text-gray-600">{metric.label}</p>
              <p className="text-xs text-gray-500 mt-1">
                vs last month: {metric.format === 'currency' ? `$${metric.previous.toFixed(2)}` :
                               metric.format === 'percentage' ? `${metric.previous}%` :
                               metric.previous.toLocaleString()}
              </p>
            </div>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-3 gap-8 mb-8">
        {/* Usage Breakdown */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Cost Breakdown</h2>
          <div className="space-y-4">
            {usageBreakdown.map((item, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-gray-900">{item.category}</span>
                    <p className="text-xs text-gray-600">{item.description}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-semibold text-gray-900">${item.cost.toFixed(2)}</span>
                    <p className="text-xs text-gray-600">{item.percentage}%</p>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
                {item.tokens > 0 && (
                  <p className="text-xs text-gray-500">{item.tokens.toLocaleString()} tokens used</p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Cost Optimizations */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Cost Optimizations</h2>
          <div className="space-y-4">
            {costOptimizations.map((optimization) => (
              <div key={optimization.id} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-900">{optimization.title}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    optimization.status === 'recommended' ? 'bg-blue-100 text-blue-800' :
                    optimization.status === 'available' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {optimization.status}
                  </span>
                </div>
                <p className="text-xs text-gray-600 mb-3">{optimization.description}</p>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-green-600">${optimization.potentialSavings.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">potential savings</p>
                  </div>
                  <button 
                    onClick={() => handleBillingAction('apply_optimization', optimization.id)}
                    className="px-3 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
                  >
                    Apply
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Plan Comparison */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Plan Comparison</h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Billing:</span>
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-3 py-1 text-sm font-medium rounded ${
                billingCycle === 'monthly' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-3 py-1 text-sm font-medium rounded ${
                billingCycle === 'yearly' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
              }`}
            >
              Yearly (Save 17%)
            </button>
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div key={plan.id} className={`relative p-6 border-2 rounded-xl transition-all ${
              plan.popular ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white'
            }`}>
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-600 text-white px-3 py-1 text-xs font-medium rounded-full">
                    Most Popular
                  </span>
                </div>
              )}
              
              <div className="text-center mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{plan.name}</h3>
                <div className="text-3xl font-bold text-gray-900">
                  ${plan.price[billingCycle as keyof typeof plan.price]}
                  <span className="text-lg text-gray-600">/{billingCycle === 'monthly' ? 'mo' : 'yr'}</span>
                </div>
                {billingCycle === 'yearly' && (
                  <p className="text-sm text-green-600 mt-1">Save ${(plan.price.monthly * 12) - plan.price.yearly}</p>
                )}
              </div>
              
              <div className="space-y-3 mb-6">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">AI Agents</span>
                  <span className="text-sm font-medium text-gray-900">{plan.agents}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Tasks/Month</span>
                  <span className="text-sm font-medium text-gray-900">{plan.tasks}</span>
                </div>
              </div>
              
              <ul className="space-y-2 mb-6">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    {feature}
                  </li>
                ))}
              </ul>
              
              <button
                onClick={() => handlePlanChange(plan.id)}
                className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                  currentSubscription.plan.toLowerCase() === plan.id
                    ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                    : plan.popular
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
                disabled={currentSubscription.plan.toLowerCase() === plan.id}
              >
                {currentSubscription.plan.toLowerCase() === plan.id ? 'Current Plan' : 'Upgrade'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Billing History */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Billing History</h2>
          <button 
            onClick={() => handleBillingAction('export_history')}
            className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Period</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {billingHistory.map((bill) => (
                <tr key={bill.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{bill.date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{bill.invoice}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{bill.plan}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{bill.period}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${bill.amount.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(bill.status)}`}>
                      {bill.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleBillingAction('view_invoice', bill.id)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleBillingAction('download_invoice', bill.id)}
                        className="text-gray-600 hover:text-gray-900"
                      >
                        <Download className="h-4 w-4" />
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
  );
};

export default Billing;