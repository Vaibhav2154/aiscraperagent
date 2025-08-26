#!/usr/bin/env python3
"""
Demo script for Multi-Agent Lead Research & Competitive Intelligence System
Shows basic functionality and API usage examples
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

class LeadResearchDemo:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def health_check(self) -> bool:
        """Check if the API is running"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ API is running and healthy")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Could not connect to API: {e}")
            return False
    
    async def discover_competitors(self, seed_company: str, max_competitors: int = 5) -> Dict[str, Any]:
        """Discover competitors for a seed company"""
        print(f"\n🔍 Discovering competitors for '{seed_company}'...")
        
        payload = {
            "seed_company": seed_company,
            "max_competitors": max_competitors
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/competitors/discover",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            competitors = data.get("competitors", [])
            print(f"✅ Found {len(competitors)} competitors:")
            for i, competitor in enumerate(competitors, 1):
                print(f"   {i}. {competitor}")
            return data
        else:
            print(f"❌ Failed to discover competitors: {response.status_code}")
            return {}
    
    async def launch_research(self, seed_company: str, max_competitors: int = 3) -> str:
        """Launch multi-agent research"""
        print(f"\n🚀 Launching multi-agent research for '{seed_company}'...")
        
        payload = {
            "seed_company": seed_company,
            "max_competitors": max_competitors
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/research/launch",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id", "")
            print(f"✅ Research session started: {session_id}")
            return session_id
        else:
            print(f"❌ Failed to launch research: {response.status_code}")
            return ""
    
    async def monitor_agents(self, duration: int = 30) -> Dict[str, Any]:
        """Monitor agent progress"""
        print(f"\n👀 Monitoring agents for {duration} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                response = await self.client.get(f"{self.base_url}/api/agents/status")
                if response.status_code == 200:
                    data = response.json()
                    agents = data.get("agents", [])
                    
                    if agents:
                        print(f"\n📊 Agent Status Update:")
                        for agent in agents:
                            status = agent.get("status", "unknown")
                            progress = agent.get("progress", 0)
                            company = agent.get("company", "unknown")
                            message = agent.get("message", "")
                            
                            status_emoji = {
                                "running": "🟡",
                                "completed": "🟢", 
                                "failed": "🔴"
                            }.get(status, "⚪")
                            
                            print(f"   {status_emoji} {company}: {status} ({progress}%) - {message}")
                    else:
                        print("   No active agents found")
                
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"   Error checking agent status: {e}")
                break
        
        # Get final status
        response = await self.client.get(f"{self.base_url}/api/agents/status")
        return response.json() if response.status_code == 200 else {}
    
    async def research_single_company(self, company_name: str) -> Dict[str, Any]:
        """Research a single company"""
        print(f"\n🏢 Researching '{company_name}'...")
        
        payload = {
            "company_name": company_name,
            "max_leads": 10
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/company/research",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            company = data.get("company")
            leads = data.get("leads", [])
            
            if company:
                print(f"✅ Company Profile:")
                print(f"   Name: {company.get('name', 'N/A')}")
                print(f"   Industry: {company.get('industry', 'N/A')}")
                print(f"   Size: {company.get('size', 'N/A')}")
                print(f"   Location: {company.get('location', 'N/A')}")
            
            print(f"\n👥 Found {len(leads)} leads:")
            for i, lead in enumerate(leads[:5], 1):  # Show first 5
                name = lead.get("name", "N/A")
                title = lead.get("title", "N/A")
                department = lead.get("department", "N/A")
                print(f"   {i}. {name} - {title} ({department})")
            
            if len(leads) > 5:
                print(f"   ... and {len(leads) - 5} more")
            
            return data
        else:
            print(f"❌ Failed to research company: {response.status_code}")
            return {}
    
    async def chat_with_data(self, question: str) -> Dict[str, Any]:
        """Chat with collected data"""
        print(f"\n💬 Asking: '{question}'")
        
        payload = {"question": question}
        
        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer provided")
            sources = data.get("sources", [])
            
            print(f"🤖 Answer: {answer}")
            if sources:
                print(f"📚 Sources: {', '.join(sources)}")
            
            return data
        else:
            print(f"❌ Failed to get chat response: {response.status_code}")
            return {}
    
    async def get_summary(self) -> Dict[str, Any]:
        """Get research summary"""
        print(f"\n📈 Getting research summary...")
        
        response = await self.client.get(f"{self.base_url}/api/summary")
        
        if response.status_code == 200:
            data = response.json()
            total_companies = data.get("total_companies", 0)
            total_leads = data.get("total_leads", 0)
            companies = data.get("companies", [])
            
            print(f"✅ Summary:")
            print(f"   Total Companies: {total_companies}")
            print(f"   Total Leads: {total_leads}")
            
            if companies:
                print(f"   Top Companies:")
                for company in companies[:3]:
                    name = company.get("name", "N/A")
                    leads_count = company.get("leads_count", 0)
                    industry = company.get("industry", "N/A")
                    print(f"     • {name} ({industry}) - {leads_count} leads")
            
            return data
        else:
            print(f"❌ Failed to get summary: {response.status_code}")
            return {}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    """Run the demo"""
    demo = LeadResearchDemo()
    
    try:
        print("🎯 Multi-Agent Lead Research System Demo")
        print("=" * 50)
        
        # Health check
        if not await demo.health_check():
            print("\n❌ Cannot connect to API. Make sure the server is running on localhost:8000")
            return
        
        # Demo workflow
        seed_company = "Apollo.io"
        
        # 1. Discover competitors
        competitors_data = await demo.discover_competitors(seed_company, max_competitors=3)
        
        # 2. Research a single company first for quick results
        await demo.research_single_company("HubSpot")
        
        # 3. Launch multi-agent research (this runs in background)
        session_id = await demo.launch_research(seed_company, max_competitors=2)
        
        if session_id:
            # 4. Monitor agents
            await demo.monitor_agents(duration=20)
        
        # 5. Get summary
        await demo.get_summary()
        
        # 6. Chat with data
        questions = [
            "How many companies have we researched?",
            "Tell me about the sales teams",
            "Which companies are in the software industry?"
        ]
        
        for question in questions:
            await demo.chat_with_data(question)
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Check the web interface at http://localhost:3000")
        print("2. Explore the API docs at http://localhost:8000/docs")
        print("3. Try your own company research queries")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
    finally:
        await demo.close()

if __name__ == "__main__":
    asyncio.run(main())
