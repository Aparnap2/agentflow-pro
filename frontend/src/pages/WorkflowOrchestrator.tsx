import React, { useState, useCallback } from 'react';
import { 
  GitBranch,
  MessageSquare,
  List} from 'lucide-react';
import { useCrews } from '../hooks/useApi';
import { 
  WorkflowBuilder, 
  WorkflowExecutionMonitor, 
  WorkflowHistory, 
  ChatInterface,
  type WorkflowExecution,
  type Message
} from '../components/workflow';

// Mock data for workflow history
const MOCK_EXECUTIONS: WorkflowExecution[] = [
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
];

const WorkflowOrchestrator: React.FC = () => {
  // Workflow Builder State
  const [activeTab, setActiveTab] = useState<'builder' | 'history' | 'chat'>('builder');
  const [selectedExecutionId, setSelectedExecutionId] = useState<string | undefined>();
  const [workflowExecutions, setWorkflowExecutions] = useState<WorkflowExecution[]>(MOCK_EXECUTIONS);
  const [chatMessages, setChatMessages] = useState<Message[]>([]);
  const [isChatProcessing, setIsChatProcessing] = useState(false);
  
  // Get crews for agent assignment
  const { crews } = useCrews();
  
  // Log when crews are loaded
  React.useEffect(() => {
    if (crews && crews.length > 0) {
      console.log('Crews loaded:', crews);
    }
  }, [crews]);
  
  // Handle workflow save
  const handleWorkflowSave = (workflow: any) => {
    console.log('Saving workflow:', workflow);
    // TODO: Implement actual save to backend
    console.log('Saving workflow with crews:', crews);
    
    // For now, just update the UI with mock data
    setWorkflowExecutions(prev => [
      {
        id: `exec-${Date.now()}`,
        workflowId: `wf-${Math.floor(1000 + Math.random() * 9000)}`,
        name: workflow.name,
        status: 'pending',
        startTime: new Date().toISOString(),
        initiatedBy: 'current-user@example.com',
      },
      ...prev
    ]);
    
    // Show a success message
    setChatMessages(prev => [
      ...prev,
      {
        id: `msg-${Date.now()}`,
        content: `Workflow "${workflow.name}" saved successfully!`,
        sender: 'assistant',
        timestamp: new Date(),
        status: 'sent',
      }
    ]);
  };
  
  // Handle chat message send
  const handleSendMessage = async (message: string) => {
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      content: message,
      sender: 'user',
      timestamp: new Date(),
      status: 'sent',
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setIsChatProcessing(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Add assistant response
      setChatMessages(prev => [
        ...prev,
        {
          id: `msg-${Date.now()}`,
          content: `I received your message: "${message}"`,
          sender: 'assistant',
          timestamp: new Date(),
          status: 'sent',
        }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsChatProcessing(false);
    }
  };
  
  // Handle execution selection
  const handleSelectExecution = (executionId: string) => {
    setSelectedExecutionId(executionId);
    setActiveTab('history');
  };
  
  // Refresh executions
  const handleRefreshExecutions = useCallback(async () => {
    // In a real app, this would fetch from the API
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        resolve();
      }, 1000);
    });
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Workflow Orchestrator</h1>
            <p className="mt-1 text-sm text-gray-500">
              Design, execute, and monitor agent workflows
            </p>
          </div>
          <div className="mt-4 md:mt-0 flex space-x-2">
            <button
              onClick={() => setActiveTab('builder')}
              className={`px-4 py-2 rounded-md flex items-center ${
                activeTab === 'builder'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <GitBranch className="w-4 h-4 mr-2" />
              Workflow Builder
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-4 py-2 rounded-md flex items-center ${
                activeTab === 'history'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <List className="w-4 h-4 mr-2" />
              Execution History
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 rounded-md flex items-center ${
                activeTab === 'chat'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Chat
            </button>
          </div>
        </div>
        
        {/* Main content area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left sidebar - Workflow builder or history */}
          <div className={`lg:col-span-2 space-y-6 ${
            activeTab === 'builder' || activeTab === 'history' ? 'block' : 'hidden lg:block'
          }`}>
            {activeTab === 'builder' ? (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="p-4 border-b border-gray-200">
                  <h2 className="text-lg font-medium text-gray-900">Workflow Builder</h2>
                  <p className="mt-1 text-sm text-gray-500">
                    Drag and drop components to design your workflow
                  </p>
                </div>
                <div className="h-[600px]">
                  <WorkflowBuilder onSave={handleWorkflowSave} />
                </div>
              </div>
            ) : activeTab === 'history' ? (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="p-4 border-b border-gray-200">
                  <h2 className="text-lg font-medium text-gray-900">Execution History</h2>
                  <p className="mt-1 text-sm text-gray-500">
                    View and manage your workflow executions
                  </p>
                </div>
                <div className="h-[600px] overflow-y-auto">
                  <WorkflowHistory 
                    executions={workflowExecutions}
                    onSelectExecution={handleSelectExecution}
                    selectedExecutionId={selectedExecutionId}
                    onRefresh={handleRefreshExecutions}
                  />
                </div>
              </div>
            ) : null}
            
            {/* Execution Monitor - Always visible when an execution is selected */}
            {selectedExecutionId && (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="p-4 border-b border-gray-200">
                  <h2 className="text-lg font-medium text-gray-900">Execution Monitor</h2>
                  <p className="mt-1 text-sm text-gray-500">
                    Monitor the status of your workflow execution
                  </p>
                </div>
                <div className="h-[400px]">
                  <WorkflowExecutionMonitor 
                    executionId={selectedExecutionId}
                    onRefresh={handleRefreshExecutions}
                  />
                </div>
              </div>
            )}
          </div>
          
          {/* Right sidebar - Chat interface */}
          <div className={`${activeTab === 'chat' ? 'block' : 'hidden lg:block'}`}>
            <div className="bg-white rounded-lg shadow overflow-hidden h-full">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Workflow Assistant</h2>
                <p className="mt-1 text-sm text-gray-500">
                  Get help with your workflows
                </p>
              </div>
              <div className="h-[calc(100%-72px)]">
                <ChatInterface
                  messages={chatMessages}
                  onSendMessage={handleSendMessage}
                  isProcessing={isChatProcessing}
                  workflowId={selectedExecutionId}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowOrchestrator;
