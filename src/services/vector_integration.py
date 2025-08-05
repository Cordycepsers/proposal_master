"""
Vector Database Integration Service

This service integrates the vector database with the existing RFP workflow,
providing semantic search capabilities for tender opportunities, requirements,
proposals, and project documentation.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src.core.vector_database import (
    VectorDatabase, VectorDocument, VectorIndexConfig, 
    SearchResult, create_document_chunks
)
from src.models.core import (
    TenderOpportunity, Requirement, Proposal, 
    WonBid, ProjectDocumentation
)
from src.config.database import get_db

logger = logging.getLogger(__name__)

class VectorIntegrationService:
    """Service for integrating vector database with RFP workflow"""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
        self.logger = logging.getLogger(__name__)
    
    async def index_tender_opportunity(self, tender: TenderOpportunity) -> List[str]:
        """Index a tender opportunity in the vector database"""
        try:
            documents = []
            
            # Create main document from tender description
            if tender.description:
                main_doc = VectorDocument(
                    id=f"tender_{tender.id}",
                    content=f"Title: {tender.title}\n\nDescription: {tender.description}",
                    metadata={
                        'type': 'tender_opportunity',
                        'tender_id': str(tender.id),
                        'organization': tender.organization,
                        'category': tender.category,
                        'status': tender.status.value,
                        'deadline': tender.deadline.isoformat() if tender.deadline else None,
                        'budget_min': float(tender.budget_min) if tender.budget_min else None,
                        'budget_max': float(tender.budget_max) if tender.budget_max else None,
                        'country': tender.country,
                        'region': tender.region
                    },
                    source='tender_opportunity'
                )
                documents.append(main_doc)
            
            # Index requirements as separate documents
            if tender.requirements:
                for req in tender.requirements:
                    if req.description:
                        req_doc = VectorDocument(
                            id=f"requirement_{req.id}",
                            content=f"Requirement: {req.requirement_text}\n\nDescription: {req.description}",
                            metadata={
                                'type': 'requirement',
                                'requirement_id': str(req.id),
                                'tender_id': str(tender.id),
                                'category': req.category,
                                'priority': req.priority.value if req.priority else None,
                                'is_mandatory': req.is_mandatory
                            },
                            source='requirement',
                            parent_document_id=f"tender_{tender.id}"
                        )
                        documents.append(req_doc)
            
            # Add documents to vector database
            if documents:
                added_ids = await self.vector_db.add_documents(documents)
                self.logger.info(f"Indexed tender {tender.id} with {len(added_ids)} documents")
                return added_ids
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to index tender {tender.id}: {e}")
            raise
    
    async def index_proposal(self, proposal: Proposal) -> List[str]:
        """Index a proposal in the vector database"""
        try:
            documents = []
            
            # Create chunks from proposal content
            if proposal.content:
                content_text = f"Proposal Title: {proposal.title}\n\n"
                if proposal.executive_summary:
                    content_text += f"Executive Summary: {proposal.executive_summary}\n\n"
                content_text += f"Full Content: {proposal.content}"
                
                # Create chunks for large proposals
                chunks = create_document_chunks(
                    document_id=f"proposal_{proposal.id}",
                    content=content_text,
                    metadata={
                        'type': 'proposal',
                        'proposal_id': str(proposal.id),
                        'tender_id': str(proposal.tender_id),
                        'status': proposal.status.value,
                        'submitted_at': proposal.submitted_at.isoformat() if proposal.submitted_at else None,
                        'score': float(proposal.score) if proposal.score else None
                    },
                    chunk_size=1500,
                    overlap=150
                )
                documents.extend(chunks)
            
            # Add documents to vector database
            if documents:
                added_ids = await self.vector_db.add_documents(documents)
                self.logger.info(f"Indexed proposal {proposal.id} with {len(added_ids)} documents")
                return added_ids
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to index proposal {proposal.id}: {e}")
            raise
    
    async def index_won_bid(self, won_bid: WonBid) -> List[str]:
        """Index a won bid for pattern learning"""
        try:
            documents = []
            
            # Create comprehensive document from won bid
            content_parts = [f"Won Bid - {won_bid.project_title}"]
            
            if won_bid.project_description:
                content_parts.append(f"Project Description: {won_bid.project_description}")
            
            if won_bid.winning_factors:
                if isinstance(won_bid.winning_factors, dict):
                    factors_text = "\n".join([f"- {k}: {v}" for k, v in won_bid.winning_factors.items()])
                else:
                    factors_text = str(won_bid.winning_factors)
                content_parts.append(f"Winning Factors:\n{factors_text}")
            
            if won_bid.lessons_learned:
                if isinstance(won_bid.lessons_learned, dict):
                    lessons_text = "\n".join([f"- {k}: {v}" for k, v in won_bid.lessons_learned.items()])
                else:
                    lessons_text = str(won_bid.lessons_learned)
                content_parts.append(f"Lessons Learned:\n{lessons_text}")
            
            content = "\n\n".join(content_parts)
            
            main_doc = VectorDocument(
                id=f"wonbid_{won_bid.id}",
                content=content,
                metadata={
                    'type': 'won_bid',
                    'won_bid_id': str(won_bid.id),
                    'tender_id': str(won_bid.tender_id) if won_bid.tender_id else None,
                    'client_organization': won_bid.client_organization,
                    'project_value': float(won_bid.project_value) if won_bid.project_value else None,
                    'contract_duration': won_bid.contract_duration,
                    'success_score': float(won_bid.success_score) if won_bid.success_score else None,
                    'year': won_bid.contract_start_date.year if won_bid.contract_start_date else None
                },
                source='won_bid'
            )
            documents.append(main_doc)
            
            # Add documents to vector database
            if documents:
                added_ids = await self.vector_db.add_documents(documents)
                self.logger.info(f"Indexed won bid {won_bid.id} with {len(added_ids)} documents")
                return added_ids
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to index won bid {won_bid.id}: {e}")
            raise
    
    async def index_project_documentation(self, project_doc: ProjectDocumentation) -> List[str]:
        """Index project documentation for semantic search"""
        try:
            documents = []
            
            # Create chunks from documentation content
            if project_doc.content:
                content_text = f"Document Title: {project_doc.title}\n\n"
                if project_doc.summary:
                    content_text += f"Summary: {project_doc.summary}\n\n"
                content_text += f"Content: {project_doc.content}"
                
                # Create chunks for large documents
                chunks = create_document_chunks(
                    document_id=f"projectdoc_{project_doc.id}",
                    content=content_text,
                    metadata={
                        'type': 'project_documentation',
                        'doc_id': str(project_doc.id),
                        'doc_type': project_doc.document_type,
                        'organization': project_doc.organization,
                        'region': project_doc.region,
                        'sector': project_doc.sector,
                        'tags': project_doc.tags,
                        'relevance_score': float(project_doc.relevance_score) if project_doc.relevance_score else None,
                        'document_date': project_doc.document_date.isoformat() if project_doc.document_date else None
                    },
                    chunk_size=1200,
                    overlap=120
                )
                documents.extend(chunks)
            
            # Add documents to vector database
            if documents:
                added_ids = await self.vector_db.add_documents(documents)
                self.logger.info(f"Indexed project documentation {project_doc.id} with {len(added_ids)} documents")
                return added_ids
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to index project documentation {project_doc.id}: {e}")
            raise
    
    async def semantic_search_tenders(self, query: str, 
                                    top_k: int = 10,
                                    filters: Optional[Dict[str, Any]] = None) -> List[Tuple[TenderOpportunity, float]]:
        """Search for similar tender opportunities"""
        try:
            # Add type filter
            search_filters = {'type': 'tender_opportunity'}
            if filters:
                search_filters.update(filters)
            
            # Perform vector search
            results = await self.vector_db.search(
                query=query,
                top_k=top_k,
                filters=search_filters
            )
            
            # Fetch corresponding database objects
            tender_results = []
            async with get_db() as db:
                for result in results:
                    tender_id = result.document.metadata.get('tender_id')
                    if tender_id:
                        stmt = select(TenderOpportunity).where(TenderOpportunity.id == int(tender_id))
                        db_result = await db.execute(stmt)
                        tender = db_result.scalar_one_or_none()
                        if tender:
                            tender_results.append((tender, result.similarity_score))
            
            return tender_results
            
        except Exception as e:
            self.logger.error(f"Semantic search for tenders failed: {e}")
            raise
    
    async def find_similar_won_bids(self, query: str, 
                                  top_k: int = 5) -> List[Tuple[WonBid, float]]:
        """Find similar won bids for pattern learning"""
        try:
            # Search for won bids
            results = await self.vector_db.search(
                query=query,
                top_k=top_k,
                filters={'type': 'won_bid'}
            )
            
            # Fetch corresponding database objects
            wonbid_results = []
            async with get_db() as db:
                for result in results:
                    wonbid_id = result.document.metadata.get('won_bid_id')
                    if wonbid_id:
                        stmt = select(WonBid).where(WonBid.id == int(wonbid_id))
                        db_result = await db.execute(stmt)
                        wonbid = db_result.scalar_one_or_none()
                        if wonbid:
                            wonbid_results.append((wonbid, result.similarity_score))
            
            return wonbid_results
            
        except Exception as e:
            self.logger.error(f"Won bid similarity search failed: {e}")
            raise
    
    async def search_project_documentation(self, query: str, 
                                         top_k: int = 10,
                                         doc_type: Optional[str] = None,
                                         organization: Optional[str] = None) -> List[Tuple[ProjectDocumentation, float]]:
        """Search project documentation with semantic similarity"""
        try:
            # Build filters
            filters = {'type': 'project_documentation'}
            if doc_type:
                filters['doc_type'] = doc_type
            if organization:
                filters['organization'] = organization
            
            # Perform vector search
            results = await self.vector_db.search(
                query=query,
                top_k=top_k,
                filters=filters
            )
            
            # Fetch corresponding database objects
            doc_results = []
            async with get_db() as db:
                for result in results:
                    doc_id = result.document.metadata.get('doc_id')
                    if doc_id:
                        stmt = select(ProjectDocumentation).where(ProjectDocumentation.id == int(doc_id))
                        db_result = await db.execute(stmt)
                        project_doc = db_result.scalar_one_or_none()
                        if project_doc:
                            doc_results.append((project_doc, result.similarity_score))
            
            return doc_results
            
        except Exception as e:
            self.logger.error(f"Project documentation search failed: {e}")
            raise
    
    async def get_recommendations_for_tender(self, tender_id: int, 
                                           top_k: int = 5) -> Dict[str, Any]:
        """Get comprehensive recommendations for a tender based on historical data"""
        try:
            async with get_db() as db:
                # Get the tender
                stmt = select(TenderOpportunity).where(TenderOpportunity.id == tender_id)
                result = await db.execute(stmt)
                tender = result.scalar_one_or_none()
                
                if not tender:
                    raise ValueError(f"Tender {tender_id} not found")
                
                # Create search query from tender
                search_query = f"{tender.title} {tender.description or ''}"
                
                # Find similar won bids
                similar_wonbids = await self.find_similar_won_bids(search_query, top_k)
                
                # Find similar project documentation
                similar_docs = await self.search_project_documentation(search_query, top_k)
                
                # Extract patterns from won bids
                winning_patterns = []
                for wonbid, score in similar_wonbids:
                    if wonbid.winning_factors:
                        winning_patterns.append({
                            'project': wonbid.project_title,
                            'score': score,
                            'factors': wonbid.winning_factors,
                            'project_value': wonbid.project_value,
                            'success_score': wonbid.success_score
                        })
                
                # Extract relevant documentation
                relevant_docs = []
                for doc, score in similar_docs:
                    relevant_docs.append({
                        'title': doc.title,
                        'organization': doc.organization,
                        'score': score,
                        'doc_type': doc.document_type,
                        'summary': doc.summary
                    })
                
                return {
                    'tender_id': tender_id,
                    'similar_won_bids': len(similar_wonbids),
                    'winning_patterns': winning_patterns,
                    'relevant_documentation': relevant_docs,
                    'recommendations': self._generate_recommendations(winning_patterns, relevant_docs)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get recommendations for tender {tender_id}: {e}")
            raise
    
    def _generate_recommendations(self, winning_patterns: List[Dict], 
                                relevant_docs: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on patterns"""
        recommendations = []
        
        # Analyze winning factors
        factor_frequency = {}
        for pattern in winning_patterns:
            if isinstance(pattern.get('factors'), dict):
                for factor, description in pattern['factors'].items():
                    factor_frequency[factor] = factor_frequency.get(factor, 0) + 1
        
        # Generate recommendations based on most common factors
        if factor_frequency:
            top_factors = sorted(factor_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
            for factor, count in top_factors:
                recommendations.append(f"Focus on {factor} - appeared in {count} similar winning bids")
        
        # Add documentation-based recommendations
        if relevant_docs:
            org_types = set(doc.get('organization', '') for doc in relevant_docs if doc.get('organization'))
            if org_types:
                recommendations.append(f"Consider experience with organizations like: {', '.join(list(org_types)[:3])}")
        
        return recommendations
    
    async def bulk_reindex(self, batch_size: int = 50):
        """Reindex all documents in the database"""
        try:
            self.logger.info("Starting bulk reindex of all documents")
            
            async with get_db() as db:
                # Index tender opportunities
                stmt = select(TenderOpportunity).options(selectinload(TenderOpportunity.requirements))
                result = await db.execute(stmt)
                tenders = result.scalars().all()
                
                for i in range(0, len(tenders), batch_size):
                    batch = tenders[i:i + batch_size]
                    for tender in batch:
                        await self.index_tender_opportunity(tender)
                    self.logger.info(f"Indexed {i + len(batch)}/{len(tenders)} tenders")
                
                # Index proposals
                stmt = select(Proposal)
                result = await db.execute(stmt)
                proposals = result.scalars().all()
                
                for i in range(0, len(proposals), batch_size):
                    batch = proposals[i:i + batch_size]
                    for proposal in batch:
                        await self.index_proposal(proposal)
                    self.logger.info(f"Indexed {i + len(batch)}/{len(proposals)} proposals")
                
                # Index won bids
                stmt = select(WonBid)
                result = await db.execute(stmt)
                won_bids = result.scalars().all()
                
                for i in range(0, len(won_bids), batch_size):
                    batch = won_bids[i:i + batch_size]
                    for won_bid in batch:
                        await self.index_won_bid(won_bid)
                    self.logger.info(f"Indexed {i + len(batch)}/{len(won_bids)} won bids")
                
                # Index project documentation
                stmt = select(ProjectDocumentation)
                result = await db.execute(stmt)
                project_docs = result.scalars().all()
                
                for i in range(0, len(project_docs), batch_size):
                    batch = project_docs[i:i + batch_size]
                    for project_doc in batch:
                        await self.index_project_documentation(project_doc)
                    self.logger.info(f"Indexed {i + len(batch)}/{len(project_docs)} project documents")
            
            self.logger.info("Bulk reindex completed successfully")
            
        except Exception as e:
            self.logger.error(f"Bulk reindex failed: {e}")
            raise

# Factory function for creating the integration service
def create_vector_integration_service(
    embedding_model: str = "all-MiniLM-L6-v2",
    index_path: str = "data/embeddings/rfp_vector_index.faiss"
) -> VectorIntegrationService:
    """Create a vector integration service with default configuration"""
    
    from src.core.vector_database import create_vector_database
    
    vector_db = create_vector_database(
        embedding_model=embedding_model,
        index_path=index_path,
        index_type="IndexFlatIP"  # Use cosine similarity
    )
    
    return VectorIntegrationService(vector_db)
