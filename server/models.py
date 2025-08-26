from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CompanyProfile(BaseModel):
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    founded: Optional[str] = None
    funding: Optional[str] = None
    employees_count: Optional[int] = None
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime = datetime.now()

class LeadProfile(BaseModel):
    name: str
    title: Optional[str] = None
    company: str
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    seniority: Optional[str] = None
    created_at: datetime = datetime.now()

class CompetitorSearchRequest(BaseModel):
    seed_company: str
    max_competitors: int = 10

class CompetitorSearchResponse(BaseModel):
    competitors: List[str]
    total_found: int

class LeadSearchRequest(BaseModel):
    company_name: str
    max_leads: int = 20

class LeadSearchResponse(BaseModel):
    leads: List[LeadProfile]
    company: CompanyProfile
    total_found: int

class ChatRequest(BaseModel):
    question: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class AgentStatus(BaseModel):
    agent_id: str
    status: str  # "running", "completed", "failed"
    company: str
    progress: int  # 0-100
    message: str
    created_at: datetime = datetime.now()
