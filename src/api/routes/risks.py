"""
Risk assessment and management routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ...agents.risk_assessment_agent import RiskAssessmentAgent
from ...utils.ai_config import get_default_ai_client

logger = logging.getLogger(__name__)

router = APIRouter()

class RiskAssessmentRequest(BaseModel):
    """Risk assessment request model."""
    document_id: Optional[str] = None
    content: Optional[str] = None
    requirements: Optional[List[Dict[str, Any]]] = None
    project_context: Optional[Dict[str, Any]] = None
    assessment_depth: str = "detailed"  # 'basic', 'detailed', 'comprehensive'
    include_quantitative: bool = True

class RiskAssessmentResponse(BaseModel):
    """Risk assessment response model."""
    assessment_id: str
    status: str
    identified_risks: List[Dict[str, Any]]
    risk_matrix: Dict[str, Any]
    mitigation_strategies: List[Dict[str, Any]]
    quantitative_analysis: Optional[Dict[str, Any]] = None
    contingency_plans: Optional[List[Dict[str, Any]]] = None

class RiskMonitoringRequest(BaseModel):
    """Risk monitoring setup request model."""
    risks: List[str]  # Risk IDs to monitor
    monitoring_frequency: str = "weekly"  # 'daily', 'weekly', 'monthly'
    alert_thresholds: Optional[Dict[str, float]] = None
    stakeholders: Optional[List[str]] = None

class RiskMonitoringResponse(BaseModel):
    """Risk monitoring setup response model."""
    monitoring_id: str
    status: str
    monitored_risks: List[Dict[str, Any]]
    monitoring_schedule: Dict[str, Any]
    alert_configuration: Dict[str, Any]

class MitigationPlanRequest(BaseModel):
    """Mitigation plan generation request model."""
    risk_id: str
    risk_details: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

class MitigationPlanResponse(BaseModel):
    """Mitigation plan response model."""
    plan_id: str
    risk_id: str
    mitigation_strategies: List[Dict[str, Any]]
    implementation_plan: Dict[str, Any]
    success_metrics: List[Dict[str, Any]]
    estimated_cost: Optional[Dict[str, Any]] = None

@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_risks(request: RiskAssessmentRequest):
    """
    Perform comprehensive risk assessment on document or project.
    
    Args:
        request: Risk assessment request with content and configuration
        
    Returns:
        RiskAssessmentResponse: Comprehensive risk analysis
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
            content = "Mock document content for risk assessment"
        
        # Initialize risk assessment agent
        ai_client = get_default_ai_client()
        agent = RiskAssessmentAgent(ai_client)
        
        # Prepare assessment inputs
        assessment_inputs = {
            'document_content': content,
            'requirements': request.requirements or [],
            'project_context': request.project_context or {},
            'assessment_depth': request.assessment_depth,
            'include_quantitative': request.include_quantitative
        }
        
        # Perform risk assessment
        results = await agent.process(assessment_inputs)
        
        # Generate assessment ID
        import uuid
        assessment_id = str(uuid.uuid4())
        
        # Convert risks to serializable format
        identified_risks = []
        for risk in results.get('identified_risks', []):
            if hasattr(risk, '__dict__'):
                # Convert dataclass to dict
                risk_dict = {
                    'id': risk.id,
                    'title': risk.title,
                    'description': risk.description,
                    'category': risk.category.value if hasattr(risk.category, 'value') else str(risk.category),
                    'probability': risk.probability,
                    'impact': risk.impact,
                    'risk_score': risk.risk_score,
                    'dependencies': risk.dependencies or [],
                    'early_warning_signs': risk.early_warning_signs or [],
                    'source_location': risk.source_location,
                    'affected_requirements': risk.affected_requirements or []
                }
            else:
                risk_dict = risk
            
            identified_risks.append(risk_dict)
        
        response = RiskAssessmentResponse(
            assessment_id=assessment_id,
            status="completed",
            identified_risks=identified_risks,
            risk_matrix=results.get('risk_matrix', {}),
            mitigation_strategies=results.get('mitigation_strategies', []),
            quantitative_analysis=results.get('quantitative_analysis'),
            contingency_plans=results.get('contingency_plans')
        )
        
        logger.info(f"Risk assessment completed: {assessment_id} ({len(identified_risks)} risks)")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk assessment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@router.post("/monitor", response_model=RiskMonitoringResponse)
