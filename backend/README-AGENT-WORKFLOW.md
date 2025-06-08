# Agent Workflow System

A powerful workflow system for orchestrating AI agents to accomplish complex tasks.

## Overview

The Agent Workflow System provides a structured way to define, execute, and monitor multi-step workflows involving AI agents. It supports:

- Sequential and parallel task execution
- Conditional branching and loops
- Error handling and retries
- State persistence
- Real-time monitoring and logging
- Integration with various AI models and services

## Key Components

### 1. BaseAgent

The foundation for all agents, providing:
- Retry logic with exponential backoff
- Circuit breaker pattern
- State management
- Metrics collection
- Error handling and logging

### 2. AgentFactory

Manages agent lifecycle and state persistence:
- Singleton pattern for centralized management
- Redis-based state persistence
- Agent registration and retrieval
- Health monitoring

### 3. AgentWorkflow

Orchestrates the execution of agent tasks:
- Define workflows with multiple steps
- Handle dependencies between steps
- Support for different step types (agent tasks, API calls, etc.)
- Input templating and transformation
- Timeout and retry policies

### 4. API Endpoints

RESTful API for managing and executing workflows:
- Create, read, update, delete workflows
- Execute workflows synchronously or asynchronously
- Monitor execution status and results
- List workflows and executions

## Getting Started

### Prerequisites

- Python 3.8+
- Redis server
- Qdrant vector database (for embeddings)
- OpenAI API key (or other LLM provider)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-chatbot.git
   cd ai-chatbot/backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Set up environment variables (create a `.env` file):
   ```env
   # Redis
   REDIS_URL=redis://localhost:6379
   REDIS_PASSWORD=your_redis_password
   
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key
   
   # Qdrant
   QDRANT_URL=http://localhost:6333
   
   # Other settings
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

### Running the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000/api/v1`.

## Usage Examples

### Creating a Workflow

```python
from app.ai.workflow.agent_workflow import AgentWorkflow, AgentWorkflowStep, AgentWorkflowStepType
from app.ai.agents.agent_factory import agent_factory

async def create_lead_workflow():
    workflow = AgentWorkflow(
        workflow_id="lead_processing",
        name="Lead Processing Workflow",
        agent_factory=agent_factory
    )
    
    # Add steps to the workflow
    workflow.add_step(AgentWorkflowStep(
        step_id="qualify_lead",
        name="Qualify Lead",
        step_type=AgentWorkflowStepType.AGENT_TASK,
        agent_type="sales",
        task="qualify_lead",
        parameters={"priority": "high"}
    ))
    
    workflow.add_step(AgentWorkflowStep(
        step_id="enrich_lead",
        name="Enrich Lead Data",
        step_type=AgentWorkflowStepType.AGENT_TASK,
        agent_type="research",
        task="enrich_lead",
        depends_on=["qualify_lead"]
    ))
    
    return workflow
```

### Executing a Workflow via API

```bash
# Create a workflow
curl -X POST "http://localhost:8000/api/v1/workflows/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lead Processing",
    "description": "Process and qualify new leads",
    "steps": [
      {
        "step_id": "qualify_lead",
        "name": "Qualify Lead",
        "step_type": "agent_task",
        "agent_type": "sales",
        "task": "qualify_lead",
        "parameters": {"priority": "high"}
      },
      {
        "step_id": "enrich_lead",
        "name": "Enrich Lead Data",
        "step_type": "agent_task",
        "agent_type": "research",
        "task": "enrich_lead",
        "depends_on": ["qualify_lead"]
      }
    ]
  }'

# Execute the workflow
curl -X POST "http://localhost:8000/api/v1/workflows/{workflow_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "lead": {
        "name": "Acme Corp",
        "email": "contact@acmecorp.com",
        "website": "https://acmecorp.com",
        "budget": 50000,
        "timeframe": "Q3 2023",
        "requirements": "AI solution for customer support"
      }
    },
    "async_execution": false
  }'
```

## Testing

Run the test suite:

```bash
pytest tests/
```

For a more detailed test of the workflow system:

```bash
python -m scripts.test_agent_workflow
```

## Monitoring and Logging

- All workflow executions are logged to `agent_workflow_test.log`
- Metrics are collected and can be exported to monitoring systems
- Error tracking is integrated with Sentry (if configured)

## Best Practices

1. **Idempotency**: Design agent tasks to be idempotent when possible.
2. **Error Handling**: Implement comprehensive error handling and retries.
3. **State Management**: Use the built-in state management for critical data.
4. **Monitoring**: Monitor workflow execution times and error rates.
5. **Security**: Follow security best practices for API keys and sensitive data.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
