import React, { useState, useCallback } from 'react';
import { Node, Edge, ReactFlow, addEdge, Background, Controls, useNodesState, useEdgesState } from 'reactflow';
import 'reactflow/dist/style.css';

interface WorkflowBuilderProps {
  onSave: (workflow: any) => void;
  initialNodes?: Node[];
  initialEdges?: Edge[];
}

const nodeTypes = {
  task: ({ data }: { data: any }) => (
    <div className="p-3 bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="font-medium text-sm">{data.label}</div>
      <div className="text-xs text-gray-500">{data.type}</div>
    </div>
  ),
};

const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  onSave,
  initialNodes = [],
  initialEdges = [],
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [workflowName, setWorkflowName] = useState('New Workflow');
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const addNode = (type: string) => {
    const newNode = {
      id: `node-${nodes.length + 1}`,
      type: 'task',
      position: { x: 100, y: 100 + nodes.length * 100 },
      data: { label: `Task ${nodes.length + 1}`, type },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const onNodeClick = (event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  };

  const onPaneClick = () => {
    setSelectedNode(null);
  };

  const handleSave = () => {
    onSave({
      name: workflowName,
      nodes,
      edges,
      createdAt: new Date().toISOString(),
    });
  };

  return (
    <div className="flex flex-col h-full">
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex justify-between items-center">
          <input
            type="text"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            className="text-xl font-semibold border-none focus:ring-0 focus:outline-none"
          />
          <div className="flex space-x-2">
            <button
              onClick={() => addNode('llm')}
              className="px-3 py-1 bg-blue-500 text-white rounded-md text-sm"
            >
              Add Task
            </button>
            <button
              onClick={handleSave}
              className="px-3 py-1 bg-green-600 text-white rounded-md text-sm"
            >
              Save Workflow
            </button>
          </div>
        </div>
      </div>
      
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
        
        {selectedNode && (
          <div className="absolute top-4 right-4 w-64 bg-white p-4 rounded-lg shadow-lg border border-gray-200">
            <h3 className="font-medium mb-2">Node Properties</h3>
            <div className="space-y-2">
              <div>
                <label className="block text-xs font-medium text-gray-700">Label</label>
                <input
                  type="text"
                  value={selectedNode.data.label}
                  onChange={(e) => {
                    setNodes((nds) =>
                      nds.map((node) =>
                        node.id === selectedNode.id
                          ? { ...node, data: { ...node.data, label: e.target.value } }
                          : node
                      )
                    );
                  }}
                  className="w-full px-2 py-1 text-sm border rounded"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700">Type</label>
                <select
                  value={selectedNode.data.type}
                  onChange={(e) => {
                    setNodes((nds) =>
                      nds.map((node) =>
                        node.id === selectedNode.id
                          ? { ...node, data: { ...node.data, type: e.target.value } }
                          : node
                      )
                    );
                  }}
                  className="w-full px-2 py-1 text-sm border rounded"
                >
                  <option value="llm">LLM Task</option>
                  <option value="data">Data Processing</option>
                  <option value="api">API Call</option>
                  <option value="condition">Condition</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowBuilder;
