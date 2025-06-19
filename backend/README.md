# AgentFlow Pro Backend

A scalable backend service for AgentFlow Pro, built with FastAPI and LangGraph for AI agent orchestration.

## Features

- **Multi-tenant Architecture**: Support for multiple organizations with isolated data
- **Authentication & Authorization**: JWT-based auth with role-based access control
- **Task Management**: Create, track, and manage AI agent tasks
- **Agent Orchestration**: Coordinate multiple AI agents using LangGraph
- **Vector Search**: Integration with Qdrant for semantic search
- **Real-time Updates**: WebSocket support for real-time communication
- **Billing & Subscriptions**: Stripe integration for payments
- **Rate Limiting**: Protect your API with tenant-based rate limiting

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **Vector Database**: Qdrant
- **Auth**: JWT
- **Payments**: Stripe
- **AI/ML**: LangChain, LangGraph, OpenAI
- **Monitoring**: Sentry

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Qdrant (for vector search)
- Stripe account (for payments)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agentflow-pro.git
   cd agentflow-pro/backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   # Apply migrations (you'll need to set up your migration tool)
   ```

### Configuration

Create a `.env` file with the following variables:

```env
# App
ENVIRONMENT=development
SECRET_KEY=your-secret-key

# Database
POSTGRES_URL=postgresql://user:password@localhost:5432/agentflow

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# OpenAI
OPENAI_API_KEY=your-openai-key

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-key

# Sentry (optional)
SENTRY_DSN=your-sentry-dsn
```

### Running the Application

```bash
# Start the development server
uvicorn app.main:app --reload

# Or with hot reload
uvicorn app.main:app --reload --reload-dir=app
```

The API will be available at `http://localhost:8000`

### API Documentation

- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   │
│   ├── api/               # API routes
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── tasks.py         # Task management
│   │   ├── agents.py        # Agent management
│   │   ├── billing.py       # Billing and subscriptions
│   │   └── health.py        # Health checks
│   │
│   ├── core/              # Core application logic
│   │   ├── __init__.py
│   │   └── config.py        # Configuration settings
│   │
│   ├── db/                # Database related code
│   │   ├── __init__.py
│   │   └── database.py      # Database connection and models
│   │
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   ├── base.py         # Base models and enums
│   │   ├── auth.py         # Auth related models
│   │   ├── task.py         # Task models
│   │   ├── agent.py        # Agent models
│   │   └── workflow.py     # Workflow models
│   │
│   ├── services/         # Business logic and services
│   │   ├── __init__.py
│   │   ├── auth_service.py  # Authentication logic
│   │   └── redis_service.py # Redis utilities
│   │
│   ├── agents/           # AI agent implementations
│   │   └── __init__.py
│   │
│   └── workflows/        # LangGraph workflows
│       └── __init__.py
│
├── tests/               # Test files
├── .env.example          # Example environment variables
├── requirements.txt      # Project dependencies
└── README.md            # This file
```

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/
```

## Deployment

### Docker

```bash
# Build the image
docker build -t agentflow-backend .

# Run the container
docker run -d --name agentflow-backend -p 8000:8000 --env-file .env agentflow-backend
```

### Kubernetes

Example deployment files are provided in the `k8s/` directory.

## API Rate Limiting

Rate limiting is implemented based on the tenant's subscription plan:

- **Starter**: 1,000 requests/day
- **Pro**: 10,000 requests/day
- **Enterprise**: 100,000 requests/day

## Error Handling

The API follows RESTful error handling conventions:

```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## License

[MIT](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For support, please open an issue in the GitHub repository.
