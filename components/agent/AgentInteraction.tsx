'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useAgentContext } from '@/contexts/AgentContext';
import { Loader2 } from 'lucide-react';

type AgentType = 'research' | 'sales' | 'support' | 'content';

interface AgentInteractionProps {
  defaultAgentType?: AgentType;
  defaultTask?: string;
  onResult?: (result: any) => void;
  className?: string;
}

export function AgentInteraction({
  defaultAgentType = 'research',
  defaultTask = '',
  onResult,
  className = '',
}: AgentInteractionProps) {
  const [agentType, setAgentType] = useState<AgentType>(defaultAgentType);
  const [task, setTask] = useState(defaultTask);
  const [context, setContext] = useState('');
  const [isWorkflow, setIsWorkflow] = useState(false);
  const [workflowId, setWorkflowId] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const { executeTask, executeWorkflow, isLoading } = useAgentContext();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    try {
      let result;
      
      if (isWorkflow && workflowId) {
        result = await executeWorkflow(
          workflowId,
          { task },
          { context: context || undefined },
          false
        );
      } else {
        result = await executeTask(
          agentType,
          task,
          context ? { context } : undefined
        );
      }
      
      setResult(result);
      onResult?.(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Agent interaction failed:', err);
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <Label htmlFor="agent-type">Agent Type</Label>
            <select
              id="agent-type"
              value={agentType}
              onChange={(e) => setAgentType(e.target.value as AgentType)}
              className="w-full p-2 border rounded"
              disabled={isWorkflow || isLoading}
            >
              <option value="research">Research</option>
              <option value="sales">Sales</option>
              <option value="support">Support</option>
              <option value="content">Content</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is-workflow"
              checked={isWorkflow}
              onChange={(e) => setIsWorkflow(e.target.checked)}
              className="h-4 w-4"
            />
            <Label htmlFor="is-workflow">Use Workflow</Label>
          </div>
          
          {isWorkflow && (
            <div className="flex-1">
              <Label htmlFor="workflow-id">Workflow ID</Label>
              <Input
                id="workflow-id"
                type="text"
                value={workflowId}
                onChange={(e) => setWorkflowId(e.target.value)}
                placeholder="Enter workflow ID"
                required
              />
            </div>
          )}
        </div>
        
        <div>
          <Label htmlFor="task">Task</Label>
          <Input
            id="task"
            type="text"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Enter your task..."
            required
          />
        </div>
        
        <div>
          <Label htmlFor="context">Context (Optional)</Label>
          <Textarea
            id="context"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Additional context for the agent..."
            rows={3}
          />
        </div>
        
        <Button type="submit" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            'Execute'
          )}
        </Button>
      </form>
      
      {error && (
        <div className="p-4 text-red-600 bg-red-50 rounded">
          <p className="font-medium">Error:</p>
          <p>{error}</p>
        </div>
      )}
      
      {result && (
        <div className="p-4 bg-gray-50 rounded">
          <h3 className="font-medium mb-2">Result:</h3>
          <pre className="text-sm bg-white p-2 rounded overflow-auto max-h-60">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
