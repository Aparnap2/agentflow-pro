import { useState, useEffect, useCallback } from 'react';
import { adminApi, AnalyticsData } from '../services/api';

export const useAnalytics = <T extends AnalyticsData = AnalyticsData>() => {
  const [analyticsData, setAnalyticsData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<string>('7d');

  // Fetch analytics data
  const fetchAnalyticsData = useCallback(async (period: string = selectedPeriod) => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getAnalyticsData(period);
      setAnalyticsData(data as unknown as T);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch analytics data');
      console.error('Error fetching analytics data:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedPeriod]);

  // Initialize data
  useEffect(() => {
    fetchAnalyticsData();
  }, [fetchAnalyticsData]);

  // Handle period change
  const handlePeriodChange = (period: string) => {
    setSelectedPeriod(period);
    fetchAnalyticsData(period);
  };

  // Export data
  const exportData = useCallback(async () => {
    if (!analyticsData) return false;
    
    try {
      // Create CSV content
      let csvContent = 'data:text/csv;charset=utf-8,';
      
      // Add KPIs
      csvContent += 'KPIs\n';
      csvContent += 'Label,Value,Change,Description\n';
      if ('kpis' in analyticsData) {
        analyticsData.kpis.forEach((kpi: any) => {
          csvContent += `"${kpi.label}","${kpi.value}","${kpi.change}","${kpi.description}"\n`;
        });
      }
      
      // Add agent performance
      if ('agentPerformance' in analyticsData) {
        csvContent += '\nAgent Performance\n';
        csvContent += 'Name,Tasks Completed,Success Rate,Cost Savings,Time Spent,Efficiency,Human Interventions,Avg Response Time,Token Usage\n';
        analyticsData.agentPerformance.forEach((agent: any) => {
          csvContent += `"${agent.name}",${agent.tasksCompleted},${agent.successRate}%,$${agent.costSavings},${agent.timeSpent},${agent.efficiency}%,${agent.humanInterventions},${agent.avgResponseTime},${agent.tokenUsage}\n`;
        });
      }
      
      // Create download link
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', `analytics_export_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      return true;
    } catch (err) {
      console.error('Error exporting data:', err);
      return false;
    }
  }, [analyticsData]);

  return {
    // State
    data: analyticsData,
    loading,
    error,
    selectedPeriod,
    
    // Actions
    setSelectedPeriod: handlePeriodChange,
    refresh: fetchAnalyticsData,
    exportData,
  };
};

export default useAnalytics;