async def setup_risk_monitoring(request: RiskMonitoringRequest):
    """
    Set up automated risk monitoring for specified risks.
    
    Args:
        request: Risk monitoring setup request
        
    Returns:
        RiskMonitoringResponse: Monitoring configuration
    """
    try:
        import uuid
        monitoring_id = str(uuid.uuid4())
        
        # Configure monitoring for each risk
        monitored_risks = []
        for risk_id in request.risks:
            monitored_risks.append({
                'risk_id': risk_id,
                'monitoring_enabled': True,
                'frequency': request.monitoring_frequency,
                'last_check': None,
                'status': 'active',
                'alert_threshold': request.alert_thresholds.get(risk_id, 0.7) if request.alert_thresholds else 0.7
            })
        
        # Configure monitoring schedule
        frequency_map = {
            'daily': {'interval_hours': 24, 'description': 'Daily risk checks'},
            'weekly': {'interval_hours': 168, 'description': 'Weekly risk reviews'},
            'monthly': {'interval_hours': 720, 'description': 'Monthly risk assessments'}
        }
        
        monitoring_schedule = frequency_map.get(request.monitoring_frequency, frequency_map['weekly'])
        monitoring_schedule['total_risks'] = len(request.risks)
        monitoring_schedule['next_check'] = "To be scheduled"
        
        # Configure alerts
        alert_configuration = {
            'enabled': True,
            'stakeholders': request.stakeholders or [],
            'notification_methods': ['email', 'dashboard'],
            'escalation_levels': {
                'low': 'Dashboard notification',
                'medium': 'Email notification',
                'high': 'Immediate email and SMS',
                'critical': 'Phone call and emergency escalation'
            }
        }
        
        response = RiskMonitoringResponse(
            monitoring_id=monitoring_id,
            status="configured",
            monitored_risks=monitored_risks,
            monitoring_schedule=monitoring_schedule,
            alert_configuration=alert_configuration
        )
        
        logger.info(f"Risk monitoring configured: {monitoring_id} ({len(request.risks)} risks)")
        return response
        
    except Exception as e:
        logger.error(f"Risk monitoring setup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Monitoring setup failed: {str(e)}")

