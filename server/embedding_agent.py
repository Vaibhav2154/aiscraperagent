import json
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import httpx
from models import CompanyProfile, LeadProfile

class EmbeddingAgent:
    def __init__(self, openrouter_api_key: str, model_name: str = "all-MiniLM-L6-v2"):
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="leads_and_companies",
            metadata={"hnsw:space": "cosine"}
        )
    
    def embed_company(self, company: CompanyProfile) -> str:
        """Embed company data and store in vector database"""
        try:
            # Create text representation of company
            company_text = self._company_to_text(company)
            
            # Generate embedding
            embedding = self.embedding_model.encode(company_text).tolist()
            
            # Store in ChromaDB
            doc_id = f"company_{company.name.replace(' ', '_').lower()}"
            
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[company_text],
                metadatas=[{
                    "type": "company",
                    "name": company.name,
                    "industry": company.industry or "",
                    "location": company.location or "",
                    "size": company.size or ""
                }]
            )
            
            return doc_id
            
        except Exception as e:
            print(f"Error embedding company {company.name}: {e}")
            return ""
    
    def embed_lead(self, lead: LeadProfile) -> str:
        """Embed lead data and store in vector database"""
        try:
            # Create text representation of lead
            lead_text = self._lead_to_text(lead)
            
            # Generate embedding
            embedding = self.embedding_model.encode(lead_text).tolist()
            
            # Store in ChromaDB
            doc_id = f"lead_{lead.name.replace(' ', '_').lower()}_{lead.company.replace(' ', '_').lower()}"
            
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[lead_text],
                metadatas=[{
                    "type": "lead",
                    "name": lead.name,
                    "title": lead.title or "",
                    "company": lead.company,
                    "department": lead.department or "",
                    "seniority": lead.seniority or ""
                }]
            )
            
            return doc_id
            
        except Exception as e:
            print(f"Error embedding lead {lead.name}: {e}")
            return ""
    
    def embed_multiple_companies(self, companies: List[CompanyProfile]) -> List[str]:
        """Embed multiple companies"""
        doc_ids = []
        for company in companies:
            doc_id = self.embed_company(company)
            if doc_id:
                doc_ids.append(doc_id)
        return doc_ids
    
    def embed_multiple_leads(self, leads: List[LeadProfile]) -> List[str]:
        """Embed multiple leads"""
        doc_ids = []
        for lead in leads:
            doc_id = self.embed_lead(lead)
            if doc_id:
                doc_ids.append(doc_id)
        return doc_ids
    
    def search_similar(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """Search for similar content based on query"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            return {
                "documents": results["documents"][0],
                "metadatas": results["metadatas"][0],
                "distances": results["distances"][0]
            }
            
        except Exception as e:
            print(f"Error searching similar content: {e}")
            return {"documents": [], "metadatas": [], "distances": []}
    
    async def chat_with_data(self, question: str, context_limit: int = 5) -> Dict[str, Any]:
        """Chat with the embedded data using LLM"""
        try:
            # Search for relevant context
            search_results = self.search_similar(question, n_results=context_limit)
            
            # Prepare context for LLM
            context_docs = search_results["documents"]
            context_metadata = search_results["metadatas"]
            
            if not context_docs:
                return {
                    "answer": "I don't have enough information to answer that question.",
                    "sources": []
                }
            
            # Build context string
            context_str = "\n\n".join([
                f"Document {i+1}: {doc}" 
                for i, doc in enumerate(context_docs)
            ])
            
            # Create prompt for LLM
            prompt = f"""
            Based on the following information about companies and leads, please answer the user's question.
            
            Context:
            {context_str}
            
            Question: {question}
            
            Please provide a helpful and accurate answer based only on the information provided in the context.
            If the information is not available in the context, please say so.
            """
            
            # Get answer from LLM
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
                        "max_tokens": 1500,
                        "temperature": 0.3
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"]
                    
                    # Extract source information
                    sources = []
                    for metadata in context_metadata:
                        if metadata.get("type") == "company":
                            sources.append(f"Company: {metadata.get('name', 'Unknown')}")
                        elif metadata.get("type") == "lead":
                            sources.append(f"Lead: {metadata.get('name', 'Unknown')} at {metadata.get('company', 'Unknown')}")
                    
                    return {
                        "answer": answer,
                        "sources": sources
                    }
                    
        except Exception as e:
            print(f"Error in chat: {e}")
            
        return {
            "answer": "Sorry, I encountered an error while processing your question.",
            "sources": []
        }
    
    def _company_to_text(self, company: CompanyProfile) -> str:
        """Convert company profile to text for embedding"""
        parts = [
            f"Company: {company.name}",
            f"Industry: {company.industry or 'Unknown'}",
            f"Description: {company.description or 'No description available'}",
            f"Size: {company.size or 'Unknown size'}",
            f"Location: {company.location or 'Unknown location'}",
            f"Founded: {company.founded or 'Unknown founding year'}",
            f"Website: {company.website or 'No website'}",
            f"Employee Count: {company.employees_count or 0}"
        ]
        
        if company.funding:
            parts.append(f"Funding: {company.funding}")
            
        return ". ".join(parts)
    
    def _lead_to_text(self, lead: LeadProfile) -> str:
        """Convert lead profile to text for embedding"""
        parts = [
            f"Person: {lead.name}",
            f"Title: {lead.title or 'Unknown title'}",
            f"Company: {lead.company}",
            f"Department: {lead.department or 'Unknown department'}",
            f"Seniority: {lead.seniority or 'Unknown seniority'}",
            f"Location: {lead.location or 'Unknown location'}"
        ]
        
        if lead.email:
            parts.append(f"Email: {lead.email}")
        if lead.phone:
            parts.append(f"Phone: {lead.phone}")
            
        return ". ".join(parts)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedded data"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"total_documents": 0, "collection_name": "unknown"}
