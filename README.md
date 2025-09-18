# AI Research Agent

A full-stack AI Research Agent that accepts research topics, runs automated research workflows, and returns structured results with explainable traces.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Background     │
                       │  Jobs (Celery)  │
                       │                 │
                       └─────────────────┘
```

## 🚀 Features

- **Research Workflow**: 5-step automated research process
- **External API Integration**: Fetches data from Wikipedia and HackerNews
- **Background Processing**: Async task execution with Celery
- **Real-time Updates**: WebSocket support for live progress tracking
- **Structured Results**: Organized summaries and keyword extraction
- **Full Audit Trail**: Complete workflow logging and traceability

## 📋 Workflow Steps

1. **Input Parsing**: Validate and store research request
2. **Data Gathering**: Fetch articles from external APIs
3. **Processing**: Extract top 5 articles, summarize, and extract keywords
4. **Result Persistence**: Save processed results and logs
5. **Return Results**: Deliver structured output to frontend

## 🛠️ Tech Stack

### Backend
- **FastAPI** (Python) - High-performance API framework
- **Celery** - Distributed task queue for background jobs
- **Redis** - Message broker and caching
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and serialization

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **ShadCN/UI** - Modern component library
- **React Query** - Server state management

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/1234-ad/ai-research-agent.git
cd ai-research-agent
```

2. **Start with Docker Compose**
```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start Redis (required for Celery)
redis-server

# Start Celery worker
celery -A app.celery worker --loglevel=info

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Deployment

### Backend Deployment (Render)
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set environment variables from `.env.example`
4. Deploy automatically on git push

### Frontend Deployment (Vercel)
1. Connect repository to Vercel
2. Set environment variables
3. Deploy with zero configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/research_agent
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 API Endpoints

### Research Endpoints
- `POST /api/research` - Submit new research topic
- `GET /api/research` - List all research requests
- `GET /api/research/{id}` - Get specific research details
- `GET /api/research/{id}/logs` - Get workflow logs

### WebSocket
- `WS /ws/research/{id}` - Real-time progress updates

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📁 Project Structure

```
ai-research-agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── tasks/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   ├── public/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🔧 Development Notes

### Trade-offs & Decisions
1. **FastAPI vs Node.js**: Chose FastAPI for better async support and data science ecosystem
2. **Celery vs RQ**: Celery for production-grade features and monitoring
3. **PostgreSQL vs SQLite**: PostgreSQL for better concurrent access and production readiness
4. **Real-time Updates**: WebSocket implementation for better UX

### Performance Considerations
- Background job processing prevents API timeouts
- Redis caching for frequently accessed data
- Database indexing on search fields
- Pagination for large result sets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Live Demo

- **Frontend**: [Deployed on Vercel]
- **Backend**: [Deployed on Render]
- **API Docs**: [Backend URL]/docs

---

Built with ❤️ for the AI Research Agent Challenge