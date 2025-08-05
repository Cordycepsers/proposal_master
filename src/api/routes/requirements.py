"""
Requirements management and extraction routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ...agents.requirement_extraction_agent import (
    RequirementExtractionAgent,
    Requirement,
    RequirementType,
    RequirementPriority,
    RequirementComplexity
)
from ...utils.ai_config import get_default_ai_client

logger = logging.getLogger(__name__)

router = APIRouter()

class RequirementRequest(BaseModel):
    """Requirement extraction request model."""
    document_id: Optional[str] = None
    content: Optional[str] = None
    extraction_mode: str = "hybrid"  # 'ai', 'pattern', 'hybrid'
    include_dependencies: bool = True
    generate_traceability: bool = True
    compliance_focus: Optional[List[str]] = None

class RequirementResponse(BaseModel):
    """Requirement extraction response model."""
    extraction_id: str
    status: str
    requirements: List[Dict[str, Any]]
    analysis_summary: Dict[str, Any]
    traceability_matrix: Optional[Dict[str, Any]] = None
    compliance_mapping: Optional[Dict[str, Any]] = None

class RequirementValidationRequest(BaseModel):
    """Requirement validation request model."""
    requirements: List[Dict[str, Any]]
    validation_criteria: Optional[Dict[str, Any]] = None

class RequirementValidationResponse(BaseModel):
    """Requirement validation response model."""
    validation_id: str
    status: str
    validation_results: List[Dict[str, Any]]
    overall_score: float
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]

class RequirementMatrix(BaseModel):
    """Requirement traceability matrix model."""
    matrix_id: str
    requirements: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    coverage_analysis: Dict[str, Any]

@router.post("/extract", response_model=RequirementResponse)
async def extract_requirements(request: RequirementRequest):
    """
    Extract requirements from document content.
    
    Args:
        request: Requirement extraction request
        
    Returns:
        RequirementResponse: Extracted requirements and analysis
    """
    try:
        # Validate request
        if not request.document_id and not request.content:
            raise HTTPException(
                status_code=400,
                detail="Either document_id or content must be provided"
            )
        
        # Get content if document_id provided
        content = request.content
        if request.document_id and not content:
            # TODO: Retrieve content from document_id
            content = "Mock document content for extraction"
        
        # Initialize extraction agent
        ai_client = get_default_ai_client()
        agent = RequirementExtractionAgent(ai_client)
        
        # Prepare extraction inputs
        extraction_inputs = {
            'document_content': content,
            'extraction_mode': request.extraction_mode,
            'include_dependencies': request.include_dependencies,
            'generate_traceability': request.generate_traceability,
            'compliance_focus': request.compliance_focus or []
        }
        
        # Extract requirements
        results = await agent.process(extraction_inputs)
        
        # Generate extraction ID
        import uuid
        extraction_id = str(uuid.uuid4())
        
        # Convert requirements to serializable format
        requirements_list = []
        for req in results.get('requirements', []):
            if hasattr(req, '__dict__'):
                # Convert dataclass to dict
                req_dict = {
                    'id': req.id,
                    'text': req.text,
                    'type': req.type.value if hasattr(req.type, 'value') else str(req.type),
                    'priority': req.priority.value if hasattr(req.priority, 'value') else str(req.priority),
                    'complexity': req.complexity.value if hasattr(req.complexity, 'value') else str(req.complexity),
                    'section': req.section,
                    'dependencies': req.dependencies or [],
                    'compliance_standards': req.compliance_standards or [],
                    'acceptance_criteria': req.acceptance_criteria or [],
                    'business_value': req.business_value,
                    'technical_risk': req.technical_risk,
                    'estimated_effort': req.estimated_effort,
                    'source_location': req.source_location
                }
            else:
                req_dict = req
            
            requirements_list.append(req_dict)
        
        response = RequirementResponse(
            extraction_id=extraction_id,
            status="completed",
            requirements=requirements_list,
            analysis_summary=results.get('analysis_summary', {}),
            traceability_matrix=results.get('traceability_matrix'),
            compliance_mapping=results.get('compliance_mapping')
        )
        
        logger.info(f"Requirements extracted: {extraction_id} ({len(requirements_list)} requirements)")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Requirement extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.post("/validate", response_model=RequirementValidationResponse)
async def validate_requirements(request: RequirementValidationRequest):
    """
    Validate a set of requirements for completeness and quality.
    
    Args:
        request: Requirement validation request
        
    Returns:
        RequirementValidationResponse: Validation results
    """
    try:
        import uuid
        validation_id = str(uuid.uuid4())
        
        validation_results = []
        issues_found = []
        total_score = 0
        
        # Validate each requirement
        for i, req in enumerate(request.requirements):
            req_id = req.get('id', f"REQ-{i+1}")
            req_text = req.get('text', '')
            
            # Check completeness
            completeness_score = 0
            if req_text and len(req_text) > 10:
                completeness_score += 25
            if req.get('type'):
                completeness_score += 15
            if req.get('priority'):
                completeness_score += 15
            if req.get('acceptance_criteria'):
                completeness_score += 25
            if req.get('business_value'):
                completeness_score += 20
            
            # Check quality
            quality_issues = []
            if len(req_text) < 20:
                quality_issues.append("Requirement text too brief")
            if not req.get('acceptance_criteria'):
                quality_issues.append("Missing acceptance criteria")
            if req.get('priority') == 'unknown':
                quality_issues.append("Priority not specified")
            
            validation_result = {
                'requirement_id': req_id,
                'completeness_score': completeness_score,
                'quality_issues': quality_issues,
                'suggestions': []
            }
            
            # Add suggestions based on issues
            if completeness_score < 80:
                validation_result['suggestions'].append("Add more detailed description")
            if not req.get('acceptance_criteria'):
                validation_result['suggestions'].append("Define clear acceptance criteria")
            
            validation_results.append(validation_result)
            total_score += completeness_score
            
            # Collect issues
            for issue in quality_issues:
                issues_found.append({
                    'requirement_id': req_id,
                    'issue_type': 'quality',
                    'description': issue,
                    'severity': 'medium'
                })
        
        # Calculate overall score
        overall_score = total_score / max(len(request.requirements), 1)
        
        # Generate recommendations
        recommendations = []
        if overall_score < 60:
            recommendations.append("Consider revising requirements for better clarity and completeness")
        if len(issues_found) > len(request.requirements) * 0.5:
            recommendations.append("Address quality issues before proceeding with implementation")
        recommendations.append("Ensure all mandatory requirements have clear acceptance criteria")
        
        response = RequirementValidationResponse(
            validation_id=validation_id,
            status="completed",
            validation_results=validation_results,
            overall_score=overall_score,
            issues_found=issues_found,
            recommendations=recommendations
        )
        
        logger.info(f"Requirements validated: {validation_id} (score: {overall_score:.1f})")
        return response
        
    except Exception as e:
        logger.error(f"Requirement validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.post("/matrix", response_model=RequirementMatrix)
async def generate_traceability_matrix(document_id: str):
    """
    Generate requirement traceability matrix for a document.
    
    Args:
        document_id: Document identifier
        
    Returns:
        RequirementMatrix: Traceability matrix with relationships
    """
    try:
        import uuid
        matrix_id = str(uuid.uuid4())
        
        # TODO: Retrieve requirements for document
        # Mock data for now
        requirements = [
            {
                'id': 'REQ-001',
                'text': 'System must provide 99.9% uptime',
                'type': 'technical',
                'priority': 'mandatory',
                'section': 'Technical Requirements'
            },
            {
                'id': 'REQ-002', 
                'text': 'Data must be encrypted',
                'type': 'security',
                'priority': 'mandatory',
                'section': 'Security Requirements'
            }
        ]
        
        relationships = [
            {
                'from_requirement': 'REQ-001',
                'to_requirement': 'REQ-002',
                'relationship_type': 'depends_on',
                'description': 'Uptime requires secure data handling'
            }
        ]
        
        coverage_analysis = {
            'total_requirements': len(requirements),
            'traced_requirements': len(relationships),
            'coverage_percentage': (len(relationships) / max(len(requirements), 1)) * 100,
            'orphaned_requirements': [],
            'circular_dependencies': []
        }
        
        matrix = RequirementMatrix(
            matrix_id=matrix_id,
            requirements=requirements,
            relationships=relationships,
            coverage_analysis=coverage_analysis
        )
        
        logger.info(f"Traceability matrix generated: {matrix_id}")
        return matrix
        
    except Exception as e:
        logger.error(f"Matrix generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Matrix generation failed: {str(e)}")

@router.get("/types")
async def get_requirement_types():
    """
    Get available requirement types and their descriptions.
    
    Returns:
        dict: Available requirement types
    """
    return {
        "types": {
            "functional": "Functional capabilities and features",
            "technical": "Technical specifications and constraints",
            "performance": "Performance and scalability requirements",
            "security": "Security and access control requirements",
            "compliance": "Regulatory and compliance requirements",
            "integration": "System integration requirements",
            "usability": "User experience and interface requirements",
            "operational": "Operations and maintenance requirements"
        },
        "priorities": {
            "mandatory": "Must be implemented - non-negotiable",
            "important": "Should be implemented - high value",
            "desirable": "Could be implemented - nice to have",
            "optional": "May be implemented - low priority"
        },
        "complexity": {
            "low": "Simple, straightforward implementation",
            "medium": "Moderate complexity, some challenges",
            "high": "Complex, significant technical challenges",
            "critical": "Very complex, major technical risks"
        }
    }

@router.get("/standards")
async def get_compliance_standards():
    """
    Get available compliance standards for requirement mapping.
    
    Returns:
        dict: Available compliance standards
    """
    return {
        "security": [
            "ISO 27001",
            "SOC 2",
            "NIST Cybersecurity Framework",
            "PCI DSS"
        ],
        "quality": [
            "ISO 9001",
            "CMMI",
            "IEEE Standards"
        ],
        "industry": [
            "HIPAA (Healthcare)",
            "GDPR (Privacy)",
            "Sarbanes-Oxley (Finance)",
            "FedRAMP (Government)"
        ],
        "technical": [
            "ISO 25010 (Software Quality)",
            "W3C Web Standards",
            "OWASP Security Standards"
        ]
    }
