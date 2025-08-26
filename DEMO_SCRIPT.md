# Demo Script for AI Scraper Agent

This demo script demonstrates the key features of the Multi-Agent Lead Research & Competitive Intelligence System.

## Demo Overview

This demo will showcase:
1. Competitor discovery for a seed company
2. Multi-agent research coordination
3. Real-time agent status monitoring
4. Lead data collection and enrichment
5. Chat interface with collected intelligence
6. Research summary and analytics

## Prerequisites

Ensure the system is running:
```bash
# Start the system
docker-compose up --build

# Verify it's running
curl http://localhost:8000/health
```

## Demo Script

### Part 1: Competitor Discovery

**Scenario**: Find competitors for "HubSpot"

```bash
echo "=== DEMO: Competitor Discovery ==="
echo "Finding competitors for HubSpot..."

curl -X POST "http://localhost:8000/api/competitors/discover" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_company": "HubSpot",
    "max_competitors": 8
  }' | jq '.'
```

**Expected Output**:
```json
{
  "competitors": [
    "Salesforce",
    "Pipedrive",
    "Zoho CRM",
    "Freshworks",
    "ActiveCampaign",
    "Pardot",
    "Marketo",
    "Mailchimp"
  ],
  "total_found": 8
}
```

### Part 2: Launch Multi-Agent Research

**Scenario**: Research the top 5 competitors found

```bash
echo "=== DEMO: Multi-Agent Research Launch ==="
echo "Launching research for HubSpot competitors..."

curl -X POST "http://localhost:8000/api/research/launch" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_company": "HubSpot",
    "max_competitors": 5
  }' | jq '.'
```

**Expected Output**:
```json
{
  "session_id": "abc123-def456-ghi789",
  "message": "Research launched for HubSpot",
  "status": "started"
}
```

### Part 3: Monitor Agent Progress

**Scenario**: Watch agents work in real-time

```bash
echo "=== DEMO: Agent Status Monitoring ==="
echo "Monitoring agent progress..."

# Check status multiple times to show progress
for i in {1..5}; do
  echo "--- Status Check $i ---"
  curl -s "http://localhost:8000/api/agents/status" | jq '.'
  echo "Waiting 10 seconds..."
  sleep 10
done
```

**Expected Output** (evolving over time):
```json
[
  {
    "agent_id": "abc123_Salesforce",
    "company": "Salesforce",
    "status": "running",
    "progress": 45,
    "message": "Collecting leads data",
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "agent_id": "abc123_Pipedrive",
    "company": "Pipedrive",
    "status": "completed",
    "progress": 100,
    "message": "Research completed successfully",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Part 4: Single Company Deep Dive

**Scenario**: Research a specific company in detail

```bash
echo "=== DEMO: Single Company Research ==="
echo "Deep dive research on Salesforce..."

curl -X POST "http://localhost:8000/api/company/research" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Salesforce",
    "max_leads": 15
  }' | jq '.'
```

**Expected Output**:
```json
{
  "company": {
    "name": "Salesforce",
    "domain": "salesforce.com",
    "description": "Customer relationship management software",
    "industry": "Software",
    "size": "5000+ employees",
    "location": "San Francisco, CA",
    "founded": "1999",
    "employees_count": 73000,
    "linkedin_url": "https://linkedin.com/company/salesforce",
    "website": "https://salesforce.com"
  },
  "leads": [
    {
      "name": "Marc Benioff",
      "title": "CEO",
      "company": "Salesforce",
      "email": "marc@salesforce.com",
      "linkedin_url": "https://linkedin.com/in/marcbenioff",
      "department": "Executive",
      "seniority": "C-Level"
    }
  ],
  "total_found": 15
}
```

### Part 5: Chat with Intelligence Data

**Scenario**: Ask analytical questions about collected data

```bash
echo "=== DEMO: Chat Interface ==="
echo "Asking analytical questions..."

# Question 1: Overview
echo "Q1: How many companies have we researched?"
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many companies have we researched in total?"
  }' | jq '.answer'

echo ""

# Question 2: Industry analysis
echo "Q2: What industries are represented?"
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What industries are these companies in and which is most common?"
  }' | jq '.answer'

echo ""

# Question 3: Team analysis
echo "Q3: Sales team structure analysis"
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many VP of Sales or Sales Directors work at these companies?"
  }' | jq '.answer'

echo ""

# Question 4: Location analysis
echo "Q4: Geographic distribution"
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which cities or regions have the most companies?"
  }' | jq '.answer'
```

**Expected Outputs**:

*Q1 Response*:
```
"Based on the collected data, we have researched 6 companies total: HubSpot (the seed company), plus 5 competitors: Salesforce, Pipedrive, Zoho CRM, Freshworks, and ActiveCampaign."
```

*Q2 Response*:
```
"The companies represent primarily the Software/SaaS industry, specifically CRM and Marketing Automation platforms. All 6 companies are in the B2B software space focused on sales and marketing tools."
```

### Part 6: Research Summary

**Scenario**: Get comprehensive overview of all research

```bash
echo "=== DEMO: Research Summary ==="
echo "Getting comprehensive research summary..."

