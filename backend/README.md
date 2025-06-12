# AgentFlow Pro Backend

This is the backend service for AgentFlow Pro, built with FastAPI and various AI technologies, featuring a Neo4j graph database for knowledge representation and agent coordination.

## Features

- **AI Orchestration**: Multi-agent workflow with LangGraph
- **LLM Integration**: Support for multiple models via OpenRouter including:
  - DeepSeek (deepseek-chat, deepseek-coder)
  - Qwen (7B, 14B, 32B variants)
  - Google Gemini (gemini-pro, gemini-1.5-flash)
  
- **Graph Database**: Neo4j for knowledge representation and agent coordination
- **Vector Database**: Qdrant for RAG (Retrieval-Augmented Generation)
- **Graph RAG**: Graphiti MCP for memory consistency
- **Monitoring**: Langfuse integration for LLM observability
- **Web Crawling**: Crawl4AI for web content extraction
- **Slack Integration**: For notifications and interactions

## Getting Started

### Prerequisites

- Python 3.10+
- Neo4j 5.x (local or AuraDB)
- Docker (for local development)

### Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your Neo4j credentials:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_secure_password
   NEO4J_DATABASE=agentflow
   NEO4J_ENCRYPTED=false
   ```

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

4. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`.

## Database Schema

AgentFlow Pro uses Neo4j to model agents, crews, workflows, and their relationships:

- **Agent**: Represents an AI agent with specific capabilities
- **Crew**: A group of agents working together
- **Workflow**: Defines a sequence of tasks
- **Task**: A unit of work in a workflow
- **Message**: Communication between agents and users

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## OpenRouter Integration

The system uses OpenRouter as the primary LLM provider, which gives access to multiple AI models through a single API. Here's how it works:

### Supported Models

| Model Name | Provider | Best For | Max Tokens |
|------------|----------|----------|------------|
| deepseek-chat | DeepSeek | General purpose chat | 32K |
| deepseek-coder-33b-instruct | DeepSeek | Code generation | 16K |
| qwen-14b-chat | Qwen | Balanced performance | 8K |
| google/gemini-pro | Google | General purpose | 32K |


### Configuration

1. Get your OpenRouter API key from [OpenRouter Dashboard](https://openrouter.ai/keys)
2. Add it to your `.env` file:
   ```
   OPENROUTER_API_KEY=your-api-key-here
   ```

### Usage

The system automatically routes tasks to the most appropriate model based on the task type:

- **Analysis tasks**: Uses DeepSeek models for strong reasoning
- **Programming tasks**: Uses DeepSeek Coder models
- **General tasks**: Uses Qwen for balanced performance
- **Fallback**: Uses DeepSeek Chat as a reliable default

You can also explicitly specify a model when making API calls by including the `model` parameter in your request.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and update the values
5. Run migrations:
   ```bash
   alembic upgrade head
   ```
6. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

To create a new migration:

```bash
alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:

```bash
alembic upgrade head
```

## Environment Variables

See `.env.example` for all available environment variables.

## Deployment

For production deployment, consider using:

- **Containerization**: Docker + Kubernetes
- **Cloud Providers**: AWS, GCP, or Azure
- **Serverless**: AWS Lambda, Google Cloud Functions

## License

[Your License Here]