@router.post("/mitigate", response_model=MitigationPlanResponse)
async def generate_mitigation_plan(request: MitigationPlanRequest):
    """
    Generate detailed mitigation plan for a specific risk.
    
    Args:
        request: Mitigation plan generation request
        
    Returns:
        MitigationPlanResponse: Detailed mitigation plan
    """
    try:
        import uuid
        plan_id = str(uuid.uuid4())
        
        risk_details = request.risk_details
        risk_category = risk_details.get('category', 'unknown')
        risk_score = risk_details.get('risk_score', 0)
        
        # Generate mitigation strategies based on risk type and severity
        mitigation_strategies = []
        
        if risk_category in ['technical', 'integration']:
            mitigation_strategies.extend([
                {
                    'strategy_id': 'TECH-01',
                    'title': 'Technical Risk Reduction',
                    'description': 'Implement proof of concept and technical validation',
                    'effectiveness': 0.8,
                    'cost_estimate': 'Medium',
                    'timeline': '2-4 weeks',
                    'resources_required': ['Senior Technical Architect', 'Development Team']
                },
                {
                    'strategy_id': 'TECH-02',
                    'title': 'Alternative Solution Design',
                    'description': 'Develop backup technical approach',
                    'effectiveness': 0.7,
                    'cost_estimate': 'High',
                    'timeline': '3-6 weeks',
                    'resources_required': ['Solution Architect', 'Research Team']
                }
            ])
        
        if risk_category in ['schedule', 'resource']:
            mitigation_strategies.extend([
                {
                    'strategy_id': 'SCHED-01',
                    'title': 'Schedule Buffer Implementation',
                    'description': 'Add buffer time for critical path activities',
                    'effectiveness': 0.6,
                    'cost_estimate': 'Low',
                    'timeline': '1 week',
                    'resources_required': ['Project Manager']
                },
                {
                    'strategy_id': 'RES-01',
                    'title': 'Resource Augmentation',
                    'description': 'Bring in additional qualified resources',
                    'effectiveness': 0.9,
                    'cost_estimate': 'High',
                    'timeline': '2-3 weeks',
                    'resources_required': ['HR Team', 'Additional Budget']
                }
            ])
        
        if risk_category in ['compliance', 'regulatory']:
            mitigation_strategies.extend([
                {
                    'strategy_id': 'COMP-01',
                    'title': 'Compliance Expert Engagement',
                    'description': 'Engage subject matter experts for compliance guidance',
                    'effectiveness': 0.95,
                    'cost_estimate': 'Medium',
                    'timeline': '1-2 weeks',
                    'resources_required': ['Compliance Expert', 'Legal Review']
                }
            ])
        
        # Default strategies for any risk
        if not mitigation_strategies:
            mitigation_strategies.append({
                'strategy_id': 'GEN-01',
                'title': 'Risk Monitoring and Early Warning',
                'description': 'Implement monitoring system for early risk detection',
                'effectiveness': 0.5,
                'cost_estimate': 'Low',
                'timeline': '1 week',
                'resources_required': ['Risk Manager']
            })
        
        # Generate implementation plan
        implementation_plan = {
            'phases': [
                {
                    'phase_id': 1,
                    'name': 'Planning and Preparation',
                    'duration': '1 week',
                    'activities': [
                        'Finalize mitigation approach',
                        'Secure required resources',
                        'Set up monitoring systems'
                    ]
                },
                {
                    'phase_id': 2,
                    'name': 'Implementation',
                    'duration': '2-4 weeks',
                    'activities': [
                        'Execute primary mitigation strategy',
                        'Monitor progress and effectiveness',
                        'Adjust approach as needed'
                    ]
                },
                {
                    'phase_id': 3,
                    'name': 'Validation and Monitoring',
                    'duration': 'Ongoing',
                    'activities': [
                        'Validate risk reduction',
                        'Continue monitoring',
                        'Report on effectiveness'
                    ]
                }
            ],
            'critical_success_factors': [
                'Executive support and sponsorship',
                'Adequate resource allocation',
                'Clear communication and coordination',
                'Regular progress monitoring'
            ],
            'dependencies': risk_details.get('dependencies', []),
            'constraints': request.constraints or {}
        }
        
        # Define success metrics
        success_metrics = [
            {
                'metric_id': 'RISK-REDUCTION',
                'name': 'Risk Score Reduction',
                'target_value': max(risk_score * 0.3, 1.0),  # Reduce by 70%
                'measurement_method': 'Periodic risk reassessment',
                'frequency': 'Weekly'
            },
            {
                'metric_id': 'IMPLEMENTATION',
                'name': 'Implementation Progress',
                'target_value': 100,
                'measurement_method': 'Milestone completion percentage',
                'frequency': 'Weekly'
            },
            {
                'metric_id': 'EFFECTIVENESS',
                'name': 'Mitigation Effectiveness',
                'target_value': 0.8,
                'measurement_method': 'Stakeholder assessment',
                'frequency': 'Monthly'
            }
        ]
        
        # Estimate costs
        estimated_cost = {
            'total_estimate': 'Medium to High',
            'breakdown': {
                'personnel': 'Medium',
                'technology': 'Low to Medium',
                'external_services': 'Low',
                'contingency': '20% of total'
            },
            'cost_factors': [
                'Complexity of mitigation strategies',
                'Resource availability and rates',
                'Timeline constraints',
                'External dependencies'
            ]
        }
        
        response = MitigationPlanResponse(
            plan_id=plan_id,
            risk_id=request.risk_id,
            mitigation_strategies=mitigation_strategies,
            implementation_plan=implementation_plan,
            success_metrics=success_metrics,
            estimated_cost=estimated_cost
        )
        
        logger.info(f"Mitigation plan generated: {plan_id} for risk {request.risk_id}")
        return response
        
    except Exception as e:
        logger.error(f"Mitigation plan generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")

