# Multi-Agent Lead Research & Competitive Intelligence System

A powerful system that automatically discovers competitors, gathers lead data via LinkedIn and Apollo API, creates structured profiles, and enables chat interaction using LLM embeddings.

## 🚀 Features

### Core Functionality
- **Competitor Discovery Agent**: Automatically finds competitors using LLM and web search
- **Lead Data Agent**: Fetches company and contact data via Apollo API and generates profiles
- **Embedding & Retrieval Agent**: Converts data into embeddings for semantic search and chat
- **Multi-Agent Orchestrator**: Runs multiple research agents in parallel for scalability
- **Chat Interface**: Query collected intelligence using natural language

### Use Case Example
Input: "Find 20 competitors of Lemlist, get their team data"
Output: Structured database of competitor companies with enriched lead profiles + chat interface

## 🛠 Tech Stack

**Backend:**
- FastAPI (Python)
- OpenRouter for LLM access (GPT-4, Claude)
- Apollo API for lead enrichment
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- SQLite for structured data storage
- AsyncIO for multi-agent concurrency

**Frontend:**
- Next.js 14 with TypeScript
- Tailwind CSS for styling
- Axios for API communication

**Infrastructure:**
- Docker & Docker Compose
- RESTful API design

## 📋 Prerequisites

1. **OpenRouter API Key** - For LLM access (required)
2. **Apollo API Key** - For lead enrichment (optional, system works with mock data)
3. **Docker & Docker Compose** - For containerization
4. **Node.js 18+** - For frontend development
5. **Python 3.11+** - For backend development

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd aiscraperagent

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
APOLLO_API_KEY=your_apollo_api_key_here  # Optional
```

**Getting API Keys:**
- **OpenRouter**: Sign up at [openrouter.ai](https://openrouter.ai) and get your API key
- **Apollo**: Sign up at [apollo.io](https://apollo.io) for lead enrichment (free tier available)

### 3. Run with Docker (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Backend will be available at: http://localhost:8000
# Frontend will be available at: http://localhost:3000
# API docs available at: http://localhost:8000/docs
```

### 4. Manual Setup (Development)

**Backend:**
```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd client
npm install
npm run dev
```

## 🎯 API Usage Examples

### 1. Discover Competitors
```bash
curl -X POST "http://localhost:8000/api/competitors/discover" \
  -H "Content-Type: application/json" \
  -d '{"seed_company": "Apollo.io", "max_competitors": 10}'
```

### 2. Launch Multi-Agent Research
```bash
curl -X POST "http://localhost:8000/api/research/launch" \
  -H "Content-Type: application/json" \
  -d '{"seed_company": "Lemlist", "max_competitors": 5}'
```

### 3. Research Single Company
```bash
curl -X POST "http://localhost:8000/api/company/research" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "HubSpot", "max_leads": 20}'
```

### 4. Chat with Data
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many SDRs work at these companies?"}'
```

### 5. Get Agent Status
```bash
curl "http://localhost:8000/api/agents/status"
```

## 🏗 System Architecture

### Multi-Agent Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Competitor  │  │    Lead     │  │  Embedding  │         │
│  │ Discovery   │  │    Data     │  │   Agent     │         │
│  │   Agent     │  │   Agent     │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │    SQLite DB    │         │   ChromaDB      │
    │  (Structured)   │         │  (Embeddings)   │
    └─────────────────┘         └─────────────────┘
```

### Data Flow

1. **Input**: Seed company name (e.g., "Apollo.io")
2. **Competitor Discovery**: LLM + web search find competitors
3. **Parallel Research**: Multiple agents research each company
4. **Data Collection**: Company profiles + lead data via Apollo API
5. **Embedding**: All data converted to vectors for semantic search
6. **Storage**: Structured data in SQLite, embeddings in ChromaDB
7. **Chat Interface**: Natural language queries over collected data

## 📁 Project Structure

```
aiscraperagent/
├── server/                    # FastAPI Backend
│   ├── main.py               # FastAPI app entry point
│   ├── models.py             # Pydantic data models
│   ├── database.py           # SQLite database manager
│   ├── competitor_agent.py   # Competitor discovery logic
│   ├── lead_agent.py         # Lead data collection
│   ├── embedding_agent.py    # Vector embeddings & chat
│   ├── orchestrator.py       # Multi-agent coordination
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend container
├── client/                   # Next.js Frontend
│   ├── app/                 # Next.js 14 app directory
│   ├── components/          # React components
│   ├── lib/                 # API client & utilities
│   └── Dockerfile          # Frontend container
├── docker-compose.yml       # Multi-service orchestration
├── .env.example            # Environment template
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM access | Yes | - |
| `APOLLO_API_KEY` | Apollo API key for lead enrichment | No | dummy_key |
| `MAX_CONCURRENT_AGENTS` | Maximum parallel agents | No | 5 |
| `DATABASE_URL` | SQLite database path | No | sqlite:///./leads.db |
| `EMBEDDING_MODEL` | Sentence transformer model | No | all-MiniLM-L6-v2 |

### Agent Configuration

- **Concurrency**: Up to 5 agents run in parallel by default
- **Timeout**: 300 seconds per agent task
- **Retry Logic**: Built-in error handling and retries
- **Progress Tracking**: Real-time status updates via WebSocket-like polling

## 🎮 Usage Workflows

### 1. Competitor Research Workflow
```bash
# Discover competitors
POST /api/competitors/discover
{"seed_company": "Apollo.io", "max_competitors": 10}

