# Setup Instructions

## Prerequisites

Before setting up the AI Scraper Agent system, ensure you have the following installed:

### Required Software

1. **Docker & Docker Compose** (Recommended)
   - Download from [docker.com](https://docker.com)
   - Verify installation: `docker --version` and `docker-compose --version`

2. **Node.js 18+** (For manual frontend setup)
   - Download from [nodejs.org](https://nodejs.org)
   - Verify installation: `node --version` and `npm --version`

3. **Python 3.11+** (For manual backend setup)
   - Download from [python.org](https://python.org)
   - Verify installation: `python --version` and `pip --version`

4. **Git** (For cloning the repository)
   - Download from [git-scm.com](https://git-scm.com)
   - Verify installation: `git --version`

### Required API Keys

1. **OpenRouter API Key** (Required)
   - Sign up at [openrouter.ai](https://openrouter.ai)
   - Navigate to API Keys section
   - Generate a new API key
   - Copy and save the key securely

2. **Apollo API Key** (Optional but recommended)
   - Sign up at [apollo.io](https://apollo.io)
   - Go to Settings → Integrations → API
   - Generate a new API key
   - Copy and save the key securely

## Quick Start (Docker - Recommended)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd aiscraperagent
```

### 2. Environment Configuration

Copy the example environment file:

```bash
# On Windows
copy .env.example .env

# On macOS/Linux
cp .env.example .env
```

Edit the `.env` file with your API keys:

```env
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional (system works with mock data without this)
APOLLO_API_KEY=your_apollo_api_key_here

# Agent Configuration (defaults are fine)
MAX_CONCURRENT_AGENTS=5
```

### 3. Build and Run with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 4. Access the Application

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Verify Installation

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Multi-Agent Lead Research System is running"
}
```

## Manual Setup (Development)

### Backend Setup

1. **Navigate to Server Directory**

```bash
cd server
```

2. **Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Set Environment Variables**

Create a `.env` file in the server directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
APOLLO_API_KEY=your_apollo_api_key_here
MAX_CONCURRENT_AGENTS=5
```

5. **Run the Backend**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to Client Directory**

```bash
cd client
```

2. **Install Dependencies**

```bash
npm install
```

3. **Start Development Server**

```bash
npm run dev
```

4. **Access Frontend**

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Configuration Options

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key_here
APOLLO_API_KEY=your_apollo_api_key_here

# Agent Configuration
MAX_CONCURRENT_AGENTS=5

# Database Configuration
DATABASE_URL=sqlite:///./leads.db

# Embedding Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Development Settings
DEBUG=false
LOG_LEVEL=INFO

# Optional: Rate Limiting
RATE_LIMIT_ENABLED=true
REQUESTS_PER_MINUTE=60

# Optional: Cache Settings
CACHE_TTL_SECONDS=3600
```

### Docker Configuration

The `docker-compose.yml` file includes:

```yaml
version: '3.8'

services:
  backend:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - APOLLO_API_KEY=${APOLLO_API_KEY}
      - MAX_CONCURRENT_AGENTS=${MAX_CONCURRENT_AGENTS:-5}
    volumes:
      - ./server:/app
      - ./server/leads.db:/app/leads.db
      - ./server/chroma_db:/app/chroma_db

  frontend:
    build: ./client
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./client:/app
      - /app/node_modules
```

## First Time Usage

### 1. Test the System

Start with a simple test to ensure everything is working:

```bash
# Test competitor discovery
curl -X POST "http://localhost:8000/api/competitors/discover" \
  -H "Content-Type: application/json" \
  -d '{"seed_company": "HubSpot", "max_competitors": 5}'
```

### 2. Launch Your First Research

```bash
# Launch multi-agent research
curl -X POST "http://localhost:8000/api/research/launch" \
  -H "Content-Type: application/json" \
  -d '{"seed_company": "Salesforce", "max_competitors": 3}'
```

### 3. Monitor Progress

```bash
# Check agent status
curl "http://localhost:8000/api/agents/status"
```

### 4. View Results

```bash
# Get research summary
curl "http://localhost:8000/api/summary"
```

### 5. Chat with Data

```bash
# Ask questions about collected data
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many companies were researched?"}'
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Port 3000/8000 is already in use`

**Solution**: 
```bash
# Check what's using the port
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # macOS/Linux

# Kill the process or change ports in docker-compose.yml
```

#### 2. API Key Issues

**Error**: `System not initialized` or `Invalid API key`

**Solution**:
- Verify your OpenRouter API key is correct
- Check that the `.env` file is in the right location
- Ensure no extra spaces around the API key

#### 3. Docker Permission Issues

**Error**: `Permission denied` when running Docker commands

**Solution**:
```bash
# Windows: Run as Administrator
# macOS/Linux: Add user to docker group
sudo usermod -aG docker $USER
# Then log out and back in
```

#### 4. Dependencies Not Installing

**Error**: `Module not found` or similar import errors

**Solution**:
```bash
# For Python backend
cd server
pip install --upgrade pip
pip install -r requirements.txt

# For Node.js frontend
cd client
rm -rf node_modules package-lock.json
npm install
```

#### 5. Database Issues

**Error**: `Database connection failed`

**Solution**:
```bash
# Delete existing database and let it recreate
rm server/leads.db
rm -rf server/chroma_db

# Restart the application
docker-compose down
docker-compose up --build
```

### Debugging

#### Enable Debug Logging

Add to your `.env` file:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

#### View Logs

```bash
# Docker logs
docker-compose logs backend
docker-compose logs frontend

# Live logs
docker-compose logs -f backend
```

#### Interactive Debugging

```bash
# Access backend container
docker-compose exec backend bash

# Access frontend container
docker-compose exec frontend sh
```

## Performance Optimization

### System Resources

**Minimum Requirements**:
- RAM: 4GB
- CPU: 2 cores
- Storage: 2GB free space

**Recommended**:
- RAM: 8GB+
- CPU: 4 cores+
- Storage: 5GB+ free space

### Configuration Tuning

For better performance, adjust these settings in `.env`:

```env
# Reduce concurrent agents if you have API rate limits
MAX_CONCURRENT_AGENTS=3

# Increase cache duration to reduce API calls
CACHE_TTL_SECONDS=7200

# Enable rate limiting to prevent API abuse
RATE_LIMIT_ENABLED=true
REQUESTS_PER_MINUTE=30
```

## Security Considerations

### 1. API Key Security

- Never commit API keys to version control
- Use environment variables for all secrets
- Rotate API keys regularly
- Consider using a secrets management service in production

### 2. Network Security

- Configure CORS properly for production
- Use HTTPS in production
- Consider API rate limiting
- Implement authentication for production use

### 3. Data Privacy

- Review data retention policies
- Ensure compliance with GDPR/CCPA if applicable
- Consider data encryption for sensitive information

## Production Deployment

### Docker Deployment

1. **Build for Production**

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Run in production mode
docker-compose -f docker-compose.prod.yml up -d
```

2. **Environment Configuration**

Create a production `.env` file:

```env
# Production API keys
OPENROUTER_API_KEY=your_production_openrouter_key
APOLLO_API_KEY=your_production_apollo_key

# Production settings
DEBUG=false
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=10

# Security settings
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_ENABLED=true
REQUESTS_PER_MINUTE=120
```

### Cloud Deployment

The system can be deployed on:

- **AWS**: Using ECS or EC2
- **Google Cloud**: Using Cloud Run or Compute Engine
- **Azure**: Using Container Instances or App Service
- **DigitalOcean**: Using App Platform or Droplets

### Monitoring

Consider adding monitoring for production:

- Application logs
- API response times
- Error rates
- Resource usage
- API quota consumption

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Ensure all prerequisites are met
4. Verify API keys are valid and have appropriate permissions
5. Check the GitHub issues for similar problems

For additional support, create an issue in the GitHub repository with:
- Detailed error messages
- System information (OS, Docker version, etc.)
- Steps to reproduce the issue
- Relevant log outputs
