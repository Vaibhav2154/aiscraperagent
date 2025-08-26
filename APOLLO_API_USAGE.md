# Apollo API Integration Guide

## Overview

This document explains how the AI Scraper Agent system integrates with Apollo.io's API for B2B lead data collection and company enrichment.

## Apollo API Setup

### 1. Getting Your Apollo API Key

1. **Sign up for Apollo**: Visit [apollo.io](https://apollo.io) and create an account
2. **Access API Settings**: Go to Settings → Integrations → API
3. **Generate API Key**: Create a new API key for your application
4. **Copy the Key**: Save the API key securely for environment configuration

### 2. API Key Configuration

Add your Apollo API key to the `.env` file:

```bash
APOLLO_API_KEY=your_apollo_api_key_here
```

**Note**: The system will work with a dummy key for testing, but real data requires a valid Apollo API key.

## Apollo API Endpoints Used

### 1. Company Search Endpoint

**Endpoint**: `https://api.apollo.io/v1/organizations/search`

**Purpose**: Find companies by name and get basic company information

**Parameters Used**:
- `q`: Company name search query
- `per_page`: Number of results per page (default: 10)
- `page`: Page number for pagination

**Sample Request**:
```python
async def fetch_company_data(self, company_name: str) -> CompanyProfile:
    url = "https://api.apollo.io/v1/organizations/search"
    headers = {"X-Api-Key": self.apollo_api_key}
    
    params = {
        "q": company_name,
        "per_page": 1
    }
    
    response = await self.session.get(url, headers=headers, params=params)
    data = response.json()
    
    if data.get("organizations"):
        org = data["organizations"][0]
        return self._parse_company_data(org)
```

### 2. People Search Endpoint

**Endpoint**: `https://api.apollo.io/v1/people/search`

**Purpose**: Find employees/contacts at specific companies

**Parameters Used**:
- `organization_names[]`: Array of company names
- `per_page`: Number of results per page
- `person_titles[]`: Filter by job titles (e.g., "Sales Director", "VP Sales")

**Sample Request**:
```python
async def fetch_leads_data(self, company_name: str, max_leads: int = 20) -> List[LeadProfile]:
    url = "https://api.apollo.io/v1/people/search"
    headers = {"X-Api-Key": self.apollo_api_key}
    
    params = {
        "organization_names[]": [company_name],
        "per_page": min(max_leads, 25),  # Apollo max per page
        "person_titles[]": [
            "Sales Director", "VP Sales", "Sales Manager",
            "Marketing Director", "CEO", "CTO", "Founder"
        ]
    }
    
    response = await self.session.get(url, headers=headers, params=params)
    data = response.json()
    
    leads = []
    for person in data.get("people", []):
        lead = self._parse_lead_data(person)
        if lead:
            leads.append(lead)
    
    return leads
```

## Data Mapping

### Company Data Mapping

Apollo provides rich company data that we map to our `CompanyProfile` model:

```python
def _parse_company_data(self, apollo_org: dict) -> CompanyProfile:
    return CompanyProfile(
        name=apollo_org.get("name", ""),
        domain=apollo_org.get("website_url", "").replace("http://", "").replace("https://", ""),
        description=apollo_org.get("short_description", ""),
        industry=apollo_org.get("industry", ""),
        size=self._format_company_size(apollo_org.get("estimated_num_employees")),
        location=self._format_location(apollo_org),
        founded=str(apollo_org.get("founded_year", "")),
        employees_count=apollo_org.get("estimated_num_employees", 0),
        linkedin_url=apollo_org.get("linkedin_url", ""),
        website=apollo_org.get("website_url", "")
    )

def _format_company_size(self, emp_count: int) -> str:
    if emp_count < 10:
        return "1-10 employees"
    elif emp_count < 50:
        return "11-50 employees"
    elif emp_count < 200:
        return "51-200 employees"
    elif emp_count < 1000:
        return "201-1000 employees"
    elif emp_count < 5000:
        return "1001-5000 employees"
    else:
        return "5000+ employees"
```

### Lead Data Mapping

Apollo people data is mapped to our `LeadProfile` model:

```python
def _parse_lead_data(self, apollo_person: dict) -> LeadProfile:
    return LeadProfile(
        name=f"{apollo_person.get('first_name', '')} {apollo_person.get('last_name', '')}".strip(),
        title=apollo_person.get("title", ""),
        company=apollo_person.get("organization", {}).get("name", ""),
        email=apollo_person.get("email", ""),
        linkedin_url=apollo_person.get("linkedin_url", ""),
        phone=self._format_phone(apollo_person.get("phone_numbers", [])),
        location=self._format_person_location(apollo_person),
        department=self._extract_department(apollo_person.get("title", "")),
        seniority=self._extract_seniority(apollo_person.get("title", ""))
    )

def _extract_department(self, title: str) -> str:
    title_lower = title.lower()
    if any(word in title_lower for word in ["sales", "business development", "revenue"]):
        return "Sales"
    elif any(word in title_lower for word in ["marketing", "growth", "brand"]):
        return "Marketing"
    elif any(word in title_lower for word in ["engineer", "developer", "technical", "cto"]):
        return "Engineering"
    elif any(word in title_lower for word in ["ceo", "founder", "president", "executive"]):
        return "Executive"
    else:
        return "Other"
```

## Rate Limiting and Best Practices

### 1. Apollo API Limits

Apollo has the following rate limits:
- **Free Plan**: 60 requests per hour
- **Starter Plan**: 1,000 requests per month
- **Professional Plan**: 10,000+ requests per month

### 2. Rate Limiting Implementation

```python
class ApolloAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = aiohttp.ClientSession()
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
    
    async def _make_request(self, url: str, params: dict) -> dict:
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        headers = {"X-Api-Key": self.api_key}
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                self.last_request_time = time.time()
                
                if response.status == 429:  # Rate limit exceeded
                    await asyncio.sleep(60)  # Wait 1 minute
                    return await self._make_request(url, params)  # Retry
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            self.logger.error(f"Apollo API error: {e}")
            return {}
```

### 3. Error Handling

```python
async def fetch_company_data(self, company_name: str) -> Optional[CompanyProfile]:
    try:
        data = await self._search_organizations(company_name)
        
        if not data.get("organizations"):
            self.logger.warning(f"No company found for: {company_name}")
            return self._create_fallback_company(company_name)
        
        return self._parse_company_data(data["organizations"][0])
        
    except Exception as e:
        self.logger.error(f"Error fetching company data for {company_name}: {e}")
        return self._create_fallback_company(company_name)

def _create_fallback_company(self, company_name: str) -> CompanyProfile:
    """Create a basic company profile when Apollo data is unavailable"""
    return CompanyProfile(
        name=company_name,
        domain=f"{company_name.lower().replace(' ', '')}.com",
        description=f"Company profile for {company_name}",
        industry="Unknown",
        size="Unknown",
        location="Unknown",
        founded="Unknown",
        employees_count=0,
        linkedin_url="",
        website=""
    )
```

## Mock Data Mode

For development and testing without Apollo API access:

```python
class MockApolloClient:
    """Mock Apollo client for testing without API key"""
    
    async def fetch_company_data(self, company_name: str) -> CompanyProfile:
        return CompanyProfile(
            name=company_name,
            domain=f"{company_name.lower().replace(' ', '')}.com",
            description=f"Mock description for {company_name}",
            industry="Technology",
            size="100-500 employees",
            location="San Francisco, CA",
            founded="2015",
            employees_count=250,
            linkedin_url=f"https://linkedin.com/company/{company_name.lower()}",
            website=f"https://{company_name.lower().replace(' ', '')}.com"
        )
    
    async def fetch_leads_data(self, company_name: str, max_leads: int = 20) -> List[LeadProfile]:
        mock_leads = []
        titles = ["VP Sales", "Sales Director", "Marketing Manager", "CEO", "CTO"]
        
        for i in range(min(max_leads, 10)):
            mock_leads.append(LeadProfile(
                name=f"John Doe {i+1}",
                title=titles[i % len(titles)],
                company=company_name,
                email=f"john.doe{i+1}@{company_name.lower().replace(' ', '')}.com",
                linkedin_url=f"https://linkedin.com/in/johndoe{i+1}",
                phone=f"+1-555-010{i:02d}",
                location="San Francisco, CA",
                department="Sales" if "sales" in titles[i % len(titles)].lower() else "Other",
                seniority="VP" if "VP" in titles[i % len(titles)] else "Manager"
            ))
        
        return mock_leads
```

## Apollo API Response Examples

### Company Search Response

```json
{
  "pagination": {
    "page": 1,
    "per_page": 1,
    "total_entries": 1
  },
  "organizations": [
    {
      "id": "5e66b6381b05b3002a4f79ff",
      "name": "HubSpot",
      "website_url": "https://hubspot.com",
      "linkedin_url": "https://www.linkedin.com/company/hubspot",
      "short_description": "CRM platform for growing companies",
      "industry": "Computer Software",
      "estimated_num_employees": 3000,
      "founded_year": 2006,
      "publicly_traded_symbol": "HUBS",
      "phone": "+1-888-482-7768",
      "headquarters_address": {
        "street_address": "25 First Street",
        "city": "Cambridge",
        "state": "Massachusetts",
        "postal_code": "02141",
        "country": "United States"
      }
    }
  ]
}
```

### People Search Response

```json
{
  "pagination": {
    "page": 1,
    "per_page": 25,
    "total_entries": 15
  },
  "people": [
    {
      "id": "5f7b2b2c4b3a8b0001234567",
      "first_name": "Sarah",
      "last_name": "Johnson",
      "title": "VP of Sales",
      "email": "sarah.johnson@hubspot.com",
      "linkedin_url": "https://www.linkedin.com/in/sarahjohnson",
      "phone_numbers": [
        {
          "raw_number": "+16179995555",
          "sanitized_number": "+16179995555"
        }
      ],
      "organization": {
        "id": "5e66b6381b05b3002a4f79ff",
        "name": "HubSpot"
      },
      "city": "Boston",
      "state": "Massachusetts",
      "country": "United States"
    }
  ]
}
```

## Configuration Options

### Environment Variables for Apollo Integration

```bash
# Apollo API Configuration
APOLLO_API_KEY=your_apollo_api_key_here
APOLLO_RATE_LIMIT_DELAY=1.0
APOLLO_MAX_RETRIES=3
APOLLO_TIMEOUT_SECONDS=30

# Lead Collection Settings
MAX_LEADS_PER_COMPANY=20
APOLLO_SEARCH_TITLES=VP Sales,Sales Director,Marketing Director,CEO,CTO
APOLLO_COMPANY_SEARCH_LIMIT=1

# Fallback Settings
USE_MOCK_DATA_ON_API_FAILURE=true
APOLLO_CACHE_TTL_SECONDS=3600
```

### Code Configuration

```python
# In lead_agent.py initialization
class LeadDataAgent:
    def __init__(self, apollo_api_key: str, openrouter_api_key: str):
        # Apollo client setup
        if apollo_api_key and apollo_api_key != "dummy_key":
            self.apollo_client = ApolloAPIClient(apollo_api_key)
            self.use_mock_data = False
        else:
            self.apollo_client = MockApolloClient()
            self.use_mock_data = True
            
        # Search configuration
        self.target_titles = [
            "VP Sales", "Sales Director", "Sales Manager",
            "Marketing Director", "Marketing Manager",
            "CEO", "CTO", "Founder", "President"
        ]
        
        self.max_requests_per_minute = 60
        self.company_search_limit = 1
```

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   ```
   Error: 401 Unauthorized - Invalid API key
   Solution: Verify your Apollo API key is correct and active
   ```

2. **Rate Limit Exceeded**
   ```
   Error: 429 Too Many Requests
   Solution: The system automatically handles this with backoff, but you may need to upgrade your Apollo plan
   ```

3. **No Results Found**
   ```
   Warning: No company found for: [Company Name]
   Solution: Try variations of the company name or check if the company exists in Apollo's database
   ```

4. **Network Timeout**
   ```
   Error: Request timeout after 30 seconds
   Solution: Check your internet connection and Apollo API status
   ```

### Debug Mode

Enable detailed logging for Apollo API calls:

```python
import logging
logging.getLogger("apollo_client").setLevel(logging.DEBUG)
```

This will show all API requests, responses, and timing information.

## Best Practices

1. **Use Appropriate Batch Sizes**: Don't request more than 25 leads per API call
2. **Implement Proper Error Handling**: Always have fallback data when API fails
3. **Cache Results**: Store successful API responses to avoid duplicate calls
4. **Monitor Usage**: Track your API usage to stay within plan limits
5. **Respect Rate Limits**: Use built-in delays and don't make concurrent requests
6. **Validate Data**: Always validate Apollo responses before processing
7. **Use Specific Search Terms**: More specific company names yield better results

This Apollo integration provides robust B2B data collection capabilities while handling edge cases and API limitations gracefully.
