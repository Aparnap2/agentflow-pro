# CrewAI and LangGraph Integration

This document provides an overview of how to use the CrewAI and LangGraph integrations in the AgentFlow Pro platform.

## Table of Contents
- [Overview](#overview)
- [Setup](#setup)
- [CrewAI Integration](#crewai-integration)
- [LangGraph Integration](#langgraph-integration)
- [Example Usage](#example-usage)
- [Monitoring with Langfuse](#monitoring-with-langfuse)
- [Best Practices](#best-practices)

## Overview

The AgentFlow Pro platform now integrates with CrewAI for multi-agent collaboration and LangGraph for workflow orchestration. These integrations allow you to create sophisticated AI workflows with multiple agents working together.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.in
   ```

2. Set up your environment variables in a `.env` file:
   ```env
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key
   
   # Langfuse (optional)
   LANGFUSE_PUBLIC_KEY=your_public_key
   LANGFUSE_SECRET_KEY=your_secret_key
   LANGFUSE_HOST=https://cloud.langfuse.com
   
   # Redis
   REDIS_URL=redis://localhost:6379
   ```

## CrewAI Integration

The CrewAI integration allows you to create teams of agents that can work together on complex tasks.

### Key Features
- Create crews with multiple agents
- Define agent roles and responsibilities
- Enable agent delegation
- Monitor agent interactions

### Example Usage

```python
from app.ai.agents.agent_factory import agent_factory

# Create a crew
crew = agent_factory.crewai_integration.create_crew(
    crew_id="content_team",
    name="Content Creation Team",
    agent_ids=["researcher", "writer", "editor"],
    config={
        "process": "hierarchical",
        "verbose": True
    }
)

# Execute a task with the crew
result = await agent_factory.crewai_integration.execute_crew_task(
    crew_id="content_team",
    task="Create a blog post about AI in healthcare",
    context={"tone": "professional", "target_audience": "healthcare professionals"}
)
```

## LangGraph Integration

LangGraph provides a way to define complex workflows with conditional logic and state management.

### Key Features
- Define directed acyclic graphs (DAGs) of tasks
- Add conditional edges based on task outputs
- State management across workflow steps
- Integration with CrewAI agents

### Example Usage

```python
from app.ai.integrations import LangGraphIntegration

# Create a LangGraph integration instance
langgraph = LangGraphIntegration(agent_factory)

# Create a graph
graph = langgraph.create_graph(
    graph_id="content_workflow",
    config={
        "nodes": [
            {
                "node_id": "research",
                "node_type": "agent",
                "agent_id": "researcher"
            },
            {
                "node_id": "write",
                "node_type": "agent",
                "agent_id": "writer"
            }
        ],
        "edges": [
            {"source": "research", "target": "write"}
        ]
    }
)

# Execute the graph
result = await langgraph.execute_graph(
    graph_id="content_workflow",
    input_data={"topic": "AI in healthcare"}
)
```

## Monitoring with Langfuse

All agent and workflow executions are automatically logged to Langfuse for monitoring and observability.

### Key Features
- Trace all agent interactions
- Monitor workflow execution
- Track performance metrics
- Debug issues with detailed logs

### Example Query

```python
from app.ai.integrations import get_langfuse_integration

langfuse = get_langfuse_integration()

# Get traces for a workflow
traces = await langfuse.get_traces(
    name="workflow_execution",
    metadata={"workflow_id": "content_creation"}
)
```

## Best Practices

1. **Start Simple**: Begin with a small number of agents and simple workflows, then gradually add complexity.

2. **Monitor Performance**: Use Langfuse to monitor the performance of your agents and workflows.

3. **Error Handling**: Implement proper error handling in your workflows to handle failures gracefully.

4. **Documentation**: Document your agents, workflows, and their interactions for better maintainability.

5. **Testing**: Test your workflows with different inputs to ensure they handle edge cases properly.

6. **Resource Management**: Be mindful of API rate limits and resource usage when running multiple agents.

7. **Versioning**: Version your agents and workflows to track changes and roll back if needed.

## Troubleshooting

### Common Issues

1. **Agents not responding**: Check if the agent services are running and accessible.
2. **Workflow stuck**: Verify that all dependencies between steps are correctly defined.
3. **Authentication errors**: Ensure that all API keys are correctly set in your environment variables.
4. **Performance issues**: Monitor resource usage and consider scaling your infrastructure if needed.

For additional help, please refer to the documentation or open an issue in the repository.
