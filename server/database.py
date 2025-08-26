import sqlite3
import json
from typing import List, Optional
from models import CompanyProfile, LeadProfile, AgentStatus
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "leads.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                domain TEXT,
                description TEXT,
                industry TEXT,
                size TEXT,
                location TEXT,
                founded TEXT,
                funding TEXT,
                employees_count INTEGER,
                linkedin_url TEXT,
                website TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Leads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT,
                company TEXT NOT NULL,
                email TEXT,
                linkedin_url TEXT,
                phone TEXT,
                location TEXT,
                department TEXT,
                seniority TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Agent status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL,
                company TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL,
                content_id TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_company(self, company: CompanyProfile) -> int:
        """Save company profile to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO companies 
            (name, domain, description, industry, size, location, founded, funding, 
             employees_count, linkedin_url, website)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company.name, company.domain, company.description, company.industry,
            company.size, company.location, company.founded, company.funding,
            company.employees_count, company.linkedin_url, company.website
        ))
        
        company_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return company_id
    
    def save_lead(self, lead: LeadProfile) -> int:
        """Save lead profile to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO leads 
            (name, title, company, email, linkedin_url, phone, location, department, seniority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead.name, lead.title, lead.company, lead.email, lead.linkedin_url,
            lead.phone, lead.location, lead.department, lead.seniority
        ))
        
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return lead_id
    
    def get_company(self, name: str) -> Optional[CompanyProfile]:
        """Get company by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM companies WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return CompanyProfile(
                name=row[1], domain=row[2], description=row[3], industry=row[4],
                size=row[5], location=row[6], founded=row[7], funding=row[8],
                employees_count=row[9], linkedin_url=row[10], website=row[11]
            )
        return None
    
    def get_leads_by_company(self, company_name: str) -> List[LeadProfile]:
        """Get all leads for a company"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM leads WHERE company = ?", (company_name,))
        rows = cursor.fetchall()
        conn.close()
        
        leads = []
        for row in rows:
            lead = LeadProfile(
                name=row[1], title=row[2], company=row[3], email=row[4],
                linkedin_url=row[5], phone=row[6], location=row[7],
                department=row[8], seniority=row[9]
            )
            leads.append(lead)
        
        return leads
    
    def update_agent_status(self, agent_id: str, status: str, progress: int, message: str):
        """Update agent status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_status 
            (agent_id, status, company, progress, message, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (agent_id, status, "", progress, message, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_all_companies(self) -> List[CompanyProfile]:
        """Get all companies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM companies")
        rows = cursor.fetchall()
        conn.close()
        
        companies = []
        for row in rows:
            company = CompanyProfile(
                name=row[1], domain=row[2], description=row[3], industry=row[4],
                size=row[5], location=row[6], founded=row[7], funding=row[8],
                employees_count=row[9], linkedin_url=row[10], website=row[11]
            )
            companies.append(company)
        
        return companies
    
    def search_content(self, query: str) -> List[dict]:
        """Search content across companies and leads"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search companies
        cursor.execute("""
            SELECT 'company' as type, name, description, industry, location 
            FROM companies 
            WHERE name LIKE ? OR description LIKE ? OR industry LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "type": row[0],
                "name": row[1],
                "description": row[2],
                "industry": row[3],
                "location": row[4]
            })
        
        # Search leads
        cursor.execute("""
            SELECT 'lead' as type, name, title, company, department
            FROM leads 
            WHERE name LIKE ? OR title LIKE ? OR company LIKE ? OR department LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        
        for row in cursor.fetchall():
            results.append({
                "type": row[0],
                "name": row[1],
                "title": row[2],
                "company": row[3],
                "department": row[4]
            })
        
        conn.close()
        return results
