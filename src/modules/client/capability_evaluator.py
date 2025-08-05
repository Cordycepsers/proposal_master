"""
Capability Evaluator Sub-Agent

Specialized sub-agent for evaluating organizational capabilities and readiness
to execute projects based on technical, operational, and resource assessments.
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio

from ...agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CapabilityEvaluator(BaseAgent):
    """Sub-agent for evaluating organizational capabilities and project readiness."""
    
    def __init__(self):
        super().__init__(
            name="Capability Evaluator",
            description="Evaluates organizational capabilities and readiness"
        )
        
        # Capability assessment dimensions
        self.capability_dimensions = {
            'technical': {
                'factors': ['technology_stack', 'architecture_experience', 'development_practices', 'security_expertise'],
                'weight': 0.3
            },
            'operational': {
                'factors': ['project_management', 'team_size', 'experience_level', 'delivery_track_record'],
                'weight': 0.25
            },
            'organizational': {
                'factors': ['change_management', 'stakeholder_engagement', 'resource_allocation', 'decision_making'],
                'weight': 0.2
            },
            'financial': {
                'factors': ['budget_management', 'cost_control', 'financial_reporting', 'investment_capacity'],
                'weight': 0.15
            },
            'strategic': {
                'factors': ['vision_alignment', 'long_term_planning', 'innovation_capacity', 'market_position'],
                'weight': 0.1
            }
        }
        
        # Maturity levels
        self.maturity_levels = {
            1: {'name': 'Initial', 'description': 'Ad-hoc processes, unpredictable outcomes'},
            2: {'name': 'Developing', 'description': 'Some processes documented, basic capabilities present'},
            3: {'name': 'Defined', 'description': 'Standardized processes, consistent execution'},
            4: {'name': 'Managed', 'description': 'Measured and controlled processes, good outcomes'},
            5: {'name': 'Optimizing', 'description': 'Continuous improvement, excellent outcomes'}
        }
        
        self.evaluation_stats = {
            'evaluations_completed': 0,
            'avg_capability_score': 0.0,
            'high_readiness_clients': 0
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate organizational capabilities and readiness.
        
        Args:
            input_data: Dictionary containing:
                - client_profile: Client organization information
                - project_requirements: Project technical and operational requirements
                - assessment_scope: Areas to focus evaluation on
                
        Returns:
            Dictionary containing capability assessment and recommendations
        """
        try:
            self.log_operation("Starting capability evaluation", input_data)
            
            client_profile = input_data.get('client_profile', {})
            project_requirements = input_data.get('project_requirements', {})
            assessment_scope = input_data.get('assessment_scope', list(self.capability_dimensions.keys()))
            
            if not client_profile:
                raise ValueError("Client profile is required for capability evaluation")
            
            # Assess capabilities by dimension
            capability_assessment = await self._assess_capabilities(
                client_profile, project_requirements, assessment_scope
            )
            
            # Calculate overall readiness score
            readiness_score = await self._calculate_readiness_score(capability_assessment)
            
            # Identify capability gaps
            capability_gaps = await self._identify_capability_gaps(
                capability_assessment, project_requirements
            )
            
            # Generate improvement recommendations
            improvement_plan = await self._generate_improvement_plan(capability_gaps, capability_assessment)
            
            # Assess project fit
            project_fit = await self._assess_project_fit(capability_assessment, project_requirements)
            
            # Update statistics
            self.evaluation_stats['evaluations_completed'] += 1
            self.evaluation_stats['avg_capability_score'] = (
                (self.evaluation_stats['avg_capability_score'] * (self.evaluation_stats['evaluations_completed'] - 1) + 
                 readiness_score['overall_score']) / self.evaluation_stats['evaluations_completed']
            )
            if readiness_score['readiness_level'] in ['high', 'very_high']:
                self.evaluation_stats['high_readiness_clients'] += 1
            
            result = {
                'status': 'success',
                'client_id': client_profile.get('id', 'unknown'),
                'capability_assessment': capability_assessment,
                'readiness_score': readiness_score,
                'capability_gaps': capability_gaps,
                'improvement_plan': improvement_plan,
                'project_fit': project_fit,
                'evaluation_stats': self.evaluation_stats.copy()
            }
            
            self.log_operation("Capability evaluation completed", {
                'client_id': client_profile.get('id', 'unknown'),
                'readiness_level': readiness_score['readiness_level']
            })
            return result
            
        except Exception as e:
            error_msg = f"Capability evaluation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'client_id': input_data.get('client_profile', {}).get('id', 'unknown')
            }
    
    async def _assess_capabilities(self, client_profile: Dict[str, Any], 
                                 project_requirements: Dict[str, Any], 
                                 assessment_scope: List[str]) -> Dict[str, Dict[str, Any]]:
        """Assess capabilities across specified dimensions."""
        try:
            assessment = {}
            
            for dimension in assessment_scope:
                if dimension not in self.capability_dimensions:
                    continue
                
                dimension_config = self.capability_dimensions[dimension]
                factors = dimension_config['factors']
                
                # Assess each factor in the dimension
                factor_scores = {}
                for factor in factors:
                    score = await self._assess_factor(factor, client_profile, project_requirements)
                    factor_scores[factor] = score
                
                # Calculate dimension score
                dimension_score = sum(factor_scores.values()) / len(factor_scores)
                maturity_level = self._get_maturity_level(dimension_score)
                
                assessment[dimension] = {
                    'score': round(dimension_score, 2),
                    'maturity_level': maturity_level,
                    'maturity_name': self.maturity_levels[maturity_level]['name'],
                    'factor_scores': factor_scores,
                    'weight': dimension_config['weight'],
                    'weighted_score': round(dimension_score * dimension_config['weight'], 2)
                }
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Capability assessment failed: {e}")
            return {}
    
    async def _assess_factor(self, factor: str, client_profile: Dict[str, Any], 
                           project_requirements: Dict[str, Any]) -> float:
        """Assess a specific capability factor."""
        try:
            # Base score from client profile
            base_score = 3.0  # Default middle score
            
            # Factor-specific assessment logic
            if factor == 'technology_stack':
                tech_experience = client_profile.get('technology_experience', {})
                required_tech = project_requirements.get('technologies', [])
                
                if required_tech:
                    matches = sum(1 for tech in required_tech if tech.lower() in 
                                 [t.lower() for t in tech_experience.get('languages', [])] +
                                 [t.lower() for t in tech_experience.get('frameworks', [])])
                    base_score = min(5.0, 2.0 + (matches / len(required_tech)) * 3.0)
            
            elif factor == 'team_size':
                team_size = client_profile.get('team_size', 0)
                required_team = project_requirements.get('estimated_team_size', 5)
                
                if team_size >= required_team:
                    base_score = 4.5
                elif team_size >= required_team * 0.8:
                    base_score = 4.0
                elif team_size >= required_team * 0.6:
                    base_score = 3.0
                else:
                    base_score = 2.0
            
            elif factor == 'budget_management':
                budget_track_record = client_profile.get('budget_track_record', 'unknown')
                if budget_track_record == 'excellent':
                    base_score = 5.0
                elif budget_track_record == 'good':
                    base_score = 4.0
                elif budget_track_record == 'fair':
                    base_score = 3.0
                elif budget_track_record == 'poor':
                    base_score = 2.0
                else:
                    base_score = 3.0  # Unknown, assume average
            
            elif factor == 'experience_level':
                years_experience = client_profile.get('years_experience', 0)
                if years_experience >= 10:
                    base_score = 5.0
                elif years_experience >= 5:
                    base_score = 4.0
                elif years_experience >= 2:
                    base_score = 3.0
                else:
                    base_score = 2.0
            
            elif factor == 'delivery_track_record':
                success_rate = client_profile.get('project_success_rate', 0.5)
                base_score = 1.0 + (success_rate * 4.0)  # Scale 0-1 to 1-5
            
            # Add organizational factors assessment
            elif factor in ['change_management', 'stakeholder_engagement']:
                org_maturity = client_profile.get('organizational_maturity', 'developing')
                maturity_scores = {'initial': 2.0, 'developing': 3.0, 'defined': 4.0, 'managed': 4.5, 'optimizing': 5.0}
                base_score = maturity_scores.get(org_maturity, 3.0)
            
            # Ensure score is within bounds
            return max(1.0, min(5.0, base_score))
            
        except Exception as e:
            self.logger.error(f"Factor assessment failed for {factor}: {e}")
            return 3.0  # Default middle score
    
    async def _calculate_readiness_score(self, capability_assessment: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall readiness score."""
        try:
            # Calculate weighted average
            total_weighted_score = sum(dim['weighted_score'] for dim in capability_assessment.values())
            total_weight = sum(dim['weight'] for dim in capability_assessment.values())
            
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Determine readiness level
            if overall_score >= 4.5:
                readiness_level = 'very_high'
                readiness_description = 'Organization is exceptionally well-prepared'
            elif overall_score >= 4.0:
                readiness_level = 'high'
                readiness_description = 'Organization is well-prepared with minor gaps'
            elif overall_score >= 3.0:
                readiness_level = 'medium'
                readiness_description = 'Organization has adequate capabilities with some development needed'
            elif overall_score >= 2.0:
                readiness_level = 'low'
                readiness_description = 'Organization needs significant capability development'
            else:
                readiness_level = 'very_low'
                readiness_description = 'Organization requires extensive preparation'
            
            return {
                'overall_score': round(overall_score, 2),
                'max_score': 5.0,
                'percentage': round((overall_score / 5.0) * 100, 1),
                'readiness_level': readiness_level,
                'description': readiness_description
            }
            
        except Exception as e:
            self.logger.error(f"Readiness score calculation failed: {e}")
            return {'overall_score': 0.0, 'readiness_level': 'unknown', 'description': 'Assessment failed'}
    
    async def _identify_capability_gaps(self, capability_assessment: Dict[str, Dict[str, Any]], 
                                      project_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify capability gaps that need attention."""
        try:
            gaps = []
            
            for dimension, assessment in capability_assessment.items():
                dimension_score = assessment['score']
                
                # Identify low-scoring areas (below 3.0)
                if dimension_score < 3.0:
                    gap = {
                        'dimension': dimension,
                        'current_score': dimension_score,
                        'target_score': 3.5,  # Minimum acceptable
                        'gap_size': 3.5 - dimension_score,
                        'severity': 'high' if dimension_score < 2.0 else 'medium',
                        'factors': []
                    }
                    
                    # Identify specific factor gaps
                    factor_scores = assessment.get('factor_scores', {})
                    for factor, score in factor_scores.items():
                        if score < 3.0:
                            gap['factors'].append({
                                'factor': factor,
                                'current_score': score,
                                'gap': 3.0 - score
                            })
                    
                    gaps.append(gap)
            
            # Sort by gap size (largest gaps first)
            gaps.sort(key=lambda x: x['gap_size'], reverse=True)
            
            return gaps
            
        except Exception as e:
            self.logger.error(f"Gap identification failed: {e}")
            return []
    
    async def _generate_improvement_plan(self, capability_gaps: List[Dict[str, Any]], 
                                       capability_assessment: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate improvement plan to address capability gaps."""
        try:
            improvement_plan = {
                'priority_actions': [],
                'medium_term_goals': [],
                'long_term_objectives': [],
                'estimated_timeline': {},
                'resource_requirements': {}
            }
            
            for gap in capability_gaps:
                dimension = gap['dimension']
                severity = gap['severity']
                gap_size = gap['gap_size']
                
                # Generate dimension-specific recommendations
                recommendations = await self._get_dimension_recommendations(dimension, gap)
                
                if severity == 'high':
                    improvement_plan['priority_actions'].extend(recommendations['immediate'])
                    improvement_plan['estimated_timeline'][dimension] = recommendations['timeline']
                    improvement_plan['resource_requirements'][dimension] = recommendations['resources']
                else:
                    improvement_plan['medium_term_goals'].extend(recommendations['medium_term'])
            
            # Add general long-term objectives
            improvement_plan['long_term_objectives'] = [
                'Establish continuous capability assessment process',
                'Implement regular training and development programs',
                'Create knowledge management and best practices repository',
                'Develop organizational change management capabilities'
            ]
            
            return improvement_plan
            
        except Exception as e:
            self.logger.error(f"Improvement plan generation failed: {e}")
            return {}
    
    async def _get_dimension_recommendations(self, dimension: str, 
                                           gap: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific recommendations for a capability dimension."""
        try:
            recommendations = {
                'immediate': [],
                'medium_term': [],
                'timeline': '3-6 months',
                'resources': 'moderate'
            }
            
            if dimension == 'technical':
                recommendations['immediate'] = [
                    'Conduct technical skills assessment for key team members',
                    'Identify and engage technical mentors or consultants',
                    'Implement technical training program for critical skills'
                ]
                recommendations['medium_term'] = [
                    'Establish technical standards and best practices',
                    'Implement code review and quality assurance processes'
                ]
                recommendations['timeline'] = '2-4 months'
                recommendations['resources'] = 'high'
            
            elif dimension == 'operational':
                recommendations['immediate'] = [
                    'Implement project management methodology (Agile/PMBOK)',
                    'Assign experienced project manager',
                    'Establish regular project reporting and communication'
                ]
                recommendations['medium_term'] = [
                    'Develop project management capabilities across team',
                    'Implement project portfolio management processes'
                ]
                recommendations['timeline'] = '1-3 months'
                recommendations['resources'] = 'moderate'
            
            elif dimension == 'organizational':
                recommendations['immediate'] = [
                    'Engage change management consultant',
                    'Establish project steering committee',
                    'Define clear roles and responsibilities'
                ]
                recommendations['medium_term'] = [
                    'Implement organizational change management processes',
                    'Develop internal change management capabilities'
                ]
                recommendations['timeline'] = '3-6 months'
                recommendations['resources'] = 'moderate'
            
            elif dimension == 'financial':
                recommendations['immediate'] = [
                    'Implement project budget tracking and reporting',
                    'Assign dedicated financial oversight',
                    'Establish cost control measures'
                ]
                recommendations['medium_term'] = [
                    'Develop financial management capabilities',
                    'Implement project financial management processes'
                ]
                recommendations['timeline'] = '1-2 months'
                recommendations['resources'] = 'low'
            
            elif dimension == 'strategic':
                recommendations['immediate'] = [
                    'Align project goals with organizational strategy',
                    'Establish executive sponsorship',
                    'Define success criteria and metrics'
                ]
                recommendations['medium_term'] = [
                    'Develop strategic planning capabilities',
                    'Implement strategic alignment processes'
                ]
                recommendations['timeline'] = '2-4 months'
                recommendations['resources'] = 'moderate'
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed for {dimension}: {e}")
            return {'immediate': [], 'medium_term': [], 'timeline': 'unknown', 'resources': 'unknown'}
    
    async def _assess_project_fit(self, capability_assessment: Dict[str, Dict[str, Any]], 
                                project_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how well the organization fits the specific project."""
        try:
            fit_score = 0.0
            fit_factors = []
            
            # Technical fit
            if 'technical' in capability_assessment:
                tech_score = capability_assessment['technical']['score']
                project_complexity = project_requirements.get('technical_complexity', 3.0)
                
                tech_fit = min(tech_score / project_complexity, 1.0)
                fit_score += tech_fit * 0.4
                fit_factors.append({
                    'factor': 'Technical Capability',
                    'score': tech_fit,
                    'assessment': 'Good fit' if tech_fit > 0.8 else 'Adequate fit' if tech_fit > 0.6 else 'Gap exists'
                })
            
            # Operational fit
            if 'operational' in capability_assessment:
                ops_score = capability_assessment['operational']['score']
                project_management_complexity = project_requirements.get('management_complexity', 3.0)
                
                ops_fit = min(ops_score / project_management_complexity, 1.0)
                fit_score += ops_fit * 0.3
                fit_factors.append({
                    'factor': 'Operational Capability',
                    'score': ops_fit,
                    'assessment': 'Good fit' if ops_fit > 0.8 else 'Adequate fit' if ops_fit > 0.6 else 'Gap exists'
                })
            
            # Resource fit
            team_size = project_requirements.get('estimated_team_size', 5)
            available_team = capability_assessment.get('operational', {}).get('factor_scores', {}).get('team_size', 3.0)
            
            resource_fit = min(available_team / 3.0, 1.0)  # Normalize to team adequacy
            fit_score += resource_fit * 0.3
            fit_factors.append({
                'factor': 'Resource Availability',
                'score': resource_fit,
                'assessment': 'Sufficient' if resource_fit > 0.8 else 'Adequate' if resource_fit > 0.6 else 'Insufficient'
            })
            
            # Overall fit assessment
            if fit_score > 0.8:
                fit_level = 'excellent'
                fit_description = 'Organization is an excellent fit for this project'
            elif fit_score > 0.6:
                fit_level = 'good'
                fit_description = 'Organization is a good fit with minor considerations'
            elif fit_score > 0.4:
                fit_level = 'fair'
                fit_description = 'Organization has adequate fit but requires development'
            else:
                fit_level = 'poor'
                fit_description = 'Organization may not be ready for this project'
            
            return {
                'overall_fit_score': round(fit_score, 2),
                'fit_level': fit_level,
                'description': fit_description,
                'fit_factors': fit_factors
            }
            
        except Exception as e:
            self.logger.error(f"Project fit assessment failed: {e}")
            return {'overall_fit_score': 0.0, 'fit_level': 'unknown', 'description': 'Assessment failed'}
    
    def _get_maturity_level(self, score: float) -> int:
        """Convert score to maturity level (1-5)."""
        if score >= 4.5:
            return 5
        elif score >= 3.5:
            return 4
        elif score >= 2.5:
            return 3
        elif score >= 1.5:
            return 2
        else:
            return 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get capability evaluation statistics."""
        return self.evaluation_stats.copy()