# Launch multi-agent research
POST /api/research/launch  
{"seed_company": "Apollo.io", "max_competitors": 10}

# Monitor progress
GET /api/agents/status

# View results
GET /api/companies
GET /api/summary
```

### 2. Single Company Deep Dive
```bash
# Research specific company
POST /api/company/research
{"company_name": "HubSpot", "max_leads": 20}

# Get company details
GET /api/companies/HubSpot/leads

# Chat about findings
POST /api/chat
{"question": "Tell me about HubSpot's sales team structure"}
```

### 3. Intelligence Analysis
```bash
# Search across all data
GET /api/search?q=sales+director

# Get research summary
GET /api/summary

# Ask analytical questions
POST /api/chat
{"question": "Which companies have raised funding recently?"}
```

## 📊 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/competitors/discover` | Find competitors for seed company |
| POST | `/api/research/launch` | Start multi-agent research |
| POST | `/api/company/research` | Research single company |
| POST | `/api/chat` | Chat with collected data |
| GET | `/api/agents/status` | Get all agent statuses |
| GET | `/api/companies` | List all companies |
| GET | `/api/companies/{name}/leads` | Get company leads |
| GET | `/api/search` | Search across data |
| GET | `/api/summary` | Get research summary |
| GET | `/health` | Health check |

### Response Formats

**Company Profile:**
```json
{
  "name": "HubSpot",
  "domain": "hubspot.com",
  "description": "CRM and marketing software",
  "industry": "Software",
  "size": "1000-5000 employees",
  "location": "Cambridge, MA",
  "founded": "2006",
  "employees_count": 3000,
  "linkedin_url": "https://linkedin.com/company/hubspot",
  "website": "https://hubspot.com"
}
```

**Lead Profile:**
```json
{
  "name": "John Smith",
  "title": "VP of Sales",
  "company": "HubSpot",
  "email": "john.smith@hubspot.com",
  "linkedin_url": "https://linkedin.com/in/johnsmith",
  "phone": "+1-555-0123",
  "location": "Boston, MA",
  "department": "Sales",
  "seniority": "VP"
}
```

## 🚨 Troubleshooting

### Common Issues

1. **"System not initialized" error**
   - Ensure OPENROUTER_API_KEY is set correctly
   - Check server logs for startup errors

2. **No competitors found**
   - Try different seed company names
   - Check OpenRouter API quota/limits

3. **Apollo API errors**
   - Verify Apollo API key is valid
   - System works with mock data if Apollo fails

4. **Port conflicts**
   - Change ports in docker-compose.yml if 3000/8000 are taken

5. **Permission errors**
   - Ensure Docker has proper permissions
   - On Windows, run as administrator if needed

### Logs and Debugging

```bash
# View backend logs
docker-compose logs backend

# View frontend logs  
docker-compose logs frontend

# Interactive debugging
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🔮 Roadmap & Enhancement Ideas

### Immediate Improvements
- [ ] Add authentication system
- [ ] Implement rate limiting
- [ ] Add data export functionality
- [ ] Enhanced error handling
- [ ] Add more LLM providers

### Advanced Features
- [ ] Genetic algorithm for lead ranking
- [ ] Job board crawling for hiring insights
- [ ] Real-time agent status WebSocket
- [ ] Advanced filtering and search
- [ ] Company org chart visualization
- [ ] Email outreach templates
- [ ] CRM integrations

### Scalability
- [ ] PostgreSQL for production
- [ ] Redis for caching
- [ ] Kubernetes deployment
- [ ] Horizontal agent scaling
- [ ] Background job queue

## ⚖️ Legal Considerations

- **Web Scraping**: Use responsibly, respect robots.txt
- **API Usage**: Follow Apollo and OpenRouter terms of service
- **Data Privacy**: Ensure compliance with GDPR/CCPA
- **Rate Limits**: Implement appropriate delays and respect API limits

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create new issue with detailed description
4. Include logs and environment details

---

**Built with ❤️ for efficient competitive intelligence and lead research**
