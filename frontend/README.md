# AgentFlow Pro Frontend

This is the frontend application for AgentFlow Pro, a platform for creating, managing, and orchestrating AI agents and workflows.

## Features

- **Agent Studio**: Create and manage AI agents with different roles and capabilities
- **Agent Factory**: Use templates to quickly create specialized agents
- **Task Orchestrator**: Execute complex tasks using agent teams and workflows
- **Analytics**: Track agent performance and task execution metrics
- **Integrations**: Connect agents to external tools and services

## API Integration

The frontend connects to the backend API using the following services:

### Agent API

- `GET /api/v1/agents/list` - List all agents
- `POST /api/v1/agents/create` - Create a new agent
- `POST /api/v1/agents/{agent_id}/process` - Process a task with an agent

### Crew API

- `GET /api/v1/agents/crews/list` - List all crews
- `POST /api/v1/agents/crews/create` - Create a new crew
- `POST /api/v1/agents/crews/{crew_id}/execute` - Execute a task with a crew

### Workflow API

- `GET /api/v1/workflows` - List all workflows
- `GET /api/v1/workflows/{workflow_id}` - Get a specific workflow
- `POST /api/v1/workflows` - Create a new workflow
- `POST /api/v1/workflows/{workflow_id}/execute` - Execute a workflow
- `GET /api/v1/workflows/executions/{execution_id}` - Get workflow execution status
- `GET /api/v1/workflows/executions` - List workflow executions

### Chat API

- `POST /api/v1/chat` - Send a chat message to the AI orchestrator

## Custom Hooks

The application uses custom React hooks to interact with the API:

- `useAgents()` - For agent operations
- `useCrews()` - For crew operations
- `useWorkflows()` - For workflow operations
- `useChat()` - For chat operations

## Getting Started

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

3. Build for production:
   ```
   npm run build
   ```

## Environment Configuration

Create a `.env` file in the root directory with the following variables:

```
VITE_API_URL=http://localhost:8000
```

## Dependencies

- React
- React Router
- Axios
- Lucide React (for icons)
- TailwindCSS (for styling)