curl -s "http://localhost:8000/api/summary" | jq '.'
```

**Expected Output**:
```json
{
  "total_companies": 6,
  "total_leads": 89,
  "companies": [
    {
      "name": "HubSpot",
      "industry": "Software",
      "size": "1000-5000 employees",
      "location": "Cambridge, MA",
      "leads_count": 18
    },
    {
      "name": "Salesforce",
      "industry": "Software",
      "size": "5000+ employees",
      "location": "San Francisco, CA",
      "leads_count": 15
    }
  ],
  "embedding_stats": {
    "total_documents": 95,
    "companies_embedded": 6,
    "leads_embedded": 89
  }
}
```

### Part 7: Advanced Search

**Scenario**: Search across all collected data

```bash
echo "=== DEMO: Advanced Search ==="
echo "Searching for sales directors..."

curl -s "http://localhost:8000/api/search?q=sales+director" | jq '.'

echo ""
echo "Searching for companies in San Francisco..."

curl -s "http://localhost:8000/api/search?q=San+Francisco" | jq '.'
```

## Interactive Demo Commands

### Real-time Agent Monitoring

Create a simple monitoring script:

```bash
#!/bin/bash
# monitor_agents.sh

echo "Starting agent monitoring..."
echo "Press Ctrl+C to stop"

while true; do
  clear
  echo "=== AGENT STATUS DASHBOARD ==="
  echo "Updated: $(date)"
  echo ""
  
  curl -s "http://localhost:8000/api/agents/status" | jq -r '
    .[] | 
    "Agent: \(.company) | Status: \(.status) | Progress: \(.progress)% | \(.message)"
  '
  
  echo ""
  echo "Overall Summary:"
  curl -s "http://localhost:8000/api/summary" | jq -r '
    "Companies: \(.total_companies) | Leads: \(.total_leads)"
  '
  
  sleep 5
done
```

### Chat Interface Demo

Create an interactive chat script:

```bash
#!/bin/bash
# chat_demo.sh

echo "=== AI Scraper Agent Chat Demo ==="
echo "Ask questions about the researched companies"
echo "Type 'exit' to quit"
echo ""

while true; do
  echo -n "Your question: "
  read question
  
  if [ "$question" = "exit" ]; then
    break
  fi
  
  echo "Thinking..."
  answer=$(curl -s -X POST "http://localhost:8000/api/chat" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"$question\"}" | jq -r '.answer')
  
  echo "Answer: $answer"
  echo ""
done
```

## Demo Video Script

For creating a demo video, follow this narrative:

### Script Outline (5-7 minutes)

**[0:00-0:30] Introduction**
- "Welcome to the AI Scraper Agent demo"
- "This system automatically discovers competitors and researches their teams"
- Show the architecture diagram

**[0:30-1:30] Competitor Discovery**
- Enter "HubSpot" as seed company
- Show how AI finds 8 competitors automatically
- Highlight the LLM-powered discovery process

**[1:30-3:00] Multi-Agent Research**
- Launch research for 5 competitors
- Show real-time agent status dashboard
- Explain parallel processing and progress tracking
- Show agent logs and status updates

**[3:00-4:00] Data Collection Results**
- Display research summary
- Show company profiles with enriched data
- Browse lead profiles with contact information
- Demonstrate data quality and completeness

**[4:00-5:30] Intelligence Chat**
- Ask analytical questions:
  - "How many Sales VPs were found?"
  - "Which companies are in San Francisco?"
  - "What's the average company size?"
- Show semantic search capabilities
- Demonstrate contextual understanding

**[5:30-6:30] System Architecture**
- Show agent coordination
- Explain embedding and vector search
- Demonstrate scalability features
- Show API documentation

**[6:30-7:00] Conclusion**
- Summary of capabilities
- Use cases and applications
- Next steps and customization options

### Video Recording Tips

1. **Screen Setup**:
   - Use 1920x1080 resolution
   - Keep terminal windows organized
   - Use large, readable fonts

2. **Demo Flow**:
   - Pre-populate some data for smoother demo
   - Have backup commands ready
   - Test all API endpoints beforehand

3. **Narration Points**:
   - Emphasize AI-powered automation
   - Highlight real-time capabilities
   - Show practical business value
   - Explain technical innovation

## Troubleshooting Demo Issues

### Common Demo Problems

1. **API Rate Limits**:
   ```bash
   # Use shorter delays for demo
   export DEMO_MODE=true
   # This reduces rate limiting delays
   ```

2. **No Results Found**:
   ```bash
   # Use these reliable companies for demos
   DEMO_COMPANIES=("HubSpot" "Salesforce" "Zoom" "Slack" "Atlassian")
   ```

3. **Slow Responses**:
   ```bash
   # Pre-warm the system
   curl "http://localhost:8000/health"
   curl "http://localhost:8000/api/summary"
   ```

### Demo Data Preparation

Create a script to populate demo data:

```bash
#!/bin/bash
# prepare_demo_data.sh

echo "Preparing demo data..."

# Research a few companies to have data ready
companies=("Zoom" "Slack" "Atlassian")

for company in "${companies[@]}"; do
  echo "Researching $company..."
  curl -X POST "http://localhost:8000/api/company/research" \
    -H "Content-Type: application/json" \
    -d "{\"company_name\": \"$company\", \"max_leads\": 10}" > /dev/null
  sleep 2
done

echo "Demo data ready!"
```

This demo script provides a comprehensive walkthrough of all system capabilities, making it perfect for showcasing the AI Scraper Agent's features to stakeholders, potential users, or for creating demonstration videos.
