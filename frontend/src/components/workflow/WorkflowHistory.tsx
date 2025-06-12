import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  Search, 
  Filter, 
  Calendar, 
  Download, 
  ChevronDown, 
  ChevronRight,
  ExternalLink,
  Play
} from 'lucide-react';

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  name: string;
  status: 'completed' | 'failed' | 'running' | 'pending';
  startTime: string;
  endTime?: string;
  duration?: number;
  initiatedBy: string;
  successRate?: number;
}

interface WorkflowHistoryProps {
  executions?: WorkflowExecution[];
  onSelectExecution?: (executionId: string) => void;
  onRefresh?: () => void;
  selectedExecutionId?: string;
  className?: string;
}

const WorkflowHistory: React.FC<WorkflowHistoryProps> = ({
  executions: externalExecutions = [],
  onSelectExecution,
  onRefresh,
  selectedExecutionId,
  className = '',
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [expandedExecution, setExpandedExecution] = useState<string | null>(null);
  
  // Mock data for demonstration
  const [mockExecutions, setMockExecutions] = useState<WorkflowExecution[]>([
    {
      id: 'exec-001',
      workflowId: 'wf-001',
      name: 'Data Processing Pipeline',
      status: 'completed',
      startTime: new Date(Date.now() - 3600000 * 2).toISOString(),
      endTime: new Date(Date.now() - 3600000 * 2 + 120000).toISOString(),
      duration: 120,
      initiatedBy: 'user@example.com',
      successRate: 100,
    },
    {
      id: 'exec-002',
      workflowId: 'wf-002',
      name: 'Daily Report Generation',
      status: 'failed',
      startTime: new Date(Date.now() - 86400000).toISOString(),
      endTime: new Date(Date.now() - 86400000 + 45000).toISOString(),
      duration: 45,
      initiatedBy: 'system',
      successRate: 0,
    },
    {
      id: 'exec-003',
      workflowId: 'wf-001',
      name: 'Data Processing Pipeline',
      status: 'running',
      startTime: new Date().toISOString(),
      initiatedBy: 'user@example.com',
    },
  ]);

  // Use external executions if provided, otherwise use mock data
  const executions = externalExecutions.length > 0 ? externalExecutions : mockExecutions;

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      if (onRefresh) {
        await onRefresh();
      } else {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    } finally {
      setIsRefreshing(false);
    }
  };

  const filteredExecutions = executions.filter(execution => {
    const matchesSearch = execution.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       execution.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || execution.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const toggleExpandExecution = (executionId: string) => {
    if (expandedExecution === executionId) {
      setExpandedExecution(null);
    } else {
      setExpandedExecution(executionId);
      if (onSelectExecution) {
        onSelectExecution(executionId);
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'running':
        return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (seconds === undefined) return '--';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 overflow-hidden ${className}`}>
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h3 className="font-medium text-gray-900">Execution History</h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-1 text-gray-500 hover:text-gray-700 disabled:opacity-50"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
      
      <div className="p-3 border-b border-gray-200 bg-gray-50">
        <div className="flex flex-col space-y-2 sm:flex-row sm:space-y-0 sm:space-x-2">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search executions..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Filter className="h-4 w-4 text-gray-400" />
            </div>
            <select
              className="block w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="running">Running</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="divide-y divide-gray-200 overflow-y-auto" style={{ maxHeight: '600px' }}>
        {filteredExecutions.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            No executions found
          </div>
        ) : (
          filteredExecutions.map((execution) => (
            <div key={execution.id} className="bg-white">
              <div 
                className={`px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-gray-50 ${
                  selectedExecutionId === execution.id ? 'bg-blue-50' : ''
                }`}
                onClick={() => toggleExpandExecution(execution.id)}
              >
                <div className="flex items-center min-w-0">
                  <div className="flex-shrink-0">
                    {getStatusIcon(execution.status)}
                  </div>
                  <div className="ml-3 min-w-0 flex-1">
                    <div className="text-sm font-medium text-gray-900 truncate">
                      {execution.name}
                    </div>
                    <div className="flex flex-wrap mt-1 text-xs text-gray-500">
                      <span className="truncate">
                        {new Date(execution.startTime).toLocaleString()}
                      </span>
                      <span className="mx-1">•</span>
                      <span>ID: {execution.id}</span>
                    </div>
                  </div>
                </div>
                <div className="ml-2 flex-shrink-0 flex">
                  <div className="text-sm text-gray-500 mr-3">
                    {formatDuration(execution.duration)}
                  </div>
                  {expandedExecution === execution.id ? (
                    <ChevronDown className="h-5 w-5 text-gray-400" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-gray-400" />
                  )}
                </div>
              </div>
              
              {expandedExecution === execution.id && (
                <div className="px-4 pb-3 pt-1 border-t border-gray-100 bg-gray-50">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">Workflow ID</div>
                      <div className="mt-1 flex items-center">
                        <span className="truncate">{execution.workflowId}</span>
                        <button className="ml-2 text-blue-600 hover:text-blue-800">
                          <ExternalLink className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">Status</div>
                      <div className="mt-1 flex items-center">
                        {getStatusIcon(execution.status)}
                        <span className="ml-1 capitalize">{execution.status}</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">Started</div>
                      <div className="mt-1">
                        {new Date(execution.startTime).toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {execution.status === 'running' ? 'Duration' : 'Completed'}
                      </div>
                      <div className="mt-1">
                        {execution.status === 'running' ? (
                          <span className="flex items-center">
                            <span className="inline-block h-2 w-2 rounded-full bg-blue-500 mr-1.5"></span>
                            {formatDuration(execution.duration)}
                          </span>
                        ) : execution.endTime ? (
                          new Date(execution.endTime).toLocaleString()
                        ) : (
                          '--'
                        )}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">Initiated By</div>
                      <div className="mt-1">{execution.initiatedBy}</div>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</div>
                      <div className="mt-1">
                        {execution.successRate !== undefined ? (
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            execution.successRate === 100 
                              ? 'bg-green-100 text-green-800' 
                              : execution.successRate > 50 
                                ? 'bg-yellow-100 text-yellow-800' 
                                : 'bg-red-100 text-red-800'
                          }`}>
                            {execution.successRate}%
                          </span>
                        ) : (
                          '--'
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-3 flex justify-end space-x-2">
                    <button
                      type="button"
                      className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <Download className="-ml-0.5 mr-1.5 h-3.5 w-3.5" />
                      Export
                    </button>
                    {execution.status === 'completed' && (
                      <button
                        type="button"
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <Play className="-ml-0.5 mr-1.5 h-3.5 w-3.5" />
                        Rerun
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default WorkflowHistory;
