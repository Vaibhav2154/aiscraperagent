from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import asyncio

from models import (
    CompetitorSearchRequest, CompetitorSearchResponse,
    LeadSearchRequest, LeadSearchResponse,
    ChatRequest, ChatResponse,
    CompanyProfile, LeadProfile
)
from orchestrator import MultiAgentOrchestrator
from database import DatabaseManager

load_dotenv()

# Global orchestrator instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    apollo_api_key = os.getenv("APOLLO_API_KEY", "dummy_key")  # Allow dummy key for testing
    max_concurrent_agents = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))
    
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is required")
    
    orchestrator = MultiAgentOrchestrator(
        openrouter_api_key=openrouter_api_key,
        apollo_api_key=apollo_api_key,
        max_concurrent_agents=max_concurrent_agents
    )
    
    print("🚀 Multi-Agent Lead Research System started successfully!")
    yield
    
    # Shutdown
    print("👋 Shutting down...")

app = FastAPI(
    title="Multi-Agent Lead Research & Competitive Intelligence System",
    description="Automatically discover competitors, gather lead data, and enable chat interaction with collected intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Lead Research & Competitive Intelligence System",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/competitors/discover", response_model=CompetitorSearchResponse)
async def discover_competitors(request: CompetitorSearchRequest, background_tasks: BackgroundTasks):
    """Discover competitors for a seed company"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        competitors = await orchestrator.competitor_agent.discover_competitors(
            request.seed_company, 
            request.max_competitors
        )
        
        return CompetitorSearchResponse(
            competitors=competitors,
            total_found=len(competitors)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error discovering competitors: {str(e)}")

@app.post("/api/research/launch")
async def launch_research(request: CompetitorSearchRequest, background_tasks: BackgroundTasks):
    """Launch multi-agent research for competitors"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        # Launch research in background
        session_id = await orchestrator.launch_competitor_research(
            request.seed_company,
            request.max_competitors
        )
        
        return {
            "session_id": session_id,
            "message": f"Research launched for {request.seed_company}",
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error launching research: {str(e)}")

@app.post("/api/company/research", response_model=LeadSearchResponse)
async def research_company(request: LeadSearchRequest):
    """Research a single company synchronously"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        result = await orchestrator.research_single_company_sync(request.company_name)
        
        company = None
        if result["company"]:
            company = CompanyProfile(**result["company"])
        
        leads = [LeadProfile(**lead_data) for lead_data in result["leads"]]
        
        return LeadSearchResponse(
            leads=leads,
            company=company,
            total_found=len(leads)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error researching company: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_data(request: ChatRequest):
    """Chat with collected research data"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        result = await orchestrator.chat_with_data(request.question)
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@app.get("/api/agents/status")
async def get_agent_statuses():
    """Get status of all running agents"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        return {
            "agents": orchestrator.get_all_agent_statuses(),
            "summary": orchestrator.get_research_summary()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")

@app.get("/api/agents/status/{agent_id}")
async def get_agent_status(agent_id: str):
    """Get status of a specific agent"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        status = orchestrator.get_agent_status(agent_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")

@app.get("/api/companies")
async def get_companies():
    """Get all researched companies"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        companies = orchestrator.db.get_all_companies()
        
        return {
            "companies": [company.dict() for company in companies],
            "total": len(companies)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting companies: {str(e)}")

@app.get("/api/companies/{company_name}/leads")
async def get_company_leads(company_name: str):
    """Get all leads for a specific company"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        company = orchestrator.db.get_company(company_name)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        leads = orchestrator.db.get_leads_by_company(company_name)
        
        return {
            "company": company.dict(),
            "leads": [lead.dict() for lead in leads],
            "total_leads": len(leads)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting company leads: {str(e)}")

@app.get("/api/search")
async def search_content(q: str):
    """Search across all collected data"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        results = orchestrator.db.search_content(q)
        
        return {
            "query": q,
            "results": results,
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching content: {str(e)}")

@app.get("/api/summary")
async def get_research_summary():
    """Get summary of all research data"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        return orchestrator.get_research_summary()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "system": "Multi-Agent Lead Research System"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