@router.get("/categories")
async def get_risk_categories():
    """
    Get available risk categories and their descriptions.
    
    Returns:
        dict: Available risk categories
    """
    return {
        "categories": {
            "technical": {
                "description": "Technology implementation and integration risks",
                "examples": ["Architecture complexity", "Technology maturity", "Integration challenges"],
                "typical_mitigation": "Proof of concepts, technical reviews, alternative solutions"
            },
            "schedule": {
                "description": "Timeline and delivery risks",
                "examples": ["Aggressive deadlines", "Resource availability", "Dependencies"],
                "typical_mitigation": "Buffer time, parallel work streams, early starts"
            },
            "resource": {
                "description": "Human and financial resource risks",
                "examples": ["Skill gaps", "Budget constraints", "Team availability"],
                "typical_mitigation": "Staff augmentation, training, budget reallocation"
            },
            "compliance": {
                "description": "Regulatory and compliance risks",
                "examples": ["Certification requirements", "Audit findings", "Policy changes"],
                "typical_mitigation": "Expert consultation, early certification, compliance monitoring"
            },
            "integration": {
                "description": "System and process integration risks",
                "examples": ["Legacy system compatibility", "Data migration", "API changes"],
                "typical_mitigation": "Integration testing, phased rollouts, fallback plans"
            },
            "commercial": {
                "description": "Business and commercial risks",
                "examples": ["Contract terms", "Pricing pressure", "Competitor actions"],
                "typical_mitigation": "Contract negotiation, competitive analysis, value justification"
            },
            "operational": {
                "description": "Operations and maintenance risks",
                "examples": ["Support model", "Performance issues", "Scalability concerns"],
                "typical_mitigation": "Service level agreements, monitoring, capacity planning"
            }
        },
        "severity_levels": {
            "low": {"score_range": "1.0-2.5", "description": "Minor impact, easily managed"},
            "medium": {"score_range": "2.6-4.0", "description": "Moderate impact, requires attention"},
            "high": {"score_range": "4.1-5.5", "description": "Significant impact, active management needed"},
            "critical": {"score_range": "5.6-7.0", "description": "Major impact, immediate action required"}
        }
    }

@router.get("/matrix/{assessment_id}")
async def get_risk_matrix(assessment_id: str):
    """
    Get risk matrix visualization for an assessment.
    
    Args:
        assessment_id: Risk assessment identifier
        
    Returns:
        dict: Risk matrix data for visualization
    """
    try:
        # TODO: Retrieve actual assessment data
        # Mock risk matrix for demonstration
        
        return {
            "assessment_id": assessment_id,
            "matrix": {
                "dimensions": {
                    "probability": {"min": 0, "max": 1, "scale": "0.0-1.0"},
                    "impact": {"min": 0, "max": 7, "scale": "1-7"}
                },
                "zones": {
                    "low": {"color": "green", "range": "1.0-2.5"},
                    "medium": {"color": "yellow", "range": "2.6-4.0"},
                    "high": {"color": "orange", "range": "4.1-5.5"},
                    "critical": {"color": "red", "range": "5.6-7.0"}
                },
                "risks": [
                    {
                        "id": "RISK-001",
                        "title": "Technical Integration Risk",
                        "probability": 0.6,
                        "impact": 5,
                        "risk_score": 3.0,
                        "zone": "medium"
                    },
                    {
                        "id": "RISK-002", 
                        "title": "Schedule Risk",
                        "probability": 0.8,
                        "impact": 6,
                        "risk_score": 4.8,
                        "zone": "high"
                    }
                ]
            },
            "summary": {
                "total_risks": 2,
                "by_zone": {
                    "low": 0,
                    "medium": 1,
                    "high": 1,
                    "critical": 0
                },
                "average_score": 3.9,
                "highest_risk": "RISK-002"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get risk matrix: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get risk matrix: {str(e)}")
