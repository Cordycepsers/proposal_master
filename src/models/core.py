"""
Core database models for the Automated RFP & Tender Response System.
"""
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from enum import Enum as PyEnum
from sqlalchemy import (
    String, Text, DateTime, Date, Float, Boolean, Integer, 
    JSON, ForeignKey, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..config.database import Base


class TenderStatus(PyEnum):
    """Status of tender opportunities."""
    DISCOVERED = "discovered"
    ANALYZING = "analyzing"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    PROPOSAL_GENERATED = "proposal_generated"
    SUBMITTED = "submitted"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"


class ProposalStatus(PyEnum):
    """Status of proposal generation and submission."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    REJECTED = "rejected"
    WON = "won"
    LOST = "lost"


class RiskLevel(PyEnum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OpportunitySource(PyEnum):
    """Source of tender opportunities."""
    UN_GLOBAL_MARKETPLACE = "un_global_marketplace"
    UNGM = "ungm"
    EU_TED = "eu_ted"
    GOVERNMENT_PORTAL = "government_portal"
    NGO_WEBSITE = "ngo_website"
    EMAIL_ALERT = "email_alert"
    RSS_FEED = "rss_feed"
    MANUAL = "manual"


class TenderOpportunity(Base):
    """Main tender opportunity model."""
    
    __tablename__ = "tender_opportunities"
    
    # Primary fields
    id: Mapped[int] = mapped_column(primary_key=True)
    tender_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Source and discovery
    source: Mapped[OpportunitySource] = mapped_column(Enum(OpportunitySource), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Timeline
    published_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    estimated_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    project_duration_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Financial
    estimated_budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)  # ISO currency code
    budget_range_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_range_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Location and scope
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Organization
    procuring_organization: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    organization_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # UN, NGO, Government, etc.
    contact_person: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Status and assessment
    status: Mapped[TenderStatus] = mapped_column(Enum(TenderStatus), default=TenderStatus.DISCOVERED, index=True)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    win_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    risk_level: Mapped[Optional[RiskLevel]] = mapped_column(Enum(RiskLevel), nullable=True)
    
    # AI Analysis results
    requirements_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    competitive_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    red_flags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    green_flags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Document references
    original_document_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    processed_documents: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    proposals: Mapped[List["Proposal"]] = relationship("Proposal", back_populates="opportunity")
    requirements: Mapped[List["Requirement"]] = relationship("Requirement", back_populates="opportunity")
    
    __table_args__ = (
        Index("ix_tender_status_deadline", "status", "deadline"),
        Index("ix_tender_relevance_score", "relevance_score"),
        Index("ix_tender_organization", "procuring_organization"),
    )


class Requirement(Base):
    """Individual requirements extracted from RFPs."""
    
    __tablename__ = "requirements"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("tender_opportunities.id"), nullable=False, index=True)
    
    # Requirement details
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Technical, Financial, Legal, etc.
    
    # Classification
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Evaluation weight
    compliance_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Full, Partial, None
    
    # Analysis
    complexity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 1-10
    our_capability_match: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    risk_assessment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # AI extraction confidence
    
    # Relationships
    opportunity: Mapped["TenderOpportunity"] = relationship("TenderOpportunity", back_populates="requirements")


class Proposal(Base):
    """Generated proposals for tender opportunities."""
    
    __tablename__ = "proposals"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("tender_opportunities.id"), nullable=False, index=True)
    
    # Proposal identification
    proposal_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    
    # Content
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    technical_approach: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    team_composition: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    timeline: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    budget_breakdown: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Pricing
    total_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    pricing_strategy: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status and quality
    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus), default=ProposalStatus.DRAFT)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    compliance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    
    # Generation metadata
    generated_by: Mapped[str] = mapped_column(String(50), default="ai_system")
    generation_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    generation_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Submission
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submission_confirmation: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Files and documents
    document_paths: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    final_pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    opportunity: Mapped["TenderOpportunity"] = relationship("TenderOpportunity", back_populates="proposals")


class WonBid(Base):
    """Historical data of won bids for learning and analysis."""
    
    __tablename__ = "won_bids"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Basic information
    project_name: Mapped[str] = mapped_column(String(300), nullable=False)
    client_organization: Mapped[str] = mapped_column(String(200), nullable=False)
    award_date: Mapped[date] = mapped_column(Date, nullable=False)
    project_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    
    # Project details
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    service_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    duration_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Success factors
    winning_factors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    competitive_advantages: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    pricing_strategy: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    team_expertise: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Proposal analysis
    proposal_sections: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    technical_approach_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    innovation_elements: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Competition analysis
    number_of_competitors: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    win_margin: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # "Narrow", "Moderate", "Wide"
    
    # Document references
    original_rfp_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    winning_proposal_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    award_notification_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Learning insights
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reusable_components: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    __table_args__ = (
        Index("ix_won_bids_client_sector", "client_organization", "sector"),
        Index("ix_won_bids_award_date", "award_date"),
    )


class ProjectDocumentation(Base):
    """Semantic search index for project documentation and patterns."""
    
    __tablename__ = "project_documentation"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Document identification
    document_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # RFP, Project Report, Funding Announcement
    
    # Source information
    organization: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Content
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Categorization
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    thematic_areas: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    geographic_focus: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Vector embeddings (stored as JSON for flexibility)
    embeddings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Analysis results
    requirement_patterns: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    funding_patterns: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    success_indicators: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # File references
    original_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    processed_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    __table_args__ = (
        Index("ix_project_docs_org_sector", "organization", "sector"),
        Index("ix_project_docs_type_date", "document_type", "publication_date"),
    )
