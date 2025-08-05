"""
Risk Assessment Agent for comprehensive project and proposal risk analysis.

This agent specializes in identifying, analyzing, and categorizing risks
associated with RFP opportunities and project requirements.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

from .base_agent import BaseAgent
from ..prompts.analysis_prompts import AnalysisPrompts

logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """Enumeration of risk categories."""
    TECHNICAL = "technical"
    SCHEDULE = "schedule"
    COMMERCIAL = "commercial"
    COMPETITIVE = "competitive"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    RESOURCE = "resource"
    EXTERNAL = "external"


class RiskProbability(Enum):
    """Enumeration of risk probability levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RiskImpact(Enum):
    """Enumeration of risk impact levels."""
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Risk:
    """Data class representing a single risk."""
    id: str
    title: str
    description: str
    category: RiskCategory
    probability: RiskProbability
    impact: RiskImpact
    risk_score: float
    mitigation_strategies: List[str]
    contingency_plans: List[str]
    owner: Optional[str] = None
    timeline: Optional[str] = None
    dependencies: Optional[List[str]] = None
    early_warning_signs: Optional[List[str]] = None
    cost_impact: Optional[float] = None
    schedule_impact: Optional[int] = None  # days
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.early_warning_signs is None:
            self.early_warning_signs = []


@dataclass
class RiskMatrix:
    """Risk assessment matrix with categorization and prioritization."""
    critical_risks: List[Risk]
    high_risks: List[Risk]
    medium_risks: List[Risk]
    low_risks: List[Risk]
    overall_risk_score: float
    risk_distribution: Dict[str, int]
    recommendations: List[str]


