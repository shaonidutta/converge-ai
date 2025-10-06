# ConvergeAI Backend - Quick Start Guide

Get up and running with ConvergeAI backend in 5 minutes!

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Steps

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env file** (Add your API keys)
   ```bash
   # Required: Add these keys to .env
   GOOGLE_API_KEY=your_google_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   ```

4. **Start all services**
   ```bash
   docker-compose up -d
   ```

5. **Check if services are running**
   ```bash
   docker-compose ps
   ```

6. **Access the API**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

That's it! 🎉

---

## Local Development (Without Docker)

### Prerequisites
- Python 3.12+
- MySQL 8.0+
- Redis

### Steps

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Copy and configure .env**
   ```bash
   cp .env.example .env
   # Edit .env with your database and API credentials
   ```

4. **Start MySQL and Redis**
   ```bash
   # Using Docker
   docker run -d -p 3306:3306 --name mysql \
     -e MYSQL_ROOT_PASSWORD=root \
     -e MYSQL_DATABASE=convergeai_db \
     mysql:8.0

   docker run -d -p 6379:6379 --name redis redis:7-alpine
   ```

5. **Start the FastAPI server**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Start Celery worker** (in another terminal)
   ```bash
   celery -A src.tasks.celery_app worker --loglevel=info
   ```

7. **Access the API**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 🧪 Verify Installation

### Test API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ConvergeAI Backend",
  "version": "1.0.0",
  "components": {
    "api": "healthy"
  }
}
```

### Test API Docs
Open in browser: http://localhost:8000/docs

You should see the Swagger UI with API documentation.

---

## Access Monitoring Tools

### With Docker Compose

- **Flower (Celery Monitoring)**: http://localhost:5555
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3002
  - Username: `admin`
  - Password: `admin`

---

## Stop Services

### Docker
```bash
docker-compose down
```

### Local Development
- Press `Ctrl+C` in each terminal running a service
- Stop MySQL and Redis containers:
  ```bash
  docker stop mysql redis
  docker rm mysql redis
  ```

---

## Common Commands

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild images
docker-compose build

# Rebuild and start
docker-compose up -d --build
```

### Development

```bash
# Format code
black .
isort .

# Lint code
flake8 .
pylint src/

# Type checking
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

---

## Troubleshooting

### Port Already in Use

If you get "port already in use" error:

```bash
# Find process using port 8000
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

### Docker Services Not Starting

```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs

# Restart Docker Desktop
```

### Database Connection Error

```bash
# Check MySQL is running
docker-compose ps mysql

# Check MySQL logs
docker-compose logs mysql

# Verify .env database credentials
```

### Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Next Steps

1. **Phase 2**: Set up database schema and models
2. **Phase 3**: Configure core services (database, cache, security)
3. **Phase 4**: Implement authentication
4. **Phase 5**: Build API endpoints

See `TASKLIST.md` for detailed implementation roadmap.

---

## Tips

- Use Docker Compose for development - it's easier!
- Check `logs/` directory for application logs
- Use `/docs` endpoint to explore API interactively
- Run tests before committing code
- Use pre-commit hooks to maintain code quality

---

## Need Help?

- Check `README.md` for detailed documentation
- Review `PHASE1_COMPLETION_SUMMARY.md` for setup details
- Open an issue on GitHub
- Contact the development team

---

**Happy Coding! 🚀**

