import httpx
import asyncio
import json
from typing import List, Dict, Any, Optional
from models import CompanyProfile, LeadProfile
import re

class LeadDataAgent:
    def __init__(self, apollo_api_key: str, openrouter_api_key: str):
        self.apollo_api_key = apollo_api_key
        self.openrouter_api_key = openrouter_api_key
        self.apollo_base_url = "https://api.apollo.io/v1"
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
    
    async def fetch_company_data(self, company_name: str) -> Optional[CompanyProfile]:
        """Fetch company data from Apollo API and enrich with LLM"""
        try:
            # Try Apollo API first
            apollo_data = await self._fetch_from_apollo_companies(company_name)
            
            if apollo_data:
                return self._convert_apollo_to_company_profile(apollo_data, company_name)
            else:
                # Fallback to LLM-generated data
                return await self._generate_company_profile_llm(company_name)
                
        except Exception as e:
            print(f"Error fetching company data for {company_name}: {e}")
            return await self._generate_company_profile_llm(company_name)
    
    async def fetch_leads_data(self, company_name: str, max_leads: int = 20) -> List[LeadProfile]:
        """Fetch leads data from Apollo API"""
        try:
            apollo_leads = await self._fetch_from_apollo_people(company_name, max_leads)
            if apollo_leads:
                return [self._convert_apollo_to_lead_profile(lead, company_name) for lead in apollo_leads]
            else:
                # Fallback to mock data
                return await self._generate_mock_leads(company_name, max_leads)
                
        except Exception as e:
            print(f"Error fetching leads for {company_name}: {e}")
            return await self._generate_mock_leads(company_name, max_leads)
    
    async def _fetch_from_apollo_companies(self, company_name: str) -> Optional[Dict]:
        """Fetch company data from Apollo API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.apollo_base_url}/mixed_companies/search",
                    headers={
                        "Cache-Control": "no-cache",
                        "X-Api-Key": self.apollo_api_key
                    },
                    params={
                        "q_organization_name": company_name,
                        "page": 1,
                        "per_page": 1
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("organizations") and len(data["organizations"]) > 0:
                        return data["organizations"][0]
                        
        except Exception as e:
            print(f"Apollo API error for company {company_name}: {e}")
            
        return None
    
    async def _fetch_from_apollo_people(self, company_name: str, max_leads: int) -> List[Dict]:
        """Fetch people data from Apollo API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.apollo_base_url}/mixed_people/search",
                    headers={
                        "Cache-Control": "no-cache",
                        "X-Api-Key": self.apollo_api_key
                    },
                    params={
                        "q_organization_name": company_name,
                        "page": 1,
                        "per_page": min(max_leads, 25)  # Apollo limits per page
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("people", [])
                    
        except Exception as e:
            print(f"Apollo API error for people at {company_name}: {e}")
            
        return []
    
    def _convert_apollo_to_company_profile(self, apollo_data: Dict, company_name: str) -> CompanyProfile:
        """Convert Apollo API response to CompanyProfile"""
        return CompanyProfile(
            name=apollo_data.get("name", company_name),
            domain=apollo_data.get("website_url", ""),
            description=apollo_data.get("short_description", ""),
            industry=apollo_data.get("industry", ""),
            size=f"{apollo_data.get('estimated_num_employees', 0)} employees",
            location=f"{apollo_data.get('city', '')}, {apollo_data.get('state', '')}, {apollo_data.get('country', '')}".strip(", "),
            founded=str(apollo_data.get("founded_year", "")),
            funding=apollo_data.get("total_funding", ""),
            employees_count=apollo_data.get("estimated_num_employees", 0),
            linkedin_url=apollo_data.get("linkedin_url", ""),
            website=apollo_data.get("website_url", "")
        )
    
    def _convert_apollo_to_lead_profile(self, apollo_person: Dict, company_name: str) -> LeadProfile:
        """Convert Apollo person data to LeadProfile"""
        return LeadProfile(
            name=f"{apollo_person.get('first_name', '')} {apollo_person.get('last_name', '')}".strip(),
            title=apollo_person.get("title", ""),
            company=company_name,
            email=apollo_person.get("email", ""),
            linkedin_url=apollo_person.get("linkedin_url", ""),
            phone=apollo_person.get("phone", ""),
            location=f"{apollo_person.get('city', '')}, {apollo_person.get('state', '')}, {apollo_person.get('country', '')}".strip(", "),
            department=apollo_person.get("departments", [""])[0] if apollo_person.get("departments") else "",
            seniority=apollo_person.get("seniority", "")
        )
    
    async def _generate_company_profile_llm(self, company_name: str) -> CompanyProfile:
        """Generate company profile using LLM"""
        prompt = f"""
        Please provide detailed information about the company "{company_name}" in JSON format.
        
        Include the following fields:
        - name: Company name
        - domain: Website domain
        - description: Brief company description
        - industry: Primary industry
        - size: Company size (e.g., "50-100 employees")
        - location: Headquarters location
        - founded: Founding year
        - funding: Funding information if available
        - employees_count: Estimated number of employees (integer)
        - linkedin_url: LinkedIn company page URL
        - website: Company website URL
        
        Return only valid JSON:
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3-haiku",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.3
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        company_data = json.loads(json_match.group())
                        return CompanyProfile(**company_data)
                        
        except Exception as e:
            print(f"Error generating company profile with LLM: {e}")
        
        # Fallback to basic profile
        return CompanyProfile(
            name=company_name,
            description=f"AI-generated profile for {company_name}",
            industry="Technology"
        )
    
    async def _generate_mock_leads(self, company_name: str, max_leads: int) -> List[LeadProfile]:
        """Generate realistic mock leads for testing"""
        # Realistic first and last names
        first_names = [
            "Sarah", "Michael", "Jennifer", "David", "Emily", "James", "Jessica", "Robert",
            "Ashley", "Christopher", "Amanda", "Daniel", "Stephanie", "Matthew", "Nicole",
            "Andrew", "Samantha", "Joshua", "Elizabeth", "Anthony", "Lauren", "Kevin",
            "Rachel", "Brian", "Megan", "Mark", "Kimberly", "Steven", "Amy", "Thomas"
        ]
        
        last_names = [
            "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
            "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
            "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
        ]
        
        # More specific titles based on departments
        title_by_department = {
            "Sales": [
                "VP of Sales", "Sales Director", "Senior Account Executive", "Account Executive",
                "Sales Development Representative", "Business Development Manager", "Regional Sales Manager",
                "Enterprise Account Manager", "Inside Sales Manager", "Sales Operations Manager"
            ],
            "Marketing": [
                "VP of Marketing", "Marketing Director", "Digital Marketing Manager", "Content Marketing Manager",
                "Growth Marketing Manager", "Product Marketing Manager", "Marketing Operations Manager",
                "Brand Manager", "Demand Generation Manager", "SEO Manager"
            ],
            "Product": [
                "VP of Product", "Product Director", "Senior Product Manager", "Product Manager",
                "Associate Product Manager", "Product Owner", "UX/UI Designer", "Product Analyst",
                "Technical Product Manager", "Product Operations Manager"
            ],
            "Engineering": [
                "CTO", "VP of Engineering", "Engineering Director", "Senior Software Engineer",
                "Software Engineer", "DevOps Engineer", "Data Engineer", "Frontend Engineer",
                "Backend Engineer", "Full Stack Engineer"
            ],
            "Business Development": [
                "VP of Business Development", "BD Director", "Business Development Manager",
                "Partnership Manager", "Strategic Partnerships", "Channel Manager",
                "Alliance Manager", "Corporate Development Manager"
            ],
            "Operations": [
                "COO", "VP of Operations", "Operations Director", "Operations Manager",
                "Business Operations Manager", "Revenue Operations Manager", "Customer Success Manager",
                "Finance Manager", "HR Manager", "Legal Counsel"
            ]
        }
        
        departments = list(title_by_department.keys())
        
        # Locations for variety
        locations = [
            "San Francisco, CA, USA", "New York, NY, USA", "Seattle, WA, USA", "Austin, TX, USA",
            "Boston, MA, USA", "Los Angeles, CA, USA", "Chicago, IL, USA", "Denver, CO, USA",
            "Atlanta, GA, USA", "London, UK", "Toronto, Canada", "Berlin, Germany"
        ]
        
        leads = []
        import random
        
        for i in range(min(max_leads, 15)):  # Generate up to 15 realistic leads
            # Select department and corresponding title
            department = departments[i % len(departments)]
            titles = title_by_department[department]
            title = titles[i % len(titles)]
            
            # Generate realistic name
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f"{first_name} {last_name}"
            
            # Generate email based on name and company
            company_domain = company_name.lower().replace(' ', '').replace('.', '')
            email_first = first_name.lower()
            email_last = last_name.lower()
            email = f"{email_first}.{email_last}@{company_domain}.com"
            
            # LinkedIn URL
            linkedin_url = f"https://linkedin.com/in/{email_first}-{email_last}"
            
            # Determine seniority based on title
            if any(word in title.lower() for word in ["vp", "ceo", "cto", "coo", "director"]):
                seniority = "Executive"
            elif any(word in title.lower() for word in ["manager", "lead", "head"]):
                seniority = "Manager"
            elif "senior" in title.lower():
                seniority = "Senior"
            else:
                seniority = "Individual Contributor"
            
            lead = LeadProfile(
                name=full_name,
                title=title,
                company=company_name,
                email=email,
                linkedin_url=linkedin_url,
                phone=f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                location=random.choice(locations),
                department=department,
                seniority=seniority
            )
            leads.append(lead)
        
        return leads
