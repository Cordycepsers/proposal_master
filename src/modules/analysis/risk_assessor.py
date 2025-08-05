"""
Risk Assessor Sub-Agent

Specialized sub-agent for evaluating project risks and providing mitigation strategies.
Analyzes technical, timeline, budget, and operational risks based on project requirements.
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, timedelta

from ...agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class RiskAssessor(BaseAgent):
    """Sub-agent for project risk assessment and mitigation planning."""
    
    def __init__(self):
        super().__init__(
            name="Risk Assessor",
            description="Evaluates project risks and provides mitigation strategies"
        )
        
        # Risk categories and their indicators
        self.risk_categories = {
            'technical': {
                'indicators': ['new technology', 'complex integration', 'legacy system', 'scalability', 'performance'],
                'weight': 0.3
            },
            'timeline': {
                'indicators': ['tight deadline', 'aggressive schedule', 'multiple phases', 'dependencies'],
                'weight': 0.25
            },
            'budget': {
                'indicators': ['limited budget', 'cost constraints', 'funding', 'expensive'],
                'weight': 0.2
            },
            'operational': {
                'indicators': ['resource availability', 'team size', 'expertise', 'training required'],
                'weight': 0.15
            },
            'compliance': {
                'indicators': ['regulatory', 'audit', 'security', 'privacy', 'gdpr', 'hipaa'],
                'weight': 0.1
            }
        }
        
        # Risk severity levels
        self.severity_levels = {
            'low': {'score': 1, 'color': 'green', 'action': 'monitor'},
            'medium': {'score': 2, 'color': 'yellow', 'action': 'plan'},
            'high': {'score': 3, 'color': 'orange', 'action': 'mitigate'},
            'critical': {'score': 4, 'color': 'red', 'action': 'immediate'}
        }
        
        self.assessment_stats = {
            'assessments_completed': 0,
            'avg_risk_score': 0.0,
            'high_risk_projects': 0
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess project risks based on requirements and project details.
        
        Args:
            input_data: Dictionary containing:
                - requirements: Extracted project requirements
                - project_details: Project metadata (timeline, budget, etc.)
                - content: Original document content
                
        Returns:
            Dictionary containing risk assessment and mitigation strategies
        """
        try:
            self.log_operation("Starting risk assessment", input_data)
            
            requirements = input_data.get('requirements', {})
            project_details = input_data.get('project_details', {})
            content = input_data.get('content', '')
            
            # Assess risks by category
            risk_assessment = await self._assess_risk_categories(requirements, project_details, content)
            
            # Calculate overall risk score
            overall_risk = await self._calculate_overall_risk(risk_assessment)
            
            # Generate mitigation strategies
            mitigation_strategies = await self._generate_mitigation_strategies(risk_assessment)
            
            # Create risk timeline
            risk_timeline = await self._create_risk_timeline(risk_assessment, project_details)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(risk_assessment, overall_risk)
            
            # Update statistics
            self.assessment_stats['assessments_completed'] += 1
            self.assessment_stats['avg_risk_score'] = (
                (self.assessment_stats['avg_risk_score'] * (self.assessment_stats['assessments_completed'] - 1) + 
                 overall_risk['score']) / self.assessment_stats['assessments_completed']
            )
            if overall_risk['level'] in ['high', 'critical']:
                self.assessment_stats['high_risk_projects'] += 1
            
            result = {
                'status': 'success',
                'risk_assessment': risk_assessment,
                'overall_risk': overall_risk,
                'mitigation_strategies': mitigation_strategies,
                'risk_timeline': risk_timeline,
                'recommendations': recommendations,
                'assessment_stats': self.assessment_stats.copy()
            }
            
            self.log_operation("Risk assessment completed", {
                'overall_risk_level': overall_risk['level'],
                'risk_score': overall_risk['score']
            })
            return result
            
        except Exception as e:
            error_msg = f"Risk assessment failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg
            }
    
    async def _assess_risk_categories(self, requirements: Dict[str, Any], 
                                    project_details: Dict[str, Any], 
                                    content: str) -> Dict[str, Dict[str, Any]]:
        """Assess risks for each category."""
        try:
            risk_assessment = {}
            content_lower = content.lower()
            
            for category, config in self.risk_categories.items():
                indicators = config['indicators']
                weight = config['weight']
                
                # Count indicator matches
                matches = []
                for indicator in indicators:
                    if indicator in content_lower:
                        matches.append(indicator)
                
                # Calculate risk score for this category
                match_ratio = len(matches) / len(indicators)
                base_score = match_ratio * 4  # Scale to 0-4
                
                # Adjust based on project details
                adjusted_score = await self._adjust_score_by_context(
                    category, base_score, project_details, requirements
                )
                
                # Determine severity level
                severity = self._get_severity_level(adjusted_score)
                
                risk_assessment[category] = {
                    'score': round(adjusted_score, 2),
                    'severity': severity,
                    'indicators_found': matches,
                    'weight': weight,
                    'weighted_score': round(adjusted_score * weight, 2)
                }
            
            return risk_assessment
            
        except Exception as e:
            self.logger.error(f"Risk category assessment failed: {e}")
            return {}
    
    async def _adjust_score_by_context(self, category: str, base_score: float, 
                                     project_details: Dict[str, Any], 
                                     requirements: Dict[str, Any]) -> float:
        """Adjust risk score based on project context."""
        try:
            adjusted_score = base_score
            
            if category == 'timeline':
                # Check deadline pressure
                deadline = project_details.get('deadline')
                if deadline:
                    # Simulate deadline analysis
                    if 'urgent' in str(deadline).lower() or 'asap' in str(deadline).lower():
                        adjusted_score += 1.0
                
                # Check requirement complexity
                total_reqs = sum(len(reqs) for reqs in requirements.values() if isinstance(reqs, list))
                if total_reqs > 20:
                    adjusted_score += 0.5
            
            elif category == 'technical':
                # Check for complex technical requirements
                tech_reqs = requirements.get('technical', [])
                if isinstance(tech_reqs, list) and len(tech_reqs) > 5:
                    adjusted_score += 0.5
                
                # Check for integration requirements
                functional_reqs = requirements.get('functional', [])
                if isinstance(functional_reqs, list):
                    integration_count = sum(1 for req in functional_reqs 
                                          if isinstance(req, dict) and 
                                          'integration' in req.get('text', '').lower())
                    adjusted_score += integration_count * 0.2
            
            elif category == 'budget':
                # Check budget constraints
                budget = project_details.get('budget')
                if budget and ('limited' in str(budget).lower() or 'tight' in str(budget).lower()):
                    adjusted_score += 0.5
            
            elif category == 'compliance':
                # Check compliance requirements
                compliance_reqs = requirements.get('compliance', [])
                if isinstance(compliance_reqs, list) and len(compliance_reqs) > 3:
                    adjusted_score += 0.8
            
            # Cap the score at 4.0
            return min(adjusted_score, 4.0)
            
        except Exception as e:
            self.logger.error(f"Score adjustment failed: {e}")
            return base_score
    
    async def _calculate_overall_risk(self, risk_assessment: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall project risk score."""
        try:
            weighted_scores = [risk['weighted_score'] for risk in risk_assessment.values()]
            overall_score = sum(weighted_scores)
            
            # Determine overall risk level
            if overall_score >= 3.0:
                level = 'critical'
            elif overall_score >= 2.0:
                level = 'high'
            elif overall_score >= 1.0:
                level = 'medium'
            else:
                level = 'low'
            
            return {
                'score': round(overall_score, 2),
                'level': level,
                'max_score': 4.0,
                'percentage': round((overall_score / 4.0) * 100, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Overall risk calculation failed: {e}")
            return {'score': 0.0, 'level': 'low', 'percentage': 0.0}
    
    async def _generate_mitigation_strategies(self, risk_assessment: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate mitigation strategies for identified risks."""
        try:
            strategies = {}
            
            for category, risk_data in risk_assessment.items():
                severity = risk_data['severity']
                score = risk_data['score']
                
                if score < 1.0:  # Low risk, minimal mitigation needed
                    strategies[category] = [{
                        'strategy': 'Monitor and review regularly',
                        'priority': 'low',
                        'timeline': '4-6 weeks',
                        'resource_requirement': 'minimal'
                    }]
                    continue
                
                category_strategies = []
                
                if category == 'technical':
                    category_strategies = [
                        {
                            'strategy': 'Conduct technical proof of concept',
                            'priority': 'high' if score >= 2.0 else 'medium',
                            'timeline': '2-3 weeks',
                            'resource_requirement': 'senior developer'
                        },
                        {
                            'strategy': 'Implement incremental development approach',
                            'priority': 'medium',
                            'timeline': 'ongoing',
                            'resource_requirement': 'team coordination'
                        }
                    ]
                
                elif category == 'timeline':
                    category_strategies = [
                        {
                            'strategy': 'Break down into smaller milestones',
                            'priority': 'high',
                            'timeline': '1 week',
                            'resource_requirement': 'project manager'
                        },
                        {
                            'strategy': 'Identify and plan for dependencies',
                            'priority': 'high',
                            'timeline': '1-2 weeks',
                            'resource_requirement': 'project team'
                        }
                    ]
                
                elif category == 'budget':
                    category_strategies = [
                        {
                            'strategy': 'Implement cost tracking and monitoring',
                            'priority': 'high',
                            'timeline': '1 week',
                            'resource_requirement': 'financial analyst'
                        },
                        {
                            'strategy': 'Define minimum viable product (MVP)',
                            'priority': 'medium',
                            'timeline': '2 weeks',
                            'resource_requirement': 'product owner'
                        }
                    ]
                
                elif category == 'operational':
                    category_strategies = [
                        {
                            'strategy': 'Assess team skills and provide training',
                            'priority': 'medium',
                            'timeline': '2-4 weeks',
                            'resource_requirement': 'training budget'
                        },
                        {
                            'strategy': 'Establish clear communication protocols',
                            'priority': 'high',
                            'timeline': '1 week',
                            'resource_requirement': 'team leads'
                        }
                    ]
                
                elif category == 'compliance':
                    category_strategies = [
                        {
                            'strategy': 'Engage compliance expert early',
                            'priority': 'critical',
                            'timeline': '1 week',
                            'resource_requirement': 'compliance consultant'
                        },
                        {
                            'strategy': 'Implement compliance checkpoints',
                            'priority': 'high',
                            'timeline': '2 weeks',
                            'resource_requirement': 'compliance team'
                        }
                    ]
                
                strategies[category] = category_strategies
            
            return strategies
            
        except Exception as e:
            self.logger.error(f"Mitigation strategy generation failed: {e}")
            return {}
    
    async def _create_risk_timeline(self, risk_assessment: Dict[str, Dict[str, Any]], 
                                  project_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a timeline of risk events and mitigation activities."""
        try:
            timeline = []
            current_date = datetime.now()
            
            # Add immediate risk assessment
            timeline.append({
                'date': current_date.isoformat(),
                'event': 'Risk Assessment Completed',
                'type': 'milestone',
                'description': 'Initial project risk assessment completed'
            })
            
            # Add mitigation checkpoints based on risk levels
            for category, risk_data in risk_assessment.items():
                severity = risk_data['severity']
                
                if severity in ['high', 'critical']:
                    # Add immediate action item
                    timeline.append({
                        'date': (current_date + timedelta(days=7)).isoformat(),
                        'event': f'{category.title()} Risk Mitigation',
                        'type': 'action',
                        'description': f'Begin mitigation strategies for {category} risks'
                    })
                
                elif severity == 'medium':
                    # Add review checkpoint
                    timeline.append({
                        'date': (current_date + timedelta(days=14)).isoformat(),
                        'event': f'{category.title()} Risk Review',
                        'type': 'review',
                        'description': f'Review and monitor {category} risks'
                    })
            
            # Add regular risk reviews
            for i in range(1, 4):  # Monthly reviews for 3 months
                timeline.append({
                    'date': (current_date + timedelta(days=30 * i)).isoformat(),
                    'event': 'Monthly Risk Review',
                    'type': 'review',
                    'description': 'Regular project risk assessment and mitigation review'
                })
            
            # Sort timeline by date
            timeline.sort(key=lambda x: x['date'])
            
            return timeline
            
        except Exception as e:
            self.logger.error(f"Risk timeline creation failed: {e}")
            return []
    
    async def _generate_recommendations(self, risk_assessment: Dict[str, Dict[str, Any]], 
                                      overall_risk: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate high-level recommendations based on risk assessment."""
        try:
            recommendations = []
            
            # Overall risk recommendations
            if overall_risk['level'] == 'critical':
                recommendations.append({
                    'type': 'critical',
                    'recommendation': 'Consider project scope reduction or timeline extension',
                    'rationale': 'Critical risk level requires immediate attention to prevent project failure'
                })
            
            elif overall_risk['level'] == 'high':
                recommendations.append({
                    'type': 'high',
                    'recommendation': 'Implement comprehensive risk monitoring and regular checkpoints',
                    'rationale': 'High risk level requires active management and frequent review'
                })
            
            # Category-specific recommendations
            for category, risk_data in risk_assessment.items():
                if risk_data['severity'] in ['high', 'critical']:
                    if category == 'technical':
                        recommendations.append({
                            'type': 'technical',
                            'recommendation': 'Allocate additional senior technical resources',
                            'rationale': 'High technical risk requires experienced team members'
                        })
                    
                    elif category == 'timeline':
                        recommendations.append({
                            'type': 'timeline',
                            'recommendation': 'Negotiate timeline extension or reduce scope',
                            'rationale': 'Timeline risks may compromise project quality'
                        })
            
            # Add general best practices
            recommendations.append({
                'type': 'general',
                'recommendation': 'Establish weekly risk review meetings',
                'rationale': 'Regular monitoring helps identify and address risks early'
            })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return []
    
    def _get_severity_level(self, score: float) -> str:
        """Determine severity level based on risk score."""
        if score >= 3.0:
            return 'critical'
        elif score >= 2.0:
            return 'high'
        elif score >= 1.0:
            return 'medium'
        else:
            return 'low'
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get risk assessment statistics."""
        return self.assessment_stats.copy()
