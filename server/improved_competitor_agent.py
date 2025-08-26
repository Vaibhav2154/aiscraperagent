import httpx
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import json
import re
import logging
from dataclasses import dataclass

@dataclass
class CompetitorInfo:
    name: str
    confidence_score: float
    source: str
    industry_match: bool = False
    verified: bool = False

class ImprovedCompetitorDiscoveryAgent:
    def __init__(self, openrouter_api_key: str):
        self.openrouter_api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.logger = logging.getLogger(__name__)
        
        # Company validation patterns
        self.invalid_patterns = [
            r'^company\s+name\s+\d+$',
            r'^competitor\s+[a-c]$',
            r'^example\s+company',
            r'^placeholder',
            r'^dummy',
            r'^test\s+company',
            r'^mock\s+company',
            r'[company|corp|inc|ltd][\s\d]+$',
            r'^[a-z\s]+\s\d+$'
        ]
        
    async def discover_competitors(self, seed_company: str, max_competitors: int = 10) -> List[str]:
        """Discover verified competitors with quality filtering"""
        if not seed_company or len(seed_company.strip()) < 2:
            self.logger.warning(f"Invalid seed company: {seed_company}")
            return []
            
        competitors_with_scores = []
        
        # Phase 1: Get industry-specific competitors from LLM
        llm_competitors = await self._get_verified_competitors_from_llm(seed_company, max_competitors * 2)
        competitors_with_scores.extend(llm_competitors)
        
        # Phase 2: Cross-validate with multiple sources
        validated_competitors = await self._cross_validate_competitors(seed_company, competitors_with_scores)
        
        # Phase 3: Remove low-quality matches
        filtered_competitors = self._filter_quality_competitors(validated_competitors)
        
        # Phase 4: Sort by confidence and return top results
        filtered_competitors.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return [comp.name for comp in filtered_competitors[:max_competitors]]
    
    async def _get_verified_competitors_from_llm(self, seed_company: str, max_competitors: int) -> List[CompetitorInfo]:
        """Enhanced LLM competitor discovery with validation"""
        
        # First, get company industry and context
        industry_context = await self._get_company_context(seed_company)
        
        prompt = f"""
        You are a business intelligence analyst. Analyze the company "{seed_company}" and provide {max_competitors} REAL, EXISTING competitors.
        
        Company Context: {industry_context}
        
        CRITICAL REQUIREMENTS:
        1. Only provide REAL companies that actually exist
        2. Focus on direct competitors in the same industry and market segment
        3. Include both established players and emerging competitors
        4. Do NOT use placeholders like "Company Name 1", "Competitor A", etc.
        5. Verify each company exists and operates in the same space
        6. Include industry leaders and niche players
        
        For each competitor, provide:
        - Company Name (exact legal name)
        - Primary reason why they compete with {seed_company}
        - Industry segment
        
        Format as JSON array:
        [
            {{
                "name": "Exact Company Name",
                "reason": "Why they compete",
                "industry": "Specific industry segment",
                "confidence": 0.9
            }}
        ]
        
        Research competitors of "{seed_company}":
        """
        
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
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
                        "max_tokens": 2000,
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Extract JSON from response
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        try:
                            competitors_data = json.loads(json_match.group())
                            competitors = []
                            
                            for comp_data in competitors_data:
                                if isinstance(comp_data, dict) and 'name' in comp_data:
                                    name = comp_data['name'].strip()
                                    
                                    # Validate competitor name
                                    if self._is_valid_company_name(name, seed_company):
                                        competitors.append(CompetitorInfo(
                                            name=name,
                                            confidence_score=comp_data.get('confidence', 0.7),
                                            source="LLM_Verified",
                                            industry_match=True
                                        ))
                            
                            return competitors
                            
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON parsing error: {e}")
                    
                    # Fallback: Parse line by line if JSON fails
                    return self._parse_text_competitors(content, seed_company)
                    
        except Exception as e:
            self.logger.error(f"Error getting competitors from LLM: {e}")
            
        return []
    
    async def _get_company_context(self, company_name: str) -> str:
        """Get basic company context to improve competitor discovery"""
        prompt = f"""
        Provide a brief analysis of "{company_name}":
        - Primary industry
        - Main products/services
        - Target market
        - Business model
        
        Keep response under 200 words and focus on facts.
        """
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
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
                        "max_tokens": 300,
                        "temperature": 0.2
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                    
        except Exception as e:
            self.logger.error(f"Error getting company context: {e}")
            
        return f"Technology company in the {company_name} industry"
    
    def _is_valid_company_name(self, name: str, seed_company: str) -> bool:
        """Validate if competitor name is legitimate"""
        if not name or len(name.strip()) < 2:
            return False
            
        name_lower = name.lower().strip()
        seed_lower = seed_company.lower().strip()
        
        # Don't include the seed company itself
        if name_lower == seed_lower:
            return False
            
        # Check against invalid patterns
        for pattern in self.invalid_patterns:
            if re.match(pattern, name_lower):
                return False
                
        # Additional quality checks
        if len(name) > 100:  # Unreasonably long
            return False
            
        if name.count(' ') > 6:  # Too many words
            return False
            
        # Check for placeholder indicators
        placeholder_words = ['placeholder', 'example', 'dummy', 'test', 'mock', 'sample']
        if any(word in name_lower for word in placeholder_words):
            return False
            
        return True
    
    def _parse_text_competitors(self, content: str, seed_company: str) -> List[CompetitorInfo]:
        """Parse competitors from text when JSON parsing fails"""
        competitors = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Clean up the line
            line = re.sub(r'^\d+\.\s*', '', line)  # Remove numbering
            line = re.sub(r'^[-*]\s*', '', line)   # Remove bullet points
            line = line.strip()
            
            # Extract company name (before any dash or colon)
            company_match = re.match(r'^([^-:]+)', line)
            if company_match:
                name = company_match.group(1).strip()
                
                if self._is_valid_company_name(name, seed_company):
                    competitors.append(CompetitorInfo(
                        name=name,
                        confidence_score=0.6,
                        source="LLM_Text",
                        industry_match=True
                    ))
        
        return competitors
    
    async def _cross_validate_competitors(self, seed_company: str, competitors: List[CompetitorInfo]) -> List[CompetitorInfo]:
        """Cross-validate competitors with additional verification"""
        validated = []
        
        for competitor in competitors:
            # Verify the competitor exists and is relevant
            is_valid = await self._verify_competitor_relevance(seed_company, competitor.name)
            
            if is_valid:
                competitor.verified = True
                competitor.confidence_score += 0.2
                validated.append(competitor)
            elif competitor.confidence_score > 0.8:
                # Keep high confidence competitors even if verification fails
                validated.append(competitor)
                
        return validated
    
    async def _verify_competitor_relevance(self, seed_company: str, competitor_name: str) -> bool:
        """Verify if a competitor is actually relevant"""
        prompt = f"""
        Are "{competitor_name}" and "{seed_company}" direct competitors?
        
        Answer with only: YES or NO
        
        Consider:
        - Do they operate in the same industry?
        - Do they target similar customers?
        - Do they offer competing products/services?
        """
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
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
                        "max_tokens": 10,
                        "temperature": 0.1
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip().upper()
                    return "YES" in answer
                    
        except Exception as e:
            self.logger.error(f"Error verifying competitor relevance: {e}")
            
        return False
    
    def _filter_quality_competitors(self, competitors: List[CompetitorInfo]) -> List[CompetitorInfo]:
        """Filter out low quality competitors"""
        filtered = []
        
        for competitor in competitors:
            # Quality thresholds
            min_confidence = 0.5
            
            if competitor.verified:
                min_confidence = 0.3
                
            if competitor.confidence_score >= min_confidence:
                filtered.append(competitor)
                
        # Remove duplicates (case-insensitive)
        seen_names = set()
        unique_competitors = []
        
        for competitor in filtered:
            name_lower = competitor.name.lower()
            if name_lower not in seen_names:
                seen_names.add(name_lower)
                unique_competitors.append(competitor)
                
        return unique_competitors
