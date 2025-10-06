# ConvergeAI Backend

**Multi-Agent Customer Service Platform powered by LangChain, LangGraph, and Google Gemini**

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## Overview

ConvergeAI is an intelligent customer service platform that uses multiple specialized AI agents to handle various customer interactions including bookings, cancellations, complaints, and policy queries. The system leverages LangGraph for orchestrating multi-agent workflows and Google Gemini models for natural language understanding and generation.

### Key Features

- **Multi-Agent Architecture**: Specialized agents for different tasks (Booking, Cancellation, Complaint, Policy, Service, SQL)
- **Intelligent Routing**: Coordinator agent routes requests to appropriate specialist agents
- **RAG-based Policy Agent**: Retrieves and grounds responses in company policies
- **Natural Language to SQL**: Ops users can query data using natural language
- **Real-time Chat**: WebSocket support for streaming responses
- **Comprehensive Monitoring**: Prometheus metrics, structured logging, and distributed tracing
- **Scalable Design**: Async architecture with Celery for background tasks

## Tech Stack

### Core Framework
- **FastAPI** (0.115.5) - Modern, fast web framework
- **Python** (3.12+) - Programming language
- **Uvicorn** - ASGI server

### Database & Caching
- **MySQL** (8.0+) - Primary database
- **Redis** - Caching and Celery broker
- **Pinecone** - Vector database for embeddings

### AI/ML Stack
- **LangChain** (0.3.13) - LLM application framework
- **LangGraph** (0.2.59) - Multi-agent orchestration
- **Google Gemini** - LLM models (2.0 Flash, 1.5 Flash, 1.5 Pro)
- **Transformers** - NLP models (sentiment analysis)
- **Sentence Transformers** - Text embeddings

### Background Tasks
- **Celery** (5.4.0) - Distributed task queue
- **Flower** - Celery monitoring

### Monitoring & Observability
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **OpenTelemetry** - Distributed tracing
- **Loguru** - Structured logging

## Project Structure

```
backend/
├── src/
│   ├── agents/              # Multi-agent system
│   │   ├── base/           # Base agent classes
│   │   ├── coordinator/    # Coordinator agent
│   │   ├── booking/        # Booking agent
│   │   ├── cancellation/   # Cancellation agent
│   │   ├── complaint/      # Complaint agent
│   │   ├── policy/         # RAG-based policy agent
│   │   ├── service/        # Service information agent
│   │   └── sql/            # Natural language to SQL agent
│   ├── api/                # API routes
│   │   ├── v1/            # API version 1
│   │   │   ├── endpoints/ # Route handlers
│   │   │   └── dependencies/ # FastAPI dependencies
│   │   └── middleware/    # Custom middleware
│   ├── core/              # Core functionality
│   │   ├── database/      # Database connection
│   │   ├── cache/         # Redis cache
│   │   ├── security/      # Authentication & authorization
│   │   ├── models/        # SQLAlchemy models
│   │   ├── repositories/  # Data access layer
│   │   └── services/      # Business logic
│   ├── llm/               # LLM integration
│   │   ├── gemini/        # Gemini client
│   │   ├── prompts/       # Prompt templates
│   │   └── cache/         # LLM response caching
│   ├── nlp/               # NLP services
│   │   ├── intent/        # Intent classification
│   │   ├── ner/           # Named entity recognition
│   │   └── sentiment/     # Sentiment analysis
│   ├── rag/               # RAG components
│   │   ├── embeddings/    # Embedding generation
│   │   ├── retrieval/     # Vector search
│   │   ├── prompts/       # RAG prompts
│   │   └── vector_store/  # Pinecone integration
│   ├── tasks/             # Celery tasks
│   │   ├── celery_app/    # Celery configuration
│   │   └── workers/       # Task definitions
│   ├── monitoring/        # Monitoring & logging
│   │   ├── metrics/       # Prometheus metrics
│   │   ├── logging/       # Logging configuration
│   │   └── tracing/       # OpenTelemetry tracing
│   ├── config/            # Configuration management
│   ├── models/            # Pydantic models
│   ├── schemas/           # API schemas
│   ├── repositories/      # Repository pattern
│   ├── services/          # Service layer
│   ├── middleware/        # Custom middleware
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── fixtures/         # Test fixtures
├── data/                  # Data directory
│   ├── uploads/          # File uploads
│   ├── cache/            # Cache files
│   ├── models/           # ML models
│   └── vector_store/     # Vector embeddings
├── logs/                  # Application logs
├── scripts/               # Utility scripts
│   ├── migrations/       # Database migrations
│   └── seeds/            # Seed data
├── config/                # Configuration files
├── deployment/            # Deployment configs
│   ├── docker/           # Docker files
│   ├── kubernetes/       # K8s manifests
│   └── monitoring/       # Monitoring configs
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Local development setup
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- MySQL 8.0+
- Redis
- Pinecone account
- Google Cloud account (for Gemini API)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ConvergeAI/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Run with Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - MySQL database
   - Redis cache
   - FastAPI backend
   - Celery worker
   - Celery beat
   - Flower (Celery monitoring)
   - Prometheus
   - Grafana

6. **Access the services**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Flower: http://localhost:5555
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3002

## Development

### Running Locally (Without Docker)

1. **Start MySQL and Redis**
   ```bash
   # Using Docker
   docker run -d -p 3306:3306 --name mysql -e MYSQL_ROOT_PASSWORD=root mysql:8.0
   docker run -d -p 6379:6379 --name redis redis:7-alpine
   ```

2. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

3. **Start the FastAPI server**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start Celery worker (in another terminal)**
   ```bash
   celery -A src.tasks.celery_app worker --loglevel=info
   ```

5. **Start Celery beat (in another terminal)**
   ```bash
   celery -A src.tasks.celery_app beat --loglevel=info
   ```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .
pylint src/

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py

# Run specific test
pytest tests/unit/test_agents.py::test_coordinator_agent
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Environment Variables

See `.env.example` for all available environment variables. Key variables:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - MySQL configuration
- `REDIS_HOST`, `REDIS_PORT` - Redis configuration
- `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT` - Pinecone configuration
- `GOOGLE_API_KEY` - Google Gemini API key
- `JWT_SECRET_KEY` - JWT secret for authentication

## 📊 Monitoring

- **Metrics**: Prometheus metrics available at `/metrics`
- **Health Check**: `/health` endpoint
- **Logs**: Structured JSON logs in `logs/` directory
- **Tracing**: OpenTelemetry traces (if enabled)

## 🚢 Deployment

### Docker Production Build

```bash
docker build --target production -t convergeai-backend:latest .
docker run -p 8000:8000 --env-file .env convergeai-backend:latest
```

### Kubernetes

```bash
kubectl apply -f deployment/kubernetes/
```

## 📝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## 📄 License

MIT License

## 👥 Team

ConvergeAI Development Team

## 📞 Support

For issues and questions, please open an issue on GitHub.