class RiskAssessmentAgent(BaseAgent):
    """
    Specialized agent for comprehensive risk assessment and analysis.
    
    Capabilities:
    - Multi-dimensional risk identification and analysis
    - Risk categorization and prioritization
    - Mitigation strategy development
    - Contingency planning recommendations
    - Risk matrix generation and visualization
    - Timeline and cost impact assessment
    - Monte Carlo risk simulations
    - Risk register management
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        super().__init__(ai_client)
        
        self.risk_indicators = {
            'technical': [
                'new technology', 'unproven', 'complex integration', 'legacy system',
                'scalability', 'performance requirements', 'technical debt',
                'third-party dependency', 'api limitations', 'data migration'
            ],
            'schedule': [
                'tight deadline', 'aggressive timeline', 'concurrent tasks',
                'resource availability', 'dependencies', 'critical path',
                'milestone', 'delivery date', 'compressed schedule'
            ],
            'commercial': [
                'budget constraint', 'cost overrun', 'payment terms',
                'contract penalty', 'price volatility', 'vendor risk',
                'economic conditions', 'currency fluctuation'
            ],
            'competitive': [
                'incumbent advantage', 'competitive pressure', 'market leader',
                'price competition', 'evaluation bias', 'relationship advantage',
                'past performance', 'brand recognition'
            ],
            'compliance': [
                'regulation', 'audit requirement', 'certification needed',
                'security clearance', 'standard compliance', 'legal requirement',
                'privacy regulation', 'industry standard'
            ],
            'operational': [
                'resource constraint', 'skill gap', 'training required',
                'organizational change', 'process maturity', 'capacity limitation',
                'quality assurance', 'support capability'
            ]
        }
        
        self.probability_matrix = {
            'very_low': 0.1,
            'low': 0.3,
            'medium': 0.5,
            'high': 0.7,
            'very_high': 0.9
        }
        
        self.impact_matrix = {
            'negligible': 1,
            'low': 2,
            'medium': 3,
            'high': 4,
            'critical': 5
        }
    
    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process risk assessment request.
        
        Args:
            inputs: Dictionary containing:
                - document_content: RFP or project document content
                - requirements: List of extracted requirements
                - project_context: Additional project information
                - assessment_depth: 'basic', 'detailed', or 'comprehensive'
                - focus_areas: List of risk categories to focus on
                - include_quantitative: Boolean for quantitative analysis
        
        Returns:
            Dictionary containing comprehensive risk assessment
        """
        try:
            document_content = inputs.get('document_content', '')
            requirements = inputs.get('requirements', [])
            project_context = inputs.get('project_context', {})
            assessment_depth = inputs.get('assessment_depth', 'detailed')
            focus_areas = inputs.get('focus_areas', [])
            include_quantitative = inputs.get('include_quantitative', True)
            
            logger.info(f"Starting risk assessment with {assessment_depth} depth")
            
            assessment_result = {
                'assessment_metadata': {
                    'depth': assessment_depth,
                    'timestamp': str(asyncio.get_event_loop().time()),
                    'agent_version': '1.0.0',
                    'focus_areas': focus_areas
                },
                'identified_risks': [],
                'risk_matrix': {},
                'risk_analysis': {},
                'mitigation_recommendations': [],
                'contingency_planning': {}
            }
            
            # Identify risks based on assessment depth
            if assessment_depth == 'basic':
                assessment_result.update(await self._basic_risk_identification(document_content))
            elif assessment_depth == 'detailed':
                assessment_result.update(await self._detailed_risk_assessment(
                    document_content, requirements, project_context
                ))
            else:  # comprehensive
                assessment_result.update(await self._comprehensive_risk_assessment(
                    document_content, requirements, project_context, focus_areas
                ))
            
            # Generate risk matrix
            if assessment_result['identified_risks']:
                assessment_result['risk_matrix'] = await self._generate_risk_matrix(
                    assessment_result['identified_risks']
                )
                
                # Quantitative analysis
                if include_quantitative and assessment_depth == 'comprehensive':
                    assessment_result['quantitative_analysis'] = await self._quantitative_risk_analysis(
                        assessment_result['identified_risks']
                    )
                
                # Generate mitigation strategies
                assessment_result['mitigation_recommendations'] = await self._generate_mitigation_strategies(
                    assessment_result['identified_risks']
                )
                
                # Contingency planning
                assessment_result['contingency_planning'] = await self._develop_contingency_plans(
                    assessment_result['identified_risks']
                )
                
                # Risk monitoring plan
                assessment_result['monitoring_plan'] = await self._create_risk_monitoring_plan(
                    assessment_result['identified_risks']
                )
            
            logger.info(f"Risk assessment completed: {len(assessment_result['identified_risks'])} risks identified")
            return assessment_result
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            return await self._fallback_risk_assessment(inputs)
    
    async def _basic_risk_identification(self, content: str) -> Dict[str, Any]:
        """Perform basic risk identification using pattern matching."""
        risks = []
        risk_counter = 1
        
        # Pattern-based risk identification
        for category, indicators in self.risk_indicators.items():
            category_enum = RiskCategory(category)
            
            for indicator in indicators:
                if indicator.lower() in content.lower():
                    risk = Risk(
                        id=f"RISK-{risk_counter:03d}",
                        title=f"{category.title()} Risk: {indicator.title()}",
                        description=f"Potential {category} risk identified: {indicator}",
                        category=category_enum,
                        probability=RiskProbability.MEDIUM,
                        impact=RiskImpact.MEDIUM,
                        risk_score=self._calculate_risk_score(RiskProbability.MEDIUM, RiskImpact.MEDIUM),
                        mitigation_strategies=[f"Address {indicator} through proper planning"],
                        contingency_plans=[f"Develop fallback plan for {indicator}"]
                    )
                    risks.append(risk)
                    risk_counter += 1
        
        return {
            'identified_risks': [asdict(risk) for risk in risks],
            'assessment_method': 'basic_pattern_matching'
        }
    
    async def _detailed_risk_assessment(self, content: str, requirements: List[Dict], 
                                      project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed risk assessment with requirement analysis."""
        risks = []
        
        # Pattern-based identification
        basic_result = await self._basic_risk_identification(content)
        pattern_risks = [Risk(**{k: v for k, v in risk.items() if k != 'dependencies' and k != 'early_warning_signs'}) 
                        for risk in basic_result['identified_risks']]
        
        # Requirement-based risk analysis
        requirement_risks = await self._analyze_requirement_risks(requirements)
        
        # Context-based risk analysis
        context_risks = await self._analyze_context_risks(project_context)
        
        # Combine and deduplicate risks
        all_risks = pattern_risks + requirement_risks + context_risks
        unique_risks = self._deduplicate_risks(all_risks)
        
        # Enhanced risk scoring
        for risk in unique_risks:
            risk.risk_score = self._calculate_enhanced_risk_score(risk, content, requirements)
            risk.early_warning_signs = self._identify_early_warning_signs(risk)
        
        return {
            'identified_risks': [asdict(risk) for risk in unique_risks],
            'assessment_method': 'detailed_analysis',
            'risk_sources': {
                'pattern_based': len(pattern_risks),
                'requirement_based': len(requirement_risks),
                'context_based': len(context_risks),
                'unique_risks': len(unique_risks)
            }
        }
    
    async def _comprehensive_risk_assessment(self, content: str, requirements: List[Dict],
                                           project_context: Dict[str, Any], 
                                           focus_areas: List[str]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment with AI analysis."""
        # Start with detailed assessment
        detailed_result = await self._detailed_risk_assessment(content, requirements, project_context)
        
        # AI-powered risk analysis if available
        if self.ai_client:
            ai_risks = await self._ai_risk_analysis(content, requirements, focus_areas)
            
            # Merge AI and pattern-based risks
            existing_risks = [Risk(**{k: v for k, v in risk.items() if k != 'dependencies' and k != 'early_warning_signs'}) 
                            for risk in detailed_result['identified_risks']]
            all_risks = existing_risks + ai_risks
            comprehensive_risks = self._deduplicate_risks(all_risks)
        else:
            comprehensive_risks = [Risk(**{k: v for k, v in risk.items() if k != 'dependencies' and k != 'early_warning_signs'}) 
                                 for risk in detailed_result['identified_risks']]
        
        # Advanced risk analysis
        for risk in comprehensive_risks:
            # Enhanced scoring with multiple factors
            risk.risk_score = self._calculate_comprehensive_risk_score(risk, content, requirements, project_context)
            
            # Timeline impact analysis
            risk.timeline = self._estimate_risk_timeline(risk)
            
            # Cost impact analysis
            risk.cost_impact = self._estimate_cost_impact(risk, project_context)
            
            # Schedule impact analysis
            risk.schedule_impact = self._estimate_schedule_impact(risk)
            
            # Risk dependencies
            risk.dependencies = self._identify_risk_dependencies(risk, comprehensive_risks)
        
        return {
            'identified_risks': [asdict(risk) for risk in comprehensive_risks],
            'assessment_method': 'comprehensive_ai_enhanced',
            'analysis_depth': 'comprehensive',
            'ai_enhanced': self.ai_client is not None
        }
    
    async def _ai_risk_analysis(self, content: str, requirements: List[Dict], 
                              focus_areas: List[str]) -> List[Risk]:
        """Perform AI-powered risk analysis."""
        try:
            # Prepare context for AI analysis
            requirements_text = '\n'.join([
                f"- {req.get('text', '')}" for req in requirements[:20]  # Limit for API
            ])
            
            focus_text = ', '.join(focus_areas) if focus_areas else 'all risk categories'
            
            risk_prompt = f"""Analyze this RFP and requirements for risks focusing on: {focus_text}

RFP Content:
{content[:3000]}...

Key Requirements:
{requirements_text}

Identify and analyze risks in these categories:
1. Technical risks (integration, scalability, complexity)
2. Schedule risks (timelines, dependencies, resources)
3. Commercial risks (budget, costs, contract terms)
4. Competitive risks (competition, differentiation)
5. Compliance risks (regulations, standards)
6. Operational risks (resources, capabilities)

For each risk, provide:
- Risk title and description
- Category (technical/schedule/commercial/competitive/compliance/operational)
- Probability (very_low/low/medium/high/very_high)
- Impact (negligible/low/medium/high/critical)
- Specific mitigation strategies
- Early warning indicators

Format as JSON array of risk objects."""

            system_prompt = "You are an expert risk analyst specializing in project and proposal risk assessment. Provide detailed, actionable risk analysis."
            
            response = await self.ai_client.generate(
                system_prompt=system_prompt,
                user_prompt=risk_prompt
            )
            
            # Parse AI response
            try:
                ai_risks_data = json.loads(response)
                if isinstance(ai_risks_data, dict) and 'risks' in ai_risks_data:
                    ai_risks_data = ai_risks_data['risks']
                
                ai_risks = []
                for i, risk_data in enumerate(ai_risks_data):
                    risk = Risk(
                        id=f"AI-RISK-{i+1:03d}",
                        title=risk_data.get('title', f'AI Identified Risk {i+1}'),
                        description=risk_data.get('description', ''),
                        category=RiskCategory(risk_data.get('category', 'technical')),
                        probability=RiskProbability(risk_data.get('probability', 'medium')),
                        impact=RiskImpact(risk_data.get('impact', 'medium')),
                        risk_score=0.0,  # Will be calculated later
                        mitigation_strategies=risk_data.get('mitigation_strategies', []),
                        contingency_plans=risk_data.get('contingency_plans', []),
                        early_warning_signs=risk_data.get('early_warning_signs', [])
                    )
                    ai_risks.append(risk)
                
                return ai_risks
                
            except json.JSONDecodeError:
                logger.warning("AI risk analysis response was not valid JSON")
                return []
            
        except Exception as e:
            logger.error(f"AI risk analysis failed: {str(e)}")
            return []
    
    async def _analyze_requirement_risks(self, requirements: List[Dict]) -> List[Risk]:
        """Analyze risks based on extracted requirements."""
        risks = []
        risk_counter = 1
        
        for req in requirements:
            req_text = req.get('text', '').lower()
            req_complexity = req.get('complexity', 'medium')
            req_priority = req.get('priority', 'important')
            
            # High complexity requirements carry inherent risk
            if req_complexity in ['high', 'critical']:
                risk = Risk(
                    id=f"REQ-RISK-{risk_counter:03d}",
                    title=f"High Complexity Requirement Risk",
                    description=f"Complex requirement may pose implementation challenges: {req['text'][:100]}...",
                    category=RiskCategory.TECHNICAL,
                    probability=RiskProbability.MEDIUM,
                    impact=RiskImpact.HIGH if req_priority == 'mandatory' else RiskImpact.MEDIUM,
                    risk_score=0.0,  # Will be calculated
                    mitigation_strategies=[
                        "Break down complex requirement into smaller components",
                        "Conduct proof-of-concept development",
                        "Allocate additional development resources"
                    ],
                    contingency_plans=[
                        "Develop alternative implementation approach",
                        "Negotiate requirement modification if necessary"
                    ]
                )
                risks.append(risk)
                risk_counter += 1
            
            # Security requirements carry compliance risk
            if any(keyword in req_text for keyword in ['security', 'authentication', 'encryption']):
                risk = Risk(
                    id=f"SEC-RISK-{risk_counter:03d}",
                    title="Security Compliance Risk",
                    description=f"Security requirement may require specialized compliance: {req['text'][:100]}...",
                    category=RiskCategory.COMPLIANCE,
                    probability=RiskProbability.MEDIUM,
                    impact=RiskImpact.HIGH,
                    risk_score=0.0,
                    mitigation_strategies=[
                        "Engage security compliance experts",
                        "Conduct security audit early in development",
                        "Plan for additional certification time"
                    ],
                    contingency_plans=[
                        "Partner with certified security vendor",
                        "Leverage existing certified components"
                    ]
                )
                risks.append(risk)
                risk_counter += 1
        
        return risks
    
    async def _analyze_context_risks(self, project_context: Dict[str, Any]) -> List[Risk]:
        """Analyze risks based on project context."""
        risks = []
        risk_counter = 1
        
        # Budget constraints
        budget = project_context.get('budget')
        if budget and budget.get('is_constrained', False):
            risk = Risk(
                id=f"CTX-RISK-{risk_counter:03d}",
                title="Budget Constraint Risk",
                description="Limited budget may impact solution quality or scope",
                category=RiskCategory.COMMERCIAL,
                probability=RiskProbability.HIGH,
                impact=RiskImpact.MEDIUM,
                risk_score=0.0,
                mitigation_strategies=[
                    "Prioritize features based on value",
                    "Consider phased implementation",
                    "Negotiate budget flexibility"
                ],
                contingency_plans=[
                    "Reduce scope to essential features",
                    "Seek additional funding sources"
                ]
            )
            risks.append(risk)
            risk_counter += 1
        
        # Timeline constraints
        timeline = project_context.get('timeline')
        if timeline and timeline.get('is_aggressive', False):
            risk = Risk(
                id=f"CTX-RISK-{risk_counter:03d}",
                title="Aggressive Timeline Risk",
                description="Tight schedule may impact quality or require additional resources",
                category=RiskCategory.SCHEDULE,
                probability=RiskProbability.HIGH,
                impact=RiskImpact.HIGH,
                risk_score=0.0,
                mitigation_strategies=[
                    "Allocate additional resources",
                    "Plan for parallel development tracks",
                    "Implement agile development methodology"
                ],
                contingency_plans=[
                    "Negotiate timeline extension",
                    "Reduce initial scope for faster delivery"
                ]
            )
            risks.append(risk)
            risk_counter += 1
        
        # Resource availability
        resources = project_context.get('resources')
        if resources and resources.get('availability', 'adequate') == 'limited':
            risk = Risk(
                id=f"CTX-RISK-{risk_counter:03d}",
                title="Resource Availability Risk",
                description="Limited resource availability may delay project delivery",
                category=RiskCategory.RESOURCE,
                probability=RiskProbability.MEDIUM,
                impact=RiskImpact.MEDIUM,
                risk_score=0.0,
                mitigation_strategies=[
                    "Plan resource allocation carefully",
                    "Cross-train team members",
                    "Consider external contractor support"
                ],
                contingency_plans=[
                    "Adjust project timeline based on resource availability",
                    "Prioritize critical path activities"
                ]
            )
            risks.append(risk)
            risk_counter += 1
        
        return risks
    
    async def _generate_risk_matrix(self, risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate risk assessment matrix."""
        matrix = {
            'critical_risks': [],
            'high_risks': [],
            'medium_risks': [],
            'low_risks': [],
            'risk_distribution': {},
            'category_breakdown': {},
            'overall_metrics': {}
        }
        
        # Categorize risks by score
        for risk in risks:
            risk_score = risk.get('risk_score', 0)
            
            if risk_score >= 4.0:
                matrix['critical_risks'].append(risk)
            elif risk_score >= 3.0:
                matrix['high_risks'].append(risk)
            elif risk_score >= 2.0:
                matrix['medium_risks'].append(risk)
            else:
                matrix['low_risks'].append(risk)
        
        # Risk distribution
        matrix['risk_distribution'] = {
            'critical': len(matrix['critical_risks']),
            'high': len(matrix['high_risks']),
            'medium': len(matrix['medium_risks']),
            'low': len(matrix['low_risks'])
        }
        
        # Category breakdown
        category_counts = {}
        for risk in risks:
            category = risk.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        matrix['category_breakdown'] = category_counts
        
        # Overall metrics
        if risks:
            total_risks = len(risks)
            avg_risk_score = sum(risk.get('risk_score', 0) for risk in risks) / total_risks
            high_risk_percentage = (len(matrix['critical_risks']) + len(matrix['high_risks'])) / total_risks * 100
            
            matrix['overall_metrics'] = {
                'total_risks': total_risks,
                'average_risk_score': round(avg_risk_score, 2),
                'high_risk_percentage': round(high_risk_percentage, 1),
                'risk_level': self._assess_overall_risk_level(avg_risk_score, high_risk_percentage)
            }
        
        return matrix
    
    async def _quantitative_risk_analysis(self, risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform quantitative risk analysis including Monte Carlo simulation."""
        analysis = {
            'cost_impact_analysis': {},
            'schedule_impact_analysis': {},
            'monte_carlo_simulation': {},
            'risk_exposure': {}
        }
        
        # Cost impact analysis
        total_cost_impact = 0
        cost_risks = [r for r in risks if r.get('cost_impact')]
        
        if cost_risks:
            for risk in cost_risks:
                probability = self.probability_matrix.get(risk.get('probability', 'medium'), 0.5)
                cost_impact = risk.get('cost_impact', 0)
                expected_cost = probability * cost_impact
                total_cost_impact += expected_cost
            
            analysis['cost_impact_analysis'] = {
                'total_expected_cost_impact': round(total_cost_impact, 2),
                'cost_at_risk_p90': round(total_cost_impact * 1.5, 2),  # Simplified P90
                'number_of_cost_risks': len(cost_risks)
            }
        
        # Schedule impact analysis
        total_schedule_impact = 0
        schedule_risks = [r for r in risks if r.get('schedule_impact')]
        
        if schedule_risks:
            for risk in schedule_risks:
                probability = self.probability_matrix.get(risk.get('probability', 'medium'), 0.5)
                schedule_impact = risk.get('schedule_impact', 0)
                expected_delay = probability * schedule_impact
                total_schedule_impact += expected_delay
            
            analysis['schedule_impact_analysis'] = {
                'total_expected_delay_days': round(total_schedule_impact, 1),
                'schedule_at_risk_p90': round(total_schedule_impact * 1.5, 1),
                'number_of_schedule_risks': len(schedule_risks)
            }
        
        # Simplified Monte Carlo simulation
        analysis['monte_carlo_simulation'] = await self._simple_monte_carlo(risks)
        
        # Risk exposure calculation
        total_exposure = 0
        for risk in risks:
            probability = self.probability_matrix.get(risk.get('probability', 'medium'), 0.5)
            impact_score = self.impact_matrix.get(risk.get('impact', 'medium'), 3)
            exposure = probability * impact_score
            total_exposure += exposure
        
        analysis['risk_exposure'] = {
            'total_risk_exposure': round(total_exposure, 2),
            'average_risk_exposure': round(total_exposure / max(len(risks), 1), 2),
            'exposure_level': self._assess_exposure_level(total_exposure, len(risks))
        }
        
        return analysis
    
    async def _simple_monte_carlo(self, risks: List[Dict[str, Any]], iterations: int = 1000) -> Dict[str, Any]:
        """Perform simplified Monte Carlo simulation for risk analysis."""
        import random
        
        simulation_results = []
        
        for _ in range(iterations):
            iteration_impact = 0
            
            for risk in risks:
                probability = self.probability_matrix.get(risk.get('probability', 'medium'), 0.5)
                impact_score = self.impact_matrix.get(risk.get('impact', 'medium'), 3)
                
                # Random occurrence based on probability
                if random.random() < probability:
                    iteration_impact += impact_score * random.uniform(0.5, 1.5)  # Add variability
            
            simulation_results.append(iteration_impact)
        
        # Calculate statistics
        simulation_results.sort()
        n = len(simulation_results)
        
        return {
            'mean_impact': round(sum(simulation_results) / n, 2),
            'p50_impact': round(simulation_results[n // 2], 2),
            'p90_impact': round(simulation_results[int(n * 0.9)], 2),
            'p95_impact': round(simulation_results[int(n * 0.95)], 2),
            'max_impact': round(max(simulation_results), 2),
            'iterations': iterations
        }
    
    async def _generate_mitigation_strategies(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate comprehensive mitigation strategies for identified risks."""
        mitigation_recommendations = []
        
        # Group risks by category for strategic planning
        risk_categories = {}
        for risk in risks:
            category = risk.get('category', 'unknown')
            if category not in risk_categories:
                risk_categories[category] = []
            risk_categories[category].append(risk)
        
        # Generate category-specific strategies
        for category, category_risks in risk_categories.items():
            high_impact_risks = [r for r in category_risks if r.get('risk_score', 0) >= 3.0]
            
            if high_impact_risks:
                strategy = {
                    'category': category,
                    'risk_count': len(category_risks),
                    'high_impact_count': len(high_impact_risks),
                    'strategic_approaches': self._get_category_strategies(category),
                    'priority_actions': [],
                    'resource_requirements': self._estimate_mitigation_resources(category_risks)
                }
                
                # Extract priority actions from high-impact risks
                for risk in high_impact_risks[:3]:  # Top 3 high-impact risks
                    strategy['priority_actions'].extend(
                        risk.get('mitigation_strategies', [])[:2]  # Top 2 strategies per risk
                    )
                
                mitigation_recommendations.append(strategy)
        
        # Add cross-cutting recommendations
        mitigation_recommendations.append({
            'category': 'cross_cutting',
            'strategic_approaches': [
                'Establish regular risk monitoring and review processes',
                'Implement risk escalation procedures',
                'Create risk communication plan for stakeholders',
                'Develop risk response team with clear responsibilities'
            ],
            'priority_actions': [
                'Schedule weekly risk review meetings',
                'Create risk dashboard for real-time monitoring',
                'Establish risk thresholds for escalation'
            ]
        })
        
        return mitigation_recommendations
    
    async def _develop_contingency_plans(self, risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Develop contingency plans for high-impact risks."""
        contingency_planning = {
            'critical_risk_plans': [],
            'scenario_planning': {},
            'resource_reserves': {},
            'escalation_procedures': {}
        }
        
        # Identify critical risks requiring contingency plans
        critical_risks = [r for r in risks if r.get('risk_score', 0) >= 4.0]
        
        for risk in critical_risks:
            contingency_plan = {
                'risk_id': risk.get('id'),
                'risk_title': risk.get('title'),
                'trigger_conditions': self._define_trigger_conditions(risk),
                'response_actions': risk.get('contingency_plans', []),
                'resource_requirements': self._estimate_contingency_resources(risk),
                'decision_authority': self._assign_decision_authority(risk),
                'communication_plan': self._create_communication_plan(risk)
            }
            contingency_planning['critical_risk_plans'].append(contingency_plan)
        
        # Scenario planning
        contingency_planning['scenario_planning'] = {
            'best_case': 'Few risks materialize, project proceeds smoothly',
            'most_likely': 'Some medium risks occur, manageable with standard mitigation',
            'worst_case': 'Multiple high-impact risks materialize simultaneously',
            'contingency_budget': self._calculate_contingency_budget(risks)
        }
        
        return contingency_planning
    
    async def _create_risk_monitoring_plan(self, risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive risk monitoring and reporting plan."""
        monitoring_plan = {
            'monitoring_frequency': {},
            'key_risk_indicators': [],
            'reporting_structure': {},
            'review_schedule': {}
        }
        
        # Define monitoring frequency by risk level
        monitoring_plan['monitoring_frequency'] = {
            'critical_risks': 'Daily',
            'high_risks': 'Weekly',
            'medium_risks': 'Bi-weekly',
            'low_risks': 'Monthly'
        }
        
        # Extract key risk indicators
        for risk in risks:
            if risk.get('risk_score', 0) >= 3.0:  # High and critical risks
                kris = []
                
                # Add early warning signs as KRIs
                early_warnings = risk.get('early_warning_signs', [])
                for warning in early_warnings:
                    kris.append({
                        'risk_id': risk.get('id'),
                        'indicator': warning,
                        'measurement': 'Qualitative assessment',
                        'threshold': 'Any occurrence',
                        'frequency': 'Weekly'
                    })
                
                monitoring_plan['key_risk_indicators'].extend(kris)
        
        # Reporting structure
        monitoring_plan['reporting_structure'] = {
            'risk_dashboard': 'Real-time risk status visualization',
            'weekly_reports': 'Risk status summary for project team',
            'monthly_reports': 'Comprehensive risk analysis for stakeholders',
            'escalation_reports': 'Immediate notification for critical risk events'
        }
        
        return monitoring_plan
    
    # Helper methods
    def _calculate_risk_score(self, probability: RiskProbability, impact: RiskImpact) -> float:
        """Calculate basic risk score."""
        prob_value = self.probability_matrix.get(probability.value, 0.5)
        impact_value = self.impact_matrix.get(impact.value, 3)
        return prob_value * impact_value
    
    def _calculate_enhanced_risk_score(self, risk: Risk, content: str, requirements: List[Dict]) -> float:
        """Calculate enhanced risk score with additional factors."""
        base_score = self._calculate_risk_score(risk.probability, risk.impact)
        
        # Adjust based on context
        adjustment_factor = 1.0
        
        # High complexity requirements increase risk
        if risk.category == RiskCategory.TECHNICAL:
            high_complexity_count = len([r for r in requirements if r.get('complexity') in ['high', 'critical']])
            if high_complexity_count > len(requirements) * 0.3:
                adjustment_factor += 0.2
        
        # Aggressive timelines increase schedule risk
        if risk.category == RiskCategory.SCHEDULE:
            if any(keyword in content.lower() for keyword in ['tight', 'aggressive', 'immediate']):
                adjustment_factor += 0.3
        
        return min(base_score * adjustment_factor, 5.0)  # Cap at 5.0
    
    def _calculate_comprehensive_risk_score(self, risk: Risk, content: str, 
                                          requirements: List[Dict], project_context: Dict) -> float:
        """Calculate comprehensive risk score with multiple factors."""
        enhanced_score = self._calculate_enhanced_risk_score(risk, content, requirements)
        
        # Additional adjustments based on project context
        context_factor = 1.0
        
        # Budget constraints
        if project_context.get('budget', {}).get('is_constrained') and risk.category == RiskCategory.COMMERCIAL:
            context_factor += 0.2
        
        # Resource limitations
        if project_context.get('resources', {}).get('availability') == 'limited':
            context_factor += 0.15
        
        # Regulatory environment
        if project_context.get('regulatory_complexity', 'low') == 'high' and risk.category == RiskCategory.COMPLIANCE:
            context_factor += 0.25
        
        return min(enhanced_score * context_factor, 5.0)
    
    def _deduplicate_risks(self, risks: List[Risk]) -> List[Risk]:
        """Remove duplicate risks based on similarity."""
        unique_risks = []
        seen_risks = set()
        
        for risk in risks:
            # Create a normalized identifier
            risk_key = f"{risk.category.value}_{risk.title.lower().replace(' ', '_')}"
            
            if risk_key not in seen_risks:
                seen_risks.add(risk_key)
                unique_risks.append(risk)
        
        return unique_risks
    
    def _identify_early_warning_signs(self, risk: Risk) -> List[str]:
        """Identify early warning signs for a risk."""
        category = risk.category
        
        warning_signs = {
            RiskCategory.TECHNICAL: [
                'Integration test failures',
                'Performance benchmark misses',
                'Third-party API changes',
                'Architecture review concerns'
            ],
            RiskCategory.SCHEDULE: [
                'Milestone delays',
                'Resource unavailability',
                'Dependency bottlenecks',
                'Scope creep requests'
            ],
            RiskCategory.COMMERCIAL: [
                'Budget variance reports',
                'Cost escalation notices',
                'Contract negotiation delays',
                'Vendor pricing changes'
            ],
            RiskCategory.COMPETITIVE: [
                'Competitor announcements',
                'Market share changes',
                'Customer feedback shifts',
                'Pricing pressure indicators'
            ],
            RiskCategory.COMPLIANCE: [
                'Regulation updates',
                'Audit findings',
                'Certification delays',
                'Standard changes'
            ]
        }
        
        return warning_signs.get(category, [
            'Stakeholder concerns raised',
            'Quality metrics declining',
            'Team stress indicators'
        ])
    
    def _estimate_risk_timeline(self, risk: Risk) -> str:
        """Estimate when risk might materialize."""
        if risk.category == RiskCategory.SCHEDULE:
            return 'Throughout project duration'
        elif risk.category == RiskCategory.TECHNICAL:
            return 'Development and testing phases'
        elif risk.category == RiskCategory.COMMERCIAL:
            return 'Contract negotiation and project execution'
        elif risk.category == RiskCategory.COMPLIANCE:
            return 'Design, development, and audit phases'
        else:
            return 'Project execution phase'
    
    def _estimate_cost_impact(self, risk: Risk, project_context: Dict) -> Optional[float]:
        """Estimate potential cost impact of risk."""
        base_budget = project_context.get('budget', {}).get('total', 1000000)  # Default $1M
        
        impact_percentages = {
            RiskImpact.NEGLIGIBLE: 0.01,
            RiskImpact.LOW: 0.05,
            RiskImpact.MEDIUM: 0.15,
            RiskImpact.HIGH: 0.30,
            RiskImpact.CRITICAL: 0.50
        }
        
        impact_percentage = impact_percentages.get(risk.impact, 0.15)
        return base_budget * impact_percentage
    
    def _estimate_schedule_impact(self, risk: Risk) -> Optional[int]:
        """Estimate potential schedule impact in days."""
        impact_days = {
            RiskImpact.NEGLIGIBLE: 1,
            RiskImpact.LOW: 5,
            RiskImpact.MEDIUM: 15,
            RiskImpact.HIGH: 30,
            RiskImpact.CRITICAL: 60
        }
        
        return impact_days.get(risk.impact, 15)
    
    def _identify_risk_dependencies(self, risk: Risk, all_risks: List[Risk]) -> List[str]:
        """Identify dependencies between risks."""
        dependencies = []
        
        # Simple dependency identification based on category relationships
        if risk.category == RiskCategory.TECHNICAL:
            # Technical risks may depend on schedule risks
            schedule_risks = [r for r in all_risks if r.category == RiskCategory.SCHEDULE]
            if schedule_risks:
                dependencies.extend([r.id for r in schedule_risks[:2]])  # Top 2
        
        elif risk.category == RiskCategory.COMMERCIAL:
            # Commercial risks may depend on competitive risks
            competitive_risks = [r for r in all_risks if r.category == RiskCategory.COMPETITIVE]
            if competitive_risks:
                dependencies.extend([r.id for r in competitive_risks[:1]])  # Top 1
        
        return dependencies
    
    def _assess_overall_risk_level(self, avg_score: float, high_risk_percentage: float) -> str:
        """Assess overall risk level for the project."""
        if avg_score >= 3.5 or high_risk_percentage >= 40:
            return 'Critical'
        elif avg_score >= 2.5 or high_risk_percentage >= 25:
            return 'High'
        elif avg_score >= 1.5 or high_risk_percentage >= 15:
            return 'Medium'
        else:
            return 'Low'
    
    def _assess_exposure_level(self, total_exposure: float, risk_count: int) -> str:
        """Assess risk exposure level."""
        avg_exposure = total_exposure / max(risk_count, 1)
        
        if avg_exposure >= 3.0:
            return 'Very High'
        elif avg_exposure >= 2.0:
            return 'High'
        elif avg_exposure >= 1.0:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_category_strategies(self, category: str) -> List[str]:
        """Get strategic approaches for risk category."""
        strategies = {
            'technical': [
                'Conduct early proof-of-concept development',
                'Implement robust testing and validation processes',
                'Plan for technical architecture reviews',
                'Establish fallback technical solutions'
            ],
            'schedule': [
                'Build schedule buffers for critical path items',
                'Implement agile project management practices',
                'Plan for resource augmentation if needed',
                'Establish milestone review and adjustment processes'
            ],
            'commercial': [
                'Negotiate favorable contract terms and conditions',
                'Establish cost monitoring and control processes',
                'Plan for budget contingencies',
                'Diversify vendor and supplier relationships'
            ],
            'competitive': [
                'Develop unique value propositions and differentiators',
                'Monitor competitive landscape continuously',
                'Build strong customer relationships',
                'Focus on solution quality and innovation'
            ],
            'compliance': [
                'Engage compliance experts early in project',
                'Plan for regulatory review and approval cycles',
                'Establish audit trail and documentation processes',
                'Monitor regulatory changes and updates'
            ]
        }
        
        return strategies.get(category, [
            'Regular monitoring and review processes',
            'Stakeholder communication and engagement',
            'Proactive risk management practices'
        ])
    
    def _estimate_mitigation_resources(self, risks: List[Dict]) -> Dict[str, Any]:
        """Estimate resources needed for risk mitigation."""
        return {
            'additional_budget': f"{len(risks) * 5000:,}",  # $5K per risk
            'additional_time': f"{len(risks) * 2} days",
            'specialist_skills': 'Risk management, domain expertise',
            'management_attention': 'Medium to High'
        }
    
    def _define_trigger_conditions(self, risk: Dict) -> List[str]:
        """Define trigger conditions for contingency plan activation."""
        return [
            f"Risk probability exceeds 70%",
            f"Early warning signs detected",
            f"Impact assessment confirms {risk.get('impact', 'medium')} level",
            f"Mitigation strategies prove insufficient"
        ]
    
    def _estimate_contingency_resources(self, risk: Dict) -> Dict[str, Any]:
        """Estimate resources needed for contingency response."""
        return {
            'budget_reserve': f"${risk.get('cost_impact', 50000):,.0f}",
            'time_reserve': f"{risk.get('schedule_impact', 14)} days",
            'team_augmentation': 'As needed based on risk category'
        }
    
    def _assign_decision_authority(self, risk: Dict) -> str:
        """Assign decision authority for contingency plan execution."""
        risk_score = risk.get('risk_score', 0)
        
        if risk_score >= 4.0:
            return 'Executive Sponsor'
        elif risk_score >= 3.0:
            return 'Project Manager'
        else:
            return 'Team Lead'
    
    def _create_communication_plan(self, risk: Dict) -> Dict[str, str]:
        """Create communication plan for risk contingency."""
        return {
            'immediate_notification': 'Project team, key stakeholders',
            'detailed_briefing': 'Executive sponsor, client representative',
            'regular_updates': 'Weekly status reports, risk dashboard',
            'resolution_communication': 'All stakeholders, lessons learned'
        }
    
    def _calculate_contingency_budget(self, risks: List[Dict]) -> Dict[str, Any]:
        """Calculate recommended contingency budget."""
        high_impact_risks = [r for r in risks if r.get('risk_score', 0) >= 3.0]
        
        total_potential_impact = sum(
            r.get('cost_impact', 50000) for r in high_impact_risks
        )
        
        # Recommended contingency: 15-25% of total potential impact
        contingency_budget = total_potential_impact * 0.20
        
        return {
            'recommended_contingency': f"${contingency_budget:,.0f}",
            'percentage_of_project': '15-25%',
            'allocation_priority': 'High-impact risks first'
        }
    
    async def _fallback_risk_assessment(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback risk assessment when main processing fails."""
        logger.info("Using fallback risk assessment")
        
        content = inputs.get('document_content', '')
        
        # Basic risk identification
        basic_risks = []
        
        # Look for common risk indicators
        risk_keywords = {
            'budget': 'Commercial risk related to budget constraints',
            'timeline': 'Schedule risk related to project timeline',
            'integration': 'Technical risk related to system integration',
            'security': 'Compliance risk related to security requirements'
        }
        
        counter = 1
        for keyword, description in risk_keywords.items():
            if keyword.lower() in content.lower():
                basic_risks.append({
                    'id': f'FALLBACK-RISK-{counter:03d}',
                    'title': f'{keyword.title()} Risk',
                    'description': description,
                    'category': 'technical',
                    'probability': 'medium',
                    'impact': 'medium',
                    'risk_score': 2.5,
                    'mitigation_strategies': [f'Address {keyword} through careful planning'],
                    'contingency_plans': [f'Develop fallback plan for {keyword} issues']
                })
                counter += 1
        
        return {
            'identified_risks': basic_risks,
            'assessment_method': 'fallback',
            'risk_matrix': {
                'medium_risks': basic_risks,
                'overall_metrics': {
                    'total_risks': len(basic_risks),
                    'risk_level': 'Medium'
                }
            },
            'error': 'Full risk assessment failed, basic patterns used'
        }
