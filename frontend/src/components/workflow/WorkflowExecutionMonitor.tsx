import React, { useEffect, useState } from 'react';
import { Play, Pause, StopCircle, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

interface ExecutionStep {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: string;
  endTime?: string;
  duration?: number;
  error?: string;
}

interface WorkflowExecutionMonitorProps {
  executionId?: string;
  onRefresh?: () => void;
}

const WorkflowExecutionMonitor: React.FC<WorkflowExecutionMonitorProps> = ({ 
  executionId, 
  onRefresh 
}) => {
  const [execution, setExecution] = useState<{
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    startTime: string;
    endTime?: string;
    duration?: number;
    steps: ExecutionStep[];
  } | null>(null);

  const [isRefreshing, setIsRefreshing] = useState(false);

  // Simulate fetching execution data
  useEffect(() => {
    if (!executionId) return;
    
    const fetchExecution = async () => {
      setIsRefreshing(true);
      try {
        // TODO: Replace with actual API call
        // const response = await fetch(`/api/executions/${executionId}`);
        // const data = await response.json();
        // setExecution(data);
        
        // Mock data for now
        setTimeout(() => {
          setExecution({
            id: executionId,
            status: 'running',
            startTime: new Date().toISOString(),
            steps: [
              {
                id: 'step-1',
                name: 'Data Extraction',
                status: 'completed',
                startTime: new Date(Date.now() - 60000).toISOString(),
                endTime: new Date(Date.now() - 30000).toISOString(),
                duration: 30,
              },
              {
                id: 'step-2',
                name: 'Data Processing',
                status: 'running',
                startTime: new Date(Date.now() - 29000).toISOString(),
              },
              {
                id: 'step-3',
                name: 'Analysis',
                status: 'pending',
              },
            ],
          });
          setIsRefreshing(false);
        }, 500);
      } catch (error) {
        console.error('Failed to fetch execution:', error);
        setIsRefreshing(false);
      }
    };

    fetchExecution();
    const interval = setInterval(fetchExecution, 5000); // Poll every 5 seconds
    
    return () => clearInterval(interval);
  }, [executionId]);

  if (!execution) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
        <div className="text-gray-500">No execution selected</div>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'running':
        return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Execution #{execution.id.slice(0, 8)}</h3>
          <div className="flex items-center space-x-2 mt-1">
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getStatusColor(execution.status)}`}>
              {execution.status.toUpperCase()}
            </span>
            <span className="text-xs text-gray-500">
              Started at {new Date(execution.startTime).toLocaleString()}
            </span>
          </div>
        </div>
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-1 text-gray-500 hover:text-gray-700 disabled:opacity-50"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>
      
      <div className="p-4">
        <div className="space-y-4">
          {execution.steps.map((step) => (
            <div key={step.id} className="border rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(step.status)}
                  <span className="font-medium">{step.name}</span>
                </div>
                <div className="text-xs text-gray-500">
                  {step.startTime && (
                    <span>
                      {new Date(step.startTime).toLocaleTimeString()}
                      {step.endTime && ` - ${new Date(step.endTime).toLocaleTimeString()}`}
                    </span>
                  )}
                  {step.duration && (
                    <span className="ml-2">
                      ({step.duration}s)
                    </span>
                  )}
                </div>
              </div>
              {step.error && (
                <div className="p-3 bg-red-50 text-red-700 text-sm">
                  {step.error}
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="mt-6 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Execution Logs</h4>
          <div className="bg-gray-50 rounded p-3 font-mono text-sm h-32 overflow-y-auto">
            {execution.steps.map((step) => (
              <div key={`log-${step.id}`} className="text-gray-600">
                [{new Date(step.startTime || new Date()).toISOString()}] {step.name}: {step.status}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowExecutionMonitor;
