"""
Profile Comparator Sub-Agent

Specialized sub-agent for comparing client profiles against project requirements
and providing compatibility analysis and recommendations.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import asyncio

from ...agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ProfileComparator(BaseAgent):
    """Sub-agent for comparing client profiles against project requirements."""
    
    def __init__(self):
        super().__init__(
            name="Profile Comparator",
            description="Compares client profiles against project requirements"
        )
        
        # Comparison categories and weights
        self.comparison_categories = {
            'technical_alignment': {
                'weight': 0.25,
                'factors': ['technology_stack', 'technical_complexity', 'security_requirements', 'scalability_needs']
            },
            'operational_alignment': {
                'weight': 0.25,
                'factors': ['project_methodology', 'team_structure', 'communication_style', 'delivery_approach']
            },
            'business_alignment': {
                'weight': 0.2,
                'factors': ['industry_experience', 'business_domain', 'market_focus', 'strategic_goals']
            },
            'resource_alignment': {
                'weight': 0.15,
                'factors': ['budget_range', 'timeline_expectations', 'team_availability', 'infrastructure_readiness']
            },
            'cultural_alignment': {
                'weight': 0.15,
                'factors': ['work_culture', 'communication_preferences', 'decision_making_style', 'risk_tolerance']
            }
        }
        
        # Compatibility levels
        self.compatibility_levels = {
            'excellent': {'min_score': 0.9, 'color': 'green', 'recommendation': 'Highly recommended'},
            'good': {'min_score': 0.75, 'color': 'light_green', 'recommendation': 'Recommended with minor considerations'},
            'fair': {'min_score': 0.6, 'color': 'yellow', 'recommendation': 'Possible with adjustments'},
            'poor': {'min_score': 0.4, 'color': 'orange', 'recommendation': 'Significant challenges expected'},
            'very_poor': {'min_score': 0.0, 'color': 'red', 'recommendation': 'Not recommended without major changes'}
        }
        
        self.comparison_stats = {
            'comparisons_completed': 0,
            'avg_compatibility_score': 0.0,
            'high_compatibility_matches': 0
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare client profile against project requirements.
        
        Args:
            input_data: Dictionary containing:
                - client_profile: Client organization profile
                - project_requirements: Project requirements and specifications
                - comparison_scope: Categories to include in comparison
                - weighting_preferences: Optional custom weights for categories
                
        Returns:
            Dictionary containing compatibility analysis and recommendations
        """
        try:
            self.log_operation("Starting profile comparison", input_data)
            
            client_profile = input_data.get('client_profile', {})
            project_requirements = input_data.get('project_requirements', {})
            comparison_scope = input_data.get('comparison_scope', list(self.comparison_categories.keys()))
            weighting_preferences = input_data.get('weighting_preferences', {})
            
            if not client_profile or not project_requirements:
                raise ValueError("Both client profile and project requirements are required")
            
            # Adjust weights if custom preferences provided
            adjusted_weights = self._adjust_weights(weighting_preferences)
            
            # Perform detailed comparison by category
            category_comparisons = await self._compare_categories(
                client_profile, project_requirements, comparison_scope, adjusted_weights
            )
            
            # Calculate overall compatibility score
            compatibility_score = await self._calculate_compatibility_score(category_comparisons)
            
            # Identify alignment strengths and gaps
            alignment_analysis = await self._analyze_alignment(category_comparisons, client_profile, project_requirements)
            
            # Generate compatibility recommendations
            recommendations = await self._generate_compatibility_recommendations(
                compatibility_score, alignment_analysis, category_comparisons
            )
            
            # Create risk assessment based on misalignments
            risk_assessment = await self._assess_compatibility_risks(alignment_analysis, category_comparisons)
            
            # Update statistics
            self.comparison_stats['comparisons_completed'] += 1
            self.comparison_stats['avg_compatibility_score'] = (
                (self.comparison_stats['avg_compatibility_score'] * (self.comparison_stats['comparisons_completed'] - 1) + 
                 compatibility_score['overall_score']) / self.comparison_stats['comparisons_completed']
            )
            if compatibility_score['compatibility_level'] in ['excellent', 'good']:
                self.comparison_stats['high_compatibility_matches'] += 1
            
            result = {
                'status': 'success',
                'client_id': client_profile.get('id', 'unknown'),
                'project_id': project_requirements.get('id', 'unknown'),
                'category_comparisons': category_comparisons,
                'compatibility_score': compatibility_score,
                'alignment_analysis': alignment_analysis,
                'recommendations': recommendations,
                'risk_assessment': risk_assessment,
                'comparison_stats': self.comparison_stats.copy()
            }
            
            self.log_operation("Profile comparison completed", {
                'client_id': client_profile.get('id', 'unknown'),
                'compatibility_level': compatibility_score['compatibility_level']
            })
            return result
            
        except Exception as e:
            error_msg = f"Profile comparison failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'client_id': input_data.get('client_profile', {}).get('id', 'unknown')
            }
    
    async def _compare_categories(self, client_profile: Dict[str, Any], 
                                project_requirements: Dict[str, Any], 
                                comparison_scope: List[str], 
                                adjusted_weights: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Compare client profile against project requirements by category."""
        try:
            comparisons = {}
            
            for category in comparison_scope:
                if category not in self.comparison_categories:
                    continue
                    
                category_config = self.comparison_categories[category]
                factors = category_config['factors']
                weight = adjusted_weights.get(category, category_config['weight'])
                
                # Compare each factor in the category
                factor_comparisons = {}
                category_score = 0.0
                
                for factor in factors:
                    factor_score, factor_details = await self._compare_factor(
                        factor, client_profile, project_requirements
                    )
                    factor_comparisons[factor] = {
                        'score': factor_score,
                        'details': factor_details
                    }
                    category_score += factor_score
                
                # Calculate average category score
                category_score = category_score / len(factors) if factors else 0.0
                
                comparisons[category] = {
                    'score': round(category_score, 2),
                    'weight': weight,
                    'weighted_score': round(category_score * weight, 2),
                    'factor_comparisons': factor_comparisons,
                    'alignment_level': self._get_alignment_level(category_score)
                }
            
            return comparisons
            
        except Exception as e:
            self.logger.error(f"Category comparison failed: {e}")
            return {}
    
    async def _compare_factor(self, factor: str, client_profile: Dict[str, Any], 
                            project_requirements: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Compare a specific factor between client and project requirements."""
        try:
            score = 0.5  # Default neutral score
            details = {'client_value': None, 'required_value': None, 'match_quality': 'unknown'}
            
            # Factor-specific comparison logic
            if factor == 'technology_stack':
                client_tech = client_profile.get('technology_experience', {})
                required_tech = project_requirements.get('technologies', [])
                
                client_languages = set(t.lower() for t in client_tech.get('languages', []))
                client_frameworks = set(t.lower() for t in client_tech.get('frameworks', []))
                required_tech_lower = set(t.lower() for t in required_tech)
                
                all_client_tech = client_languages.union(client_frameworks)
                matches = len(all_client_tech.intersection(required_tech_lower))
                
                if required_tech:
                    score = min(1.0, matches / len(required_tech))
                    details = {
                        'client_value': list(all_client_tech),
                        'required_value': required_tech,
                        'matches': matches,
                        'match_quality': 'excellent' if score > 0.8 else 'good' if score > 0.6 else 'partial' if score > 0.3 else 'poor'
                    }
            
            elif factor == 'budget_range':
                client_budget = client_profile.get('budget_range', {})
                required_budget = project_requirements.get('estimated_budget', {})
                
                client_max = client_budget.get('max', 0)
                required_min = required_budget.get('min', 0)
                required_max = required_budget.get('max', float('inf'))
                
                if client_max >= required_min:
                    if client_max >= required_max:
                        score = 1.0  # Client budget exceeds requirements
                    else:
                        score = 0.7  # Client budget covers minimum but not ideal
                else:
                    score = max(0.0, client_max / required_min)  # Partial coverage
                
                details = {
                    'client_value': client_budget,
                    'required_value': required_budget,
                    'match_quality': 'excellent' if score > 0.9 else 'good' if score > 0.7 else 'adequate' if score > 0.5 else 'insufficient'
                }
            
            elif factor == 'timeline_expectations':
                client_timeline = client_profile.get('preferred_timeline', {})
                required_timeline = project_requirements.get('timeline', {})
                
                client_duration = client_timeline.get('max_duration_months', 12)
                required_duration = required_timeline.get('duration_months', 6)
                
                if client_duration >= required_duration:
                    score = 1.0
                else:
                    score = max(0.0, client_duration / required_duration)
                
                details = {
                    'client_value': client_timeline,
                    'required_value': required_timeline,
                    'match_quality': 'compatible' if score > 0.9 else 'tight' if score > 0.7 else 'challenging'
                }
            
            elif factor == 'industry_experience':
                client_industries = client_profile.get('industry_experience', [])
                project_industry = project_requirements.get('industry', '')
                
                if project_industry.lower() in [ind.lower() for ind in client_industries]:
                    score = 1.0
                    details['match_quality'] = 'direct_match'
                else:
                    # Check for related industries
                    related_score = await self._calculate_industry_similarity(client_industries, project_industry)
                    score = related_score
                    details['match_quality'] = 'related' if score > 0.5 else 'different'
                
                details.update({
                    'client_value': client_industries,
                    'required_value': project_industry
                })
            
            elif factor == 'team_availability':
                client_team_size = client_profile.get('available_team_size', 0)
                required_team_size = project_requirements.get('estimated_team_size', 5)
                
                if client_team_size >= required_team_size:
                    score = 1.0
                elif client_team_size >= required_team_size * 0.8:
                    score = 0.8
                else:
                    score = max(0.0, client_team_size / required_team_size)
                
                details = {
                    'client_value': client_team_size,
                    'required_value': required_team_size,
                    'match_quality': 'sufficient' if score > 0.8 else 'adequate' if score > 0.6 else 'insufficient'
                }
            
            elif factor == 'risk_tolerance':
                client_risk = client_profile.get('risk_tolerance', 'medium')
                project_risk = project_requirements.get('risk_level', 'medium')
                
                risk_compatibility = {
                    ('low', 'low'): 1.0,
                    ('low', 'medium'): 0.6,
                    ('low', 'high'): 0.2,
                    ('medium', 'low'): 0.8,
                    ('medium', 'medium'): 1.0,
                    ('medium', 'high'): 0.7,
                    ('high', 'low'): 0.9,
                    ('high', 'medium'): 0.9,
                    ('high', 'high'): 1.0
                }
                
                score = risk_compatibility.get((client_risk, project_risk), 0.5)
                details = {
                    'client_value': client_risk,
                    'required_value': project_risk,
                    'match_quality': 'compatible' if score > 0.8 else 'manageable' if score > 0.5 else 'challenging'
                }
            
            # Add more factor comparisons as needed
            else:
                # Generic comparison for other factors
                score = 0.7  # Assume reasonable compatibility
                details = {
                    'client_value': client_profile.get(factor, 'unknown'),
                    'required_value': project_requirements.get(factor, 'unknown'),
                    'match_quality': 'assumed_compatible'
                }
            
            return round(score, 2), details
            
        except Exception as e:
            self.logger.error(f"Factor comparison failed for {factor}: {e}")
            return 0.5, {'error': str(e)}
    
    async def _calculate_industry_similarity(self, client_industries: List[str], 
                                           project_industry: str) -> float:
        """Calculate similarity between client industries and project industry."""
        try:
            # Simple industry similarity mapping (would use more sophisticated matching in production)
            industry_relationships = {
                'finance': ['banking', 'insurance', 'fintech'],
                'healthcare': ['medical', 'pharmaceutical', 'biotech'],
                'technology': ['software', 'it', 'telecommunications'],
                'retail': ['e-commerce', 'consumer goods', 'fashion'],
                'manufacturing': ['automotive', 'industrial', 'aerospace']
            }
            
            project_ind_lower = project_industry.lower()
            client_inds_lower = [ind.lower() for ind in client_industries]
            
            # Check for related industries
            for category, related in industry_relationships.items():
                if project_ind_lower in related or project_ind_lower == category:
                    for client_ind in client_inds_lower:
                        if client_ind in related or client_ind == category:
                            return 0.7  # Related industry experience
            
            return 0.3  # Different but some transferable experience
            
        except Exception as e:
            self.logger.error(f"Industry similarity calculation failed: {e}")
            return 0.5
    
    async def _calculate_compatibility_score(self, category_comparisons: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall compatibility score."""
        try:
            total_weighted_score = sum(cat['weighted_score'] for cat in category_comparisons.values())
            total_weight = sum(cat['weight'] for cat in category_comparisons.values())
            
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Determine compatibility level
            compatibility_level = 'very_poor'
            for level, config in self.compatibility_levels.items():
                if overall_score >= config['min_score']:
                    compatibility_level = level
                    break
            
            level_config = self.compatibility_levels[compatibility_level]
            
            return {
                'overall_score': round(overall_score, 2),
                'max_score': 1.0,
                'percentage': round(overall_score * 100, 1),
                'compatibility_level': compatibility_level,
                'recommendation': level_config['recommendation'],
                'color_indicator': level_config['color']
            }
            
        except Exception as e:
            self.logger.error(f"Compatibility score calculation failed: {e}")
            return {'overall_score': 0.0, 'compatibility_level': 'unknown', 'recommendation': 'Assessment failed'}
    
    async def _analyze_alignment(self, category_comparisons: Dict[str, Dict[str, Any]], 
                               client_profile: Dict[str, Any], 
                               project_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze alignment strengths and gaps."""
        try:
            strengths = []
            gaps = []
            neutral_areas = []
            
            for category, comparison in category_comparisons.items():
                score = comparison['score']
                alignment_level = comparison['alignment_level']
                
                if score >= 0.8:
                    strengths.append({
                        'category': category,
                        'score': score,
                        'description': f"Strong alignment in {category.replace('_', ' ')}"
                    })
                elif score < 0.5:
                    gaps.append({
                        'category': category,
                        'score': score,
                        'gap_size': 0.8 - score,  # Target is 0.8
                        'description': f"Significant gap in {category.replace('_', ' ')}"
                    })
                else:
                    neutral_areas.append({
                        'category': category,
                        'score': score,
                        'description': f"Adequate alignment in {category.replace('_', ' ')}"
                    })
            
            # Sort by score
            strengths.sort(key=lambda x: x['score'], reverse=True)
            gaps.sort(key=lambda x: x['gap_size'], reverse=True)
            
            return {
                'strengths': strengths,
                'gaps': gaps,
                'neutral_areas': neutral_areas,
                'strength_count': len(strengths),
                'gap_count': len(gaps),
                'overall_balance': 'strength_heavy' if len(strengths) > len(gaps) else 'gap_heavy' if len(gaps) > len(strengths) else 'balanced'
            }
            
        except Exception as e:
            self.logger.error(f"Alignment analysis failed: {e}")
            return {}
    
    async def _generate_compatibility_recommendations(self, compatibility_score: Dict[str, Any], 
                                                   alignment_analysis: Dict[str, Any], 
                                                   category_comparisons: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate recommendations based on compatibility analysis."""
        try:
            recommendations = []
            
            compatibility_level = compatibility_score['compatibility_level']
            
            # Overall recommendations based on compatibility level
            if compatibility_level == 'excellent':
                recommendations.append({
                    'type': 'positive',
                    'priority': 'low',
                    'recommendation': 'Proceed with confidence - excellent client-project fit',
                    'rationale': 'High compatibility across all assessment categories'
                })
            
            elif compatibility_level == 'good':
                recommendations.append({
                    'type': 'positive',
                    'priority': 'low',
                    'recommendation': 'Recommended engagement with minor adjustments',
                    'rationale': 'Good overall compatibility with manageable gaps'
                })
            
            elif compatibility_level == 'fair':
                recommendations.append({
                    'type': 'caution',
                    'priority': 'medium',
                    'recommendation': 'Consider engagement with significant preparation',
                    'rationale': 'Moderate compatibility requiring careful planning'
                })
            
            elif compatibility_level in ['poor', 'very_poor']:
                recommendations.append({
                    'type': 'warning',
                    'priority': 'high',
                    'recommendation': 'Recommend against engagement without major changes',
                    'rationale': 'Low compatibility indicates high risk of project challenges'
                })
            
            # Specific recommendations for gaps
            gaps = alignment_analysis.get('gaps', [])
            for gap in gaps[:3]:  # Top 3 gaps
                category = gap['category']
                
                if category == 'technical_alignment':
                    recommendations.append({
                        'type': 'technical',
                        'priority': 'high',
                        'recommendation': 'Provide technical training or augment team with external expertise',
                        'rationale': f'Technical alignment score of {gap["score"]} indicates skill gaps'
                    })
                
                elif category == 'resource_alignment':
                    recommendations.append({
                        'type': 'resource',
                        'priority': 'high',
                        'recommendation': 'Adjust project scope or timeline to match available resources',
                        'rationale': f'Resource constraints identified with alignment score of {gap["score"]}'
                    })
                
                elif category == 'cultural_alignment':
                    recommendations.append({
                        'type': 'cultural',
                        'priority': 'medium',
                        'recommendation': 'Implement change management and communication protocols',
                        'rationale': 'Cultural misalignment can impact project execution'
                    })
            
            # Leverage strengths
            strengths = alignment_analysis.get('strengths', [])
            if strengths:
                top_strength = strengths[0]
                recommendations.append({
                    'type': 'leverage',
                    'priority': 'medium',
                    'recommendation': f'Leverage strong {top_strength["category"].replace("_", " ")} alignment',
                    'rationale': f'Excellent compatibility in this area (score: {top_strength["score"]})'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return []
    
    async def _assess_compatibility_risks(self, alignment_analysis: Dict[str, Any], 
                                        category_comparisons: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Assess risks based on compatibility gaps."""
        try:
            risks = []
            risk_score = 0.0
            
            gaps = alignment_analysis.get('gaps', [])
            
            for gap in gaps:
                category = gap['category']
                gap_size = gap['gap_size']
                
                risk_level = 'high' if gap_size > 0.4 else 'medium' if gap_size > 0.2 else 'low'
                
                risk = {
                    'category': category,
                    'risk_level': risk_level,
                    'gap_size': gap_size,
                    'impact': self._get_risk_impact(category),
                    'mitigation_difficulty': self._get_mitigation_difficulty(category)
                }
                
                risks.append(risk)
                
                # Add to overall risk score
                if risk_level == 'high':
                    risk_score += 0.3
                elif risk_level == 'medium':
                    risk_score += 0.2
                else:
                    risk_score += 0.1
            
            # Determine overall risk level
            if risk_score >= 0.8:
                overall_risk_level = 'high'
            elif risk_score >= 0.4:
                overall_risk_level = 'medium'
            else:
                overall_risk_level = 'low'
            
            return {
                'risks': risks,
                'overall_risk_score': round(risk_score, 2),
                'overall_risk_level': overall_risk_level,
                'risk_count': len(risks),
                'high_risk_count': len([r for r in risks if r['risk_level'] == 'high'])
            }
            
        except Exception as e:
            self.logger.error(f"Risk assessment failed: {e}")
            return {}
    
    def _adjust_weights(self, weighting_preferences: Dict[str, float]) -> Dict[str, float]:
        """Adjust category weights based on preferences."""
        adjusted_weights = {}
        
        for category, config in self.comparison_categories.items():
            if category in weighting_preferences:
                adjusted_weights[category] = weighting_preferences[category]
            else:
                adjusted_weights[category] = config['weight']
        
        # Normalize weights to sum to 1.0
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for category in adjusted_weights:
                adjusted_weights[category] = adjusted_weights[category] / total_weight
        
        return adjusted_weights
    
    def _get_alignment_level(self, score: float) -> str:
        """Get alignment level description based on score."""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.75:
            return 'good'
        elif score >= 0.6:
            return 'fair'
        elif score >= 0.4:
            return 'poor'
        else:
            return 'very_poor'
    
    def _get_risk_impact(self, category: str) -> str:
        """Get risk impact level for a category."""
        impact_mapping = {
            'technical_alignment': 'high',
            'operational_alignment': 'high',
            'business_alignment': 'medium',
            'resource_alignment': 'high',
            'cultural_alignment': 'medium'
        }
        return impact_mapping.get(category, 'medium')
    
    def _get_mitigation_difficulty(self, category: str) -> str:
        """Get mitigation difficulty for a category."""
        difficulty_mapping = {
            'technical_alignment': 'medium',
            'operational_alignment': 'medium',
            'business_alignment': 'low',
            'resource_alignment': 'high',
            'cultural_alignment': 'high'
        }
        return difficulty_mapping.get(category, 'medium')
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get profile comparison statistics."""
        return self.comparison_stats.copy()
