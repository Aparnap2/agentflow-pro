'use client';

import { useState } from 'react';
import { AgentInteraction } from '@/components/agent/AgentInteraction';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function AgentsPage() {
  const [activeTab, setActiveTab] = useState('interact');
  const [results, setResults] = useState<Record<string, any>>({});

  const handleResult = (result: any, tab: string) => {
    setResults(prev => ({
      ...prev,
      [tab]: result
    }));
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Agent Interactions</h1>
      
      <Tabs 
        value={activeTab} 
        onValueChange={setActiveTab}
        className="space-y-4"
      >
        <TabsList>
          <TabsTrigger value="interact">Interact</TabsTrigger>
          <TabsTrigger value="research">Research Agent</TabsTrigger>
          <TabsTrigger value="sales">Sales Agent</TabsTrigger>
          <TabsTrigger value="support">Support Agent</TabsTrigger>
          <TabsTrigger value="content">Content Agent</TabsTrigger>
        </TabsList>

        <TabsContent value="interact" className="pt-4">
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Custom Agent Interaction</h2>
              <AgentInteraction 
                onResult={(result) => handleResult(result, 'custom')}
              />
            </div>

            {results.custom && (
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-lg font-medium mb-2">Latest Result</h3>
                <pre className="text-sm bg-white p-4 rounded overflow-auto max-h-96">
                  {JSON.stringify(results.custom, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="research" className="pt-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Research Agent</h2>
            <AgentInteraction 
              defaultAgentType="research"
              defaultTask="Research the latest trends in AI for 2024"
              onResult={(result) => handleResult(result, 'research')}
            />
          </div>
        </TabsContent>

        <TabsContent value="sales" className="pt-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Sales Agent</h2>
            <AgentInteraction 
              defaultAgentType="sales"
              defaultTask="Qualify this lead and suggest next steps"
              onResult={(result) => handleResult(result, 'sales')}
            />
          </div>
        </TabsContent>

        <TabsContent value="support" className="pt-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Support Agent</h2>
            <AgentInteraction 
              defaultAgentType="support"
              defaultTask="Help me troubleshoot my login issue"
              onResult={(result) => handleResult(result, 'support')}
            />
          </div>
        </TabsContent>

        <TabsContent value="content" className="pt-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Content Agent</h2>
            <AgentInteraction 
              defaultAgentType="content"
              defaultTask="Write a blog post about AI in healthcare"
              onResult={(result) => handleResult(result, 'content')}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
