"""
Document analysis and AI-powered insights routes.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ...agents.document_analysis_orchestrator import DocumentAnalysisOrchestrator
from ...utils.ai_config import get_default_ai_client

logger = logging.getLogger(__name__)

router = APIRouter()

class AnalysisRequest(BaseModel):
    """Document analysis request model."""
    document_id: Optional[str] = None
    file_path: Optional[str] = None
    analysis_config: Optional[Dict[str, Any]] = None
    project_context: Optional[Dict[str, Any]] = None
    compliance_standards: Optional[List[str]] = None
    output_format: str = "detailed"

class AnalysisResponse(BaseModel):
    """Document analysis response model."""
    analysis_id: str
    status: str
    document_info: Optional[Dict[str, Any]] = None
    requirement_analysis: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    critical_success_factors: Optional[List[Dict[str, Any]]] = None
    compliance_analysis: Optional[Dict[str, Any]] = None
    integrated_insights: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    executive_summary: Optional[Dict[str, Any]] = None

class QuickAnalysisRequest(BaseModel):
    """Quick analysis request for text content."""
    content: str
    analysis_type: str  # 'requirements', 'risks', 'summary', 'evaluation'
    context: Optional[Dict[str, Any]] = None

class QuickAnalysisResponse(BaseModel):
    """Quick analysis response model."""
    analysis_type: str
    results: Dict[str, Any]
    processing_time: float

class ComparisonRequest(BaseModel):
    """Document comparison request model."""
    document_ids: List[str]
    comparison_type: str = "similarity"  # 'similarity', 'requirements', 'risks'
    weights: Optional[Dict[str, float]] = None

class ComparisonResponse(BaseModel):
    """Document comparison response model."""
    comparison_id: str
    document_ids: List[str]
    comparison_type: str
    results: Dict[str, Any]
    similarity_matrix: Optional[List[List[float]]] = None

@router.post("/comprehensive", response_model=AnalysisResponse)
async def comprehensive_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Perform comprehensive document analysis using all agents.
    
    Args:
        request: Analysis request with document and configuration
        
    Returns:
        AnalysisResponse: Comprehensive analysis results
    """
    try:
        # Validate request
        if not request.document_id and not request.file_path:
            raise HTTPException(
                status_code=400, 
                detail="Either document_id or file_path must be provided"
            )
        
        # Resolve file path
        file_path = request.file_path
        if request.document_id and not file_path:
            # TODO: Resolve file path from document_id
            file_path = f"data/documents/uploads/{request.document_id}_*"
        
        # Initialize orchestrator
        ai_client = get_default_ai_client()
        orchestrator = DocumentAnalysisOrchestrator(ai_client)
        
        # Prepare analysis inputs
        analysis_inputs = {
            'file_path': file_path,
            'analysis_config': request.analysis_config or {},
            'project_context': request.project_context or {},
            'compliance_standards': request.compliance_standards or [],
            'output_format': request.output_format
        }
        
        # Run comprehensive analysis
        results = await orchestrator.process(analysis_inputs)
        
        # Generate analysis ID
        import uuid
        analysis_id = str(uuid.uuid4())
        
        # Convert results to response format
        response = AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            document_info=results.get('document_analysis', {}),
            requirement_analysis=results.get('requirement_analysis', {}),
            risk_assessment=results.get('risk_assessment', {}),
            critical_success_factors=results.get('critical_success_factors', []),
            compliance_analysis=results.get('compliance_analysis', {}),
            integrated_insights=results.get('integrated_insights', {}),
            recommendations=results.get('recommendations', []),
            executive_summary=results.get('executive_summary', {})
        )
        
        # TODO: Store results for future retrieval
        
        logger.info(f"Comprehensive analysis completed: {analysis_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/quick", response_model=QuickAnalysisResponse)
