import asyncio
import uuid
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
import logging

from competitor_agent import CompetitorDiscoveryAgent
from lead_agent import LeadDataAgent
from embedding_agent import EmbeddingAgent
from database import DatabaseManager
from models import AgentStatus, CompanyProfile, LeadProfile

@dataclass
class AgentTask:
    agent_id: str
    company_name: str
    task_type: str  # "research", "embed"
    status: str = "pending"
    progress: int = 0
    message: str = ""
    created_at: datetime = datetime.now()

class MultiAgentOrchestrator:
    def __init__(self, 
                 openrouter_api_key: str, 
                 apollo_api_key: str,
                 max_concurrent_agents: int = 5):
        self.openrouter_api_key = openrouter_api_key
        self.apollo_api_key = apollo_api_key
        self.max_concurrent_agents = max_concurrent_agents
        
        # Initialize agents
        self.competitor_agent = CompetitorDiscoveryAgent(openrouter_api_key)
        self.lead_agent = LeadDataAgent(apollo_api_key, openrouter_api_key)
        self.embedding_agent = EmbeddingAgent(openrouter_api_key)
        self.db = DatabaseManager()
        
        # Task management
        self.active_tasks: Dict[str, AgentTask] = {}
        self.task_queue: List[AgentTask] = []
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_agents)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def launch_competitor_research(self, seed_company: str, max_competitors: int = 10) -> str:
        """Launch multi-agent research for competitors"""
        session_id = str(uuid.uuid4())
        self.logger.info(f"Starting competitor research session {session_id} for {seed_company}")
        
        try:
            # Step 1: Discover competitors
            self.logger.info(f"Discovering competitors for {seed_company}")
            competitors = await self.competitor_agent.discover_competitors(seed_company, max_competitors)
            
            if not competitors:
                self.logger.warning(f"No competitors found for {seed_company}")
                return session_id
            
            self.logger.info(f"Found {len(competitors)} competitors: {competitors}")
            
            # Step 2: Create research tasks for each competitor
            research_tasks = []
            for competitor in competitors:
                task = AgentTask(
                    agent_id=f"{session_id}_{competitor}",
                    company_name=competitor,
                    task_type="research"
                )
                research_tasks.append(task)
                self.active_tasks[task.agent_id] = task
            
            # Step 3: Execute research tasks in parallel
            await self._execute_parallel_research(research_tasks)
            
            self.logger.info(f"Completed competitor research session {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error in competitor research session {session_id}: {e}")
            return session_id
    
    async def _execute_parallel_research(self, tasks: List[AgentTask]):
        """Execute research tasks in parallel with concurrency limit"""
        semaphore = asyncio.Semaphore(self.max_concurrent_agents)
        
        async def research_single_company(task: AgentTask):
            async with semaphore:
                await self._research_company(task)
        
        # Execute all tasks concurrently
        await asyncio.gather(*[research_single_company(task) for task in tasks])
    
    async def _research_company(self, task: AgentTask):
        """Research a single company and its leads"""
        try:
            self._update_task_status(task.agent_id, "running", 10, f"Starting research for {task.company_name}")
            
            # Step 1: Fetch company data
            self.logger.info(f"Fetching company data for {task.company_name}")
            company = await self.lead_agent.fetch_company_data(task.company_name)
            
            if company:
                company_id = self.db.save_company(company)
                self._update_task_status(task.agent_id, "running", 30, f"Company data saved")
            else:
                self._update_task_status(task.agent_id, "failed", 30, f"Failed to fetch company data")
                return
            
            # Step 2: Fetch leads data
            self.logger.info(f"Fetching leads for {task.company_name}")
            leads = await self.lead_agent.fetch_leads_data(task.company_name, max_leads=20)
            
            if leads:
                for lead in leads:
                    self.db.save_lead(lead)
                self._update_task_status(task.agent_id, "running", 60, f"Saved {len(leads)} leads")
            else:
                self._update_task_status(task.agent_id, "running", 60, f"No leads found")
            
            # Step 3: Embed data
            self.logger.info(f"Embedding data for {task.company_name}")
            
            # Embed company
            if company:
                self.embedding_agent.embed_company(company)
            
            # Embed leads
            if leads:
                self.embedding_agent.embed_multiple_leads(leads)
            
            self._update_task_status(task.agent_id, "completed", 100, f"Research completed successfully")
            self.logger.info(f"Completed research for {task.company_name}")
            
        except Exception as e:
            self.logger.error(f"Error researching {task.company_name}: {e}")
            self._update_task_status(task.agent_id, "failed", 0, f"Error: {str(e)}")
    
    def _update_task_status(self, agent_id: str, status: str, progress: int, message: str):
        """Update task status"""
        if agent_id in self.active_tasks:
            task = self.active_tasks[agent_id]
            task.status = status
            task.progress = progress
            task.message = message
            
            # Also update in database
            self.db.update_agent_status(agent_id, status, progress, message)
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        if agent_id in self.active_tasks:
            task = self.active_tasks[agent_id]
            return {
                "agent_id": task.agent_id,
                "company": task.company_name,
                "status": task.status,
                "progress": task.progress,
                "message": task.message,
                "created_at": task.created_at.isoformat()
            }
        return {}
    
    def get_all_agent_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        return [self.get_agent_status(agent_id) for agent_id in self.active_tasks.keys()]
    
    async def research_single_company_sync(self, company_name: str) -> Dict[str, Any]:
        """Research a single company synchronously"""
        agent_id = f"sync_{company_name}_{uuid.uuid4()}"
        task = AgentTask(agent_id=agent_id, company_name=company_name, task_type="research")
        self.active_tasks[agent_id] = task
        
        await self._research_company(task)
        
        # Return results
        company = self.db.get_company(company_name)
        leads = self.db.get_leads_by_company(company_name)
        
        return {
            "company": company.dict() if company else None,
            "leads": [lead.dict() for lead in leads],
            "total_leads": len(leads),
            "status": self.get_agent_status(agent_id)
        }
    
    async def chat_with_data(self, question: str) -> Dict[str, Any]:
        """Chat with all collected data"""
        return await self.embedding_agent.chat_with_data(question)
    
    def get_research_summary(self) -> Dict[str, Any]:
        """Get summary of all research data"""
        companies = self.db.get_all_companies()
        total_leads = 0
        
        company_summaries = []
        for company in companies:
            leads = self.db.get_leads_by_company(company.name)
            total_leads += len(leads)
            
            company_summaries.append({
                "name": company.name,
                "industry": company.industry,
                "size": company.size,
                "location": company.location,
                "leads_count": len(leads)
            })
        
        return {
            "total_companies": len(companies),
            "total_leads": total_leads,
            "companies": company_summaries,
            "embedding_stats": self.embedding_agent.get_collection_stats()
        }
