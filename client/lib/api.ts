import axios from 'axios';
import { log } from 'console';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Types for our lead research system
export interface CompanyProfile {
  name: string;
  domain?: string;
  description?: string;
  industry?: string;
  size?: string;
  location?: string;
  founded?: string;
  funding?: string;
  employees_count?: number;
  linkedin_url?: string;
  website?: string;
  created_at?: string;
}

export interface LeadProfile {
  name: string;
  title?: string;
  company: string;
  email?: string;
  linkedin_url?: string;
  phone?: string;
  location?: string;
  department?: string;
  seniority?: string;
  created_at?: string;
}

export interface AgentStatus {
  agent_id: string;
  company: string;
  status: 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  created_at: string;
}

export interface ResearchSummary {
  total_companies: number;
  total_leads: number;
  companies?: Array<{
    name: string;
    industry?: string;
    size?: string;
    location?: string;
    leads_count: number;
  }>;
  embedding_stats?: {
    total_documents: number;
    collection_name: string;
  };
}

// API Methods for Lead Research System
export const competitorService = {
  discover: (seedCompany: string, maxCompetitors: number = 10) => 
    api.post('/api/competitors/discover', { 
      seed_company: seedCompany, 
      max_competitors: maxCompetitors 
    }),
};

export const researchService = {
  launchResearch: (seedCompany: string, maxCompetitors: number = 10) =>
    api.post('/api/research/launch', {
      seed_company: seedCompany,
      max_competitors: maxCompetitors
    }),
  
  researchCompany: (companyName: string, maxLeads: number = 20) =>
    api.post('/api/company/research', {
      company_name: companyName,
      max_leads: maxLeads
    }),
};

export const agentService = {
  getStatus: () => api.get<{ agents: AgentStatus[]; summary: ResearchSummary }>('/api/agents/status'),
  getAgentStatus: (agentId: string) => api.get<AgentStatus>(`/api/agents/status/${agentId}`),
};

export const companyService = {
  getAll: () => api.get<{ companies: CompanyProfile[]; total: number }>('/api/companies'),
  getCompanyLeads: (companyName: string) => 
    api.get<{ company: CompanyProfile; leads: LeadProfile[]; total_leads: number }>(`/api/companies/${encodeURIComponent(companyName)}/leads`),
};

export const chatService = {
  chat: (question: string, context?: string) =>
    api.post<{ answer: string; sources: string[] }>('/api/chat', { 
      question, 
      context 
    }),
};

export const searchService = {
  search: (query: string) =>
    api.get<{ query: string; results: any[]; total: number }>('/api/search', { 
      params: { q: query } 
    }),
  
  getSummary: () => api.get<ResearchSummary>('/api/summary'),
};

export const healthService = {
  check: () => api.get('/health'),
};
