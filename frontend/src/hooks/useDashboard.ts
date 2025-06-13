import { useState, useEffect, useCallback, useMemo } from 'react';
import { adminApi, DashboardMetrics } from '../services/api';
import { toast } from 'react-hot-toast';

// Types for our dashboard state
interface DashboardState {
  metrics: DashboardMetrics | null;
  overview: any | null;
  activeAgents: any[];
  recentTasks: any[];
  systemHealth: {
    status: 'operational' | 'degraded' | 'maintenance' | 'error';
    message: string;
    updatedAt: string;
  };
  stats: Array<{
    label: string;
    value: string | number;
    icon: string;
    color: string;
    trend: string;
    clickable: boolean;
  }>;
  loading: boolean;
  error: string | null;
}

export const useDashboard = () => {
  // Main state
  const [state, setState] = useState<Omit<DashboardState, 'refresh' | 'handleAgentAction' | 'handleApproval' | 'submitTask'>>({
    metrics: null,
    overview: null,
    activeAgents: [],
    recentTasks: [],
    systemHealth: {
      status: 'operational',
      message: 'All systems operational',
      updatedAt: new Date().toISOString()
    },
    stats: [],
    loading: true,
    error: null
  });

  // Derived state
  const { metrics, overview, activeAgents, recentTasks, systemHealth, stats, loading, error } = state;

  // Fetch all dashboard data
  const fetchDashboardData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      // Fetch data in parallel for better performance
      const [
        metricsData, 
        overviewData, 
        agentsData, 
        tasksData,
        systemHealthData
      ] = await Promise.all([
        adminApi.getDashboardMetrics(),
        adminApi.getDashboardOverview(),
        adminApi.getAgents('active'),
        adminApi.getTasks('in_progress'),
        adminApi.getSystemMetrics()
      ]);

      // Transform metrics for the dashboard stats
      const dashboardStats = [
        { 
          label: 'Active Agents', 
          value: agentsData.count || 0,
          icon: 'Bot',
          color: 'text-blue-600',
          trend: overviewData?.agentTrend || '0',
          clickable: true 
        },
        { 
          label: 'Tasks Completed', 
          value: metricsData.tasksCompleted || 0,
          icon: 'CheckCircle',
          color: 'text-green-600',
          trend: overviewData?.taskTrend || '0',
          clickable: true 
        },
        { 
          label: 'Cost Savings', 
          value: `$${(metricsData.costSavings || 0).toLocaleString()}`,
          icon: 'TrendingUp',
          color: 'text-emerald-600',
          trend: overviewData?.costTrend || '0%',
          clickable: true 
        },
        { 
          label: 'Time Saved', 
          value: `${metricsData.timeSaved || 0}h`,
          icon: 'Clock',
          color: 'text-purple-600',
          trend: overviewData?.efficiencyTrend || '0%',
          clickable: true 
        }
      ];

      // Transform agents data
      const formattedAgents = agentsData.results.map((agent: any) => ({
        id: agent.id,
        name: agent.name,
        status: agent.status,
        task: agent.current_task || 'No active task',
        progress: agent.progress || 0,
        currentStep: agent.current_step || 'Initializing...',
        steps: agent.steps || [],
        tools: agent.tools || [],
        tokens: agent.tokens_used || 0,
        cost: `$${(agent.cost || 0).toFixed(2)}`,
        efficiency: agent.efficiency || 0,
        logs: agent.recent_logs || [],
        pendingApproval: agent.pending_approval,
        output: agent.output
      }));

      // Update state with all the fetched data
      setState(prev => ({
        ...prev,
        metrics: metricsData,
        overview: overviewData,
        activeAgents: formattedAgents,
        recentTasks: tasksData.results || [],
        systemHealth: {
          status: systemHealthData.status || 'operational',
          message: systemHealthData.message || 'All systems operational',
          updatedAt: systemHealthData.updated_at || new Date().toISOString()
        },
        stats: dashboardStats,
        loading: false
      }));

    } catch (err: any) {
      const errorMsg = err.message || 'Failed to fetch dashboard data';
      console.error('Error fetching dashboard data:', err);
      toast.error(errorMsg);
      setState(prev => ({
        ...prev,
        error: errorMsg,
        loading: false
      }));
    }
  }, []);

  // Initialize data on component mount
  useEffect(() => {
    fetchDashboardData();
    
    // Set up polling for real-time updates (every 30 seconds)
    const pollInterval = setInterval(fetchDashboardData, 30000);
    
    // Clean up interval on unmount
    return () => clearInterval(pollInterval);
  }, [fetchDashboardData]);

  // Handle agent actions (start, stop, pause, resume)
  const handleAgentAction = async (agentId: string, action: 'start' | 'stop' | 'pause' | 'resume') => {
    try {
      setState(prev => ({ ...prev, loading: true }));
      await adminApi.controlAgent(agentId, action);
      toast.success(`Agent ${action} command sent successfully`);
      
      // Refresh data after a short delay to allow backend to process
      setTimeout(fetchDashboardData, 1000);
    } catch (err: any) {
      const errorMsg = err.message || `Failed to ${action} agent`;
      console.error(`Error performing ${action} on agent ${agentId}:`, err);
      toast.error(errorMsg);
      throw err;
    }
  };

  // Handle task approval/rejection
  const handleApproval = async (approvalId: string, approved: boolean) => {
    try {
      setState(prev => ({ ...prev, loading: true }));
      await adminApi.processApproval(approvalId, approved ? 'approve' : 'reject');
      toast.success(`Task ${approved ? 'approved' : 'rejected'} successfully`);
      
      // Refresh data
      fetchDashboardData();
    } catch (err: any) {
      const errorMsg = err.message || `Failed to process approval`;
      console.error(`Error processing approval ${approvalId}:`, err);
      toast.error(errorMsg);
      throw err;
    }
  };

  // Submit a new task
  const submitTask = async (taskData: { description: string; priority?: number; metadata?: any }) => {
    try {
      setState(prev => ({ ...prev, loading: true }));
      const result = await adminApi.submitTask({
        ...taskData,
        priority: taskData.priority || 1, // Default priority
        metadata: {
          ...(taskData.metadata || {}),
          source: 'dashboard'
        }
      });
      
      toast.success('Task submitted successfully');
      fetchDashboardData(); // Refresh data
      return result;
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to submit task';
      console.error('Error submitting task:', err);
      toast.error(errorMsg);
      throw err;
    }
  };

  // Get system status color
  const getSystemStatusColor = useMemo(() => {
    switch (systemHealth.status) {
      case 'operational': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'maintenance': return 'text-blue-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  }, [systemHealth.status]);

  return {
    // State
    metrics,
    overview,
    activeAgents,
    recentTasks,
    systemHealth,
    stats,
    loading,
    error,
    
    // Computed
    systemStatusColor: getSystemStatusColor,
    
    // Actions
    refresh: fetchDashboardData,
    handleAgentAction,
    handleApproval,
    submitTask
  };
};

export default useDashboard;
