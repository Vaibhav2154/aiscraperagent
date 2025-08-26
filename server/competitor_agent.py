import httpx
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import json
import re

class CompetitorDiscoveryAgent:
    def __init__(self, openrouter_api_key: str):
        self.openrouter_api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
    async def discover_competitors(self, seed_company: str, max_competitors: int = 10) -> List[str]:
        """Discover competitors using LLM and web search"""
        competitors = []
        
        # Use LLM to generate potential competitors
        llm_competitors = await self._get_competitors_from_llm(seed_company, max_competitors)
        competitors.extend(llm_competitors)
        
        # Use web search to find more competitors
        search_competitors = await self._search_competitors_web(seed_company)
        competitors.extend(search_competitors)
        
        # Remove duplicates and limit results
        unique_competitors = list(set(competitors))
        return unique_competitors[:max_competitors]
    
    async def _get_competitors_from_llm(self, seed_company: str, max_competitors: int) -> List[str]:
        """Use LLM to identify competitors"""
        prompt = f"""
        Given the company "{seed_company}", please provide a list of {max_competitors} direct competitors.
        
        Instructions:
        - Focus on companies in the same industry and market segment
        - Include both established players and emerging competitors
        - Provide only company names, one per line
        - Do not include the seed company itself
        
        Example format:
        Company Name 1
        Company Name 2
        Company Name 3
        
        Competitors of {seed_company}:
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
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
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Extract company names from response
                    lines = content.strip().split('\n')
                    competitors = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('-') and not line.startswith('*'):
                            # Clean up the line to extract just the company name
                            company_name = re.sub(r'^\d+\.\s*', '', line)  # Remove numbering
                            company_name = company_name.strip()
                            if company_name and company_name.lower() != seed_company.lower():
                                competitors.append(company_name)
                    
                    return competitors[:max_competitors]
                    
        except Exception as e:
            print(f"Error getting competitors from LLM: {e}")
            
        return []
    
    async def _search_competitors_web(self, seed_company: str) -> List[str]:
        """Search for competitors using web scraping"""
        competitors = []
        
        try:
            search_queries = [
                f"{seed_company} competitors",
                f"{seed_company} alternatives",
                f"companies like {seed_company}"
            ]
            
            async with httpx.AsyncClient() as client:
                for query in search_queries:
                    try:
                        # Use a simple web search (you might want to use Google Custom Search API)
                        # For now, we'll use a mock implementation
                        mock_competitors = await self._mock_web_search(seed_company)
                        competitors.extend(mock_competitors)
                    except Exception as e:
                        print(f"Error in web search for {query}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error in web search: {e}")
            
        return list(set(competitors))
    
    async def _mock_web_search(self, seed_company: str) -> List[str]:
        """Mock web search results with realistic competitors based on industry patterns"""
        # Comprehensive competitor database organized by company and industry
        mock_results = {
            # Sales & Marketing Tools
            "apollo": ["Outreach", "SalesLoft", "HubSpot", "Pipedrive", "Salesforce", "ZoomInfo", "LinkedIn Sales Navigator"],
            "lemlist": ["Outreach", "Reply.io", "Woodpecker", "Mailshake", "QuickMail", "SalesLoft", "Klenty"],
            "outreach": ["Apollo", "SalesLoft", "Lemlist", "HubSpot", "Pipedrive", "Reply.io"],
            "salesloft": ["Outreach", "Apollo", "HubSpot", "Pipedrive", "Lemlist", "Groove"],
            "mailshake": ["Lemlist", "Outreach", "Reply.io", "Woodpecker", "QuickMail", "Klenty"],
            
            # CRM Platforms
            "salesforce": ["HubSpot", "Pipedrive", "Microsoft Dynamics 365", "Zoho CRM", "Oracle Sales Cloud", "SugarCRM"],
            "hubspot": ["Salesforce", "Pipedrive", "Zoho CRM", "ActiveCampaign", "Marketo", "Pardot"],
            "pipedrive": ["HubSpot", "Salesforce", "Zoho CRM", "Freshsales", "Close", "Copper"],
            "zoho": ["HubSpot", "Salesforce", "Pipedrive", "Freshworks", "SugarCRM"],
            
            # Marketing Automation
            "marketo": ["HubSpot", "Pardot", "ActiveCampaign", "Mailchimp", "Constant Contact"],
            "pardot": ["Marketo", "HubSpot", "ActiveCampaign", "Eloqua", "Act-On"],
            "mailchimp": ["Constant Contact", "ActiveCampaign", "ConvertKit", "AWeber", "GetResponse"],
            
            # Data & Analytics
            "zoominfo": ["Apollo", "LinkedIn Sales Navigator", "Clearbit", "DiscoverOrg", "InsideView"],
            "clearbit": ["ZoomInfo", "Apollo", "FullContact", "Pipl", "DataSift"],
            
            # Communication Tools
            "slack": ["Microsoft Teams", "Discord", "Zoom", "Google Workspace", "Cisco Webex"],
            "zoom": ["Microsoft Teams", "Google Meet", "Slack", "GoToMeeting", "Cisco Webex"],
            "teams": ["Slack", "Zoom", "Google Workspace", "Discord", "Cisco Webex"],
            
            # Project Management
            "asana": ["Monday.com", "Trello", "Notion", "ClickUp", "Jira"],
            "monday": ["Asana", "Trello", "Notion", "ClickUp", "Smartsheet"],
            "notion": ["Asana", "Monday.com", "Airtable", "ClickUp", "Coda"],
            
            # E-commerce
            "shopify": ["WooCommerce", "BigCommerce", "Magento", "Squarespace", "Wix"],
            "woocommerce": ["Shopify", "BigCommerce", "Magento", "PrestaShop"],
            
            # Analytics
            "mixpanel": ["Amplitude", "Google Analytics", "Adobe Analytics", "Heap", "Segment"],
            "amplitude": ["Mixpanel", "Google Analytics", "Adobe Analytics", "Heap"],
            
            # Development Tools
            "github": ["GitLab", "Bitbucket", "Azure DevOps", "SourceForge"],
            "gitlab": ["GitHub", "Bitbucket", "Azure DevOps", "Gitea"],
            
            # Cloud Services
            "aws": ["Microsoft Azure", "Google Cloud Platform", "IBM Cloud", "DigitalOcean"],
            "azure": ["AWS", "Google Cloud Platform", "IBM Cloud", "Oracle Cloud"],
            "gcp": ["AWS", "Microsoft Azure", "IBM Cloud", "Alibaba Cloud"]
        }
        
        seed_lower = seed_company.lower().strip()
        
        # Direct match
        if seed_lower in mock_results:
            return mock_results[seed_lower]
        
        # Partial match
        for key, competitors in mock_results.items():
            if key in seed_lower or seed_lower in key:
                return competitors
        
        # If no match found, try to infer from industry keywords
        industry_keywords = {
            "crm": ["HubSpot", "Salesforce", "Pipedrive", "Zoho CRM", "Freshsales"],
            "sales": ["Outreach", "SalesLoft", "Apollo", "HubSpot", "Pipedrive"],
            "marketing": ["HubSpot", "Marketo", "Pardot", "ActiveCampaign", "Mailchimp"],
            "email": ["Lemlist", "Outreach", "Mailchimp", "ActiveCampaign", "ConvertKit"],
            "analytics": ["Google Analytics", "Mixpanel", "Amplitude", "Adobe Analytics"],
            "cloud": ["AWS", "Microsoft Azure", "Google Cloud Platform", "IBM Cloud"],
            "communication": ["Slack", "Microsoft Teams", "Zoom", "Discord"],
            "ecommerce": ["Shopify", "WooCommerce", "BigCommerce", "Magento"]
        }
        
        for keyword, competitors in industry_keywords.items():
            if keyword in seed_lower:
                return competitors
        
        # If still no match, return empty list instead of generic competitors
        return []