async def quick_analysis(request: QuickAnalysisRequest):
    """
    Perform quick analysis on text content.
    
    Args:
        request: Quick analysis request with content and type
        
    Returns:
        QuickAnalysisResponse: Quick analysis results
    """
    try:
        import time
        start_time = time.time()
        
        # Initialize AI client
        ai_client = get_default_ai_client()
        
        # Perform analysis based on type
        if request.analysis_type == "requirements":
            from ...agents.requirement_extraction_agent import RequirementExtractionAgent
            agent = RequirementExtractionAgent(ai_client)
            results = await agent.process({
                'document_content': request.content,
                'extraction_mode': 'quick'
            })
            
        elif request.analysis_type == "risks":
            from ...agents.risk_assessment_agent import RiskAssessmentAgent
            agent = RiskAssessmentAgent(ai_client)
            results = await agent.process({
                'document_content': request.content,
                'assessment_depth': 'basic'
            })
            
        elif request.analysis_type == "summary":
            from ...agents.document_parser_agent import DocumentParserAgent
            agent = DocumentParserAgent(ai_client)
            results = await agent.process({
                'content': request.content,
                'analysis_depth': 'basic'
            })
            
        elif request.analysis_type == "evaluation":
            from ...agents.analysis_agent import AnalysisAgent
            agent = AnalysisAgent(ai_client)
            results = await agent.process({
                'content': request.content,
                'analyze_criteria': True
            })
            
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown analysis type: {request.analysis_type}"
            )
        
        processing_time = time.time() - start_time
        
        return QuickAnalysisResponse(
            analysis_type=request.analysis_type,
            results=results,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quick analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")

@router.post("/compare", response_model=ComparisonResponse)
async def compare_documents(request: ComparisonRequest):
    """
    Compare multiple documents for similarity or specific aspects.
    
    Args:
        request: Comparison request with document IDs and type
        
    Returns:
        ComparisonResponse: Document comparison results
    """
    try:
        if len(request.document_ids) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 documents required for comparison"
            )
        
        # TODO: Implement document comparison logic
        # This would use the similarity engine and comparison algorithms
        
        import uuid
        comparison_id = str(uuid.uuid4())
        
        # Mock comparison results for now
        results = {
            "documents_compared": len(request.document_ids),
            "comparison_type": request.comparison_type,
            "overall_similarity": 0.75,
            "key_differences": [
                "Document structure variations",
                "Requirement complexity differences",
                "Risk profile variations"
            ],
            "recommendations": [
                "Focus on common requirements across documents",
                "Address unique risks in each document",
                "Consider document-specific strategies"
            ]
        }
        
        # Mock similarity matrix
        n_docs = len(request.document_ids)
        similarity_matrix = [[1.0 if i == j else 0.75 for j in range(n_docs)] 
                           for i in range(n_docs)]
        
        return ComparisonResponse(
            comparison_id=comparison_id,
            document_ids=request.document_ids,
            comparison_type=request.comparison_type,
            results=results,
            similarity_matrix=similarity_matrix
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@router.get("/results/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_results(analysis_id: str):
    """
    Retrieve stored analysis results by ID.
    
    Args:
        analysis_id: The analysis identifier
        
    Returns:
        AnalysisResponse: Stored analysis results
    """
    try:
        # TODO: Implement results storage and retrieval
        # For now, return a mock response
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            document_info={"message": "Analysis results would be retrieved from storage"},
            requirement_analysis={},
            risk_assessment={},
            critical_success_factors=[],
            compliance_analysis={},
            integrated_insights={},
            recommendations=[]
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")

@router.delete("/results/{analysis_id}")
async def delete_analysis_results(analysis_id: str):
    """
    Delete stored analysis results.
    
    Args:
        analysis_id: The analysis identifier
        
    Returns:
        dict: Deletion confirmation
    """
    try:
        # TODO: Implement results deletion
        
        return {
            "message": "Analysis results deleted successfully",
            "analysis_id": analysis_id
        }
        
    except Exception as e:
        logger.error(f"Failed to delete analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete results: {str(e)}")

@router.get("/types")
async def get_analysis_types():
    """
    Get available analysis types and their descriptions.
    
    Returns:
        dict: Available analysis types
    """
    return {
        "comprehensive": {
            "description": "Full document analysis with all agents",
            "includes": [
                "Document parsing and structure analysis",
                "Requirement extraction and categorization", 
                "Risk assessment and mitigation planning",
                "Critical success factor identification",
                "Compliance analysis",
                "Integrated insights and recommendations"
            ],
            "typical_duration": "2-5 minutes",
            "output_formats": ["detailed", "executive_summary", "both"]
        },
        "quick": {
            "description": "Fast analysis of specific aspects",
            "types": {
                "requirements": "Extract and categorize requirements",
                "risks": "Identify and assess risks",
                "summary": "Generate document summary",
                "evaluation": "Analyze evaluation criteria"
            },
            "typical_duration": "10-30 seconds",
            "output_format": "structured_json"
        },
        "comparison": {
            "description": "Compare multiple documents",
            "types": {
                "similarity": "Overall document similarity",
                "requirements": "Requirement-based comparison",
                "risks": "Risk profile comparison"
            },
            "typical_duration": "1-3 minutes",
            "max_documents": 10
        }
    }
