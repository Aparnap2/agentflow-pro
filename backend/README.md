# AgentFlow Pro Backend

This is the backend service for AgentFlow Pro, built with FastAPI and various AI technologies.

## Features

- **AI Orchestration**: Multi-agent workflow with LangGraph
- **LLM Integration**: Support for Gemini, OpenRouter (DeepSeek, Qwen), and OpenAI
- **Vector Database**: Qdrant for RAG (Retrieval-Augmented Generation)
- **Graph RAG**: Graphiti MCP for memory consistency
- **Database**: Aiven PostgreSQL for structured data
- **Monitoring**: Langfuse integration for LLM observability
- **Web Crawling**: Crawl4AI for web content extraction
- **Slack Integration**: For notifications and interactions

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
