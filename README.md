# ConvergeAI - Multi-Agent Service Platform

AI-powered service booking platform with intelligent complaint management.

## 🏗️ Project Structure

```
ConvergeAI/
├── backend/              # Python/FastAPI backend
├── customer-frontend/    # Customer-facing React app
└── ops-frontend/         # Operations dashboard React app
```

Note: Only the three main application folders are tracked in git. All other folders (database, docs, deployment, etc.) are ignored.

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

### Customer Frontend
```bash
cd customer-frontend
npm install
npm run dev
```

### Operations Frontend
```bash
cd ops-frontend
npm install
npm run dev
```

## 🐳 Docker Setup

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down
```

## 🔧 Development

Each application has its own README with detailed setup instructions:
- Backend: See `backend/README.md`
- Customer Frontend: See `customer-frontend/README.md`
- Operations Frontend: See `ops-frontend/README.md`

## 📦 Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, LangGraph, LangChain
- **Frontend:** React, Next.js, TypeScript, Tailwind CSS
- **Database:** MySQL 8.0+
- **Vector DB:** Qdrant (self-hosted)
- **Cache:** Redis
- **LLM:** Google Gemini (tiered strategy)
- **Embeddings:** Google text-embedding-004
- **Voice:** Deepgram (STT), Google Cloud TTS
- **Monitoring:** LangSmith, Prometheus, Grafana

## 📄 License

Proprietary - All rights reserved
