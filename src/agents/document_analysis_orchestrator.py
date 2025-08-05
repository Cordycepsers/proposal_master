"""
Document Analysis Orchestrator for comprehensive RFP and document analysis.

This orchestrator coordinates the Document Parser Agent, Requirement Extraction Agent,
and Risk Assessment Agent to provide comprehensive document analysis with structured
output including requirement breakdown, risk assessment matrix, critical success
factors, and compliance requirements.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime

from .document_parser_agent import DocumentParserAgent
from .requirement_extraction_agent import RequirementExtractionAgent
from .risk_assessment_agent import RiskAssessmentAgent
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DocumentAnalysisOrchestrator(BaseAgent):
    """
    Orchestrator for comprehensive document analysis workflow.
    
    Coordinates multiple specialized agents to provide:
    - Document parsing and structure analysis
    - Requirement extraction and categorization
    - Risk assessment and mitigation planning
    - Critical success factor identification
    - Compliance requirement analysis
    - Integrated analysis report
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        super().__init__(ai_client)
        
        # Initialize specialized agents
        self.document_parser = DocumentParserAgent(ai_client)
        self.requirement_extractor = RequirementExtractionAgent(ai_client)
        self.risk_assessor = RiskAssessmentAgent(ai_client)
        
        # Analysis configuration
        self.default_config = {
            'parsing_depth': 'comprehensive',
            'extraction_mode': 'hybrid',
            'risk_assessment_depth': 'detailed',
            'include_quantitative_risk': True,
            'generate_compliance_matrix': True,
            'identify_success_factors': True
        }
    
    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process comprehensive document analysis request.
        
        Args:
            inputs: Dictionary containing:
                - file_path: Path to document file (PDF, DOCX, TXT, MD)
                - analysis_config: Configuration for analysis depth and options
                - project_context: Additional project information
                - compliance_standards: List of compliance standards to check
                - output_format: 'detailed', 'executive_summary', or 'both'
        
        Returns:
            Comprehensive analysis report with:
            - Document information and structure
            - Requirement breakdown and analysis
            - Risk assessment matrix
            - Critical success factors
            - Compliance requirements
            - Recommendations and next steps
        """
        try:
            file_path = inputs.get('file_path')
            analysis_config = {**self.default_config, **inputs.get('analysis_config', {})}
            project_context = inputs.get('project_context', {})
            compliance_standards = inputs.get('compliance_standards', [])
            output_format = inputs.get('output_format', 'detailed')
            
            if not file_path or not Path(file_path).exists():
                raise ValueError(f"Invalid file path: {file_path}")
            
            logger.info(f"Starting comprehensive document analysis: {file_path}")
            
            # Initialize analysis result
            analysis_result = {
                'analysis_metadata': {
                    'file_path': str(file_path),
                    'analysis_timestamp': datetime.now().isoformat(),
                    'configuration': analysis_config,
                    'orchestrator_version': '1.0.0'
                },
                'document_analysis': {},
                'requirement_analysis': {},
                'risk_assessment': {},
                'critical_success_factors': [],
                'compliance_analysis': {},
                'integrated_insights': {},
                'recommendations': []
            }
            
            # Phase 1: Document Parsing and Structure Analysis
            logger.info("Phase 1: Document parsing and structure analysis")
            parsing_result = await self.document_parser.process({
                'file_path': file_path,
                'analysis_depth': analysis_config.get('parsing_depth', 'comprehensive'),
                'extract_sections': True,
                'extract_tables': True,
                'identify_requirements': True
            })
            
            analysis_result['document_analysis'] = parsing_result
            document_content = parsing_result.get('document_info', {}).get('content', '')
            
            if not document_content:
                raise ValueError("Failed to extract document content")
            
            # Phase 2: Requirement Extraction and Analysis
            logger.info("Phase 2: Requirement extraction and analysis")
            requirement_result = await self.requirement_extractor.process({
                'document_content': document_content,
                'extraction_mode': analysis_config.get('extraction_mode', 'hybrid'),
                'include_dependencies': True,
                'generate_traceability': True,
                'compliance_focus': compliance_standards
            })
            
            analysis_result['requirement_analysis'] = requirement_result
            
            # Phase 3: Risk Assessment
            logger.info("Phase 3: Risk assessment and analysis")
            risk_result = await self.risk_assessor.process({
                'document_content': document_content,
                'requirements': requirement_result.get('requirements', []),
                'project_context': project_context,
                'assessment_depth': analysis_config.get('risk_assessment_depth', 'detailed'),
                'include_quantitative': analysis_config.get('include_quantitative_risk', True)
            })
            
            analysis_result['risk_assessment'] = risk_result
            
            # Phase 4: Critical Success Factors Analysis
            if analysis_config.get('identify_success_factors', True):
                logger.info("Phase 4: Critical success factors identification")
                success_factors = await self._identify_critical_success_factors(
                    parsing_result, requirement_result, risk_result
                )
                analysis_result['critical_success_factors'] = success_factors
            
            # Phase 5: Compliance Analysis
            if analysis_config.get('generate_compliance_matrix', True) and compliance_standards:
                logger.info("Phase 5: Compliance analysis")
                compliance_analysis = await self._perform_compliance_analysis(
                    document_content, requirement_result, compliance_standards
                )
                analysis_result['compliance_analysis'] = compliance_analysis
            
            # Phase 6: Integrated Analysis and Insights
            logger.info("Phase 6: Integrated analysis and insights")
            integrated_insights = await self._generate_integrated_insights(
                parsing_result, requirement_result, risk_result
            )
            analysis_result['integrated_insights'] = integrated_insights
            
            # Phase 7: Recommendations and Action Items
            logger.info("Phase 7: Recommendations and action items")
            recommendations = await self._generate_comprehensive_recommendations(
                analysis_result
            )
            analysis_result['recommendations'] = recommendations
            
            # Format output based on request
            if output_format == 'executive_summary':
                analysis_result = await self._create_executive_summary(analysis_result)
            elif output_format == 'both':
                analysis_result['executive_summary'] = await self._create_executive_summary(analysis_result)
            
            logger.info("Comprehensive document analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Document analysis orchestration failed: {str(e)}")
            return await self._fallback_analysis(inputs)
    
    async def _identify_critical_success_factors(self, parsing_result: Dict, 
                                               requirement_result: Dict, 
                                               risk_result: Dict) -> List[Dict[str, Any]]:
        """Identify critical success factors from integrated analysis."""
        success_factors = []
        
        # From requirements analysis
        req_factors = requirement_result.get('critical_success_factors', [])
        success_factors.extend(req_factors)
        
        # From risk analysis - high-impact mitigation requirements
        high_risks = risk_result.get('risk_matrix', {}).get('high_risks', [])
        critical_risks = risk_result.get('risk_matrix', {}).get('critical_risks', [])
        
        for risk in high_risks + critical_risks:
            success_factors.append({
                'type': 'risk_mitigation',
                'factor': f"Effective mitigation of {risk.get('title', 'high-impact risk')}",
                'description': risk.get('description', ''),
                'priority': 'high',
                'success_criteria': [
                    'Risk probability reduced below threshold',
                    'Mitigation strategies successfully implemented',
                    'Contingency plans ready for activation'
                ],
                'related_risk_id': risk.get('id')
            })
        
        # From document structure - key sections that indicate critical areas
        sections = parsing_result.get('sections', {})
        
        if 'evaluation' in sections and sections['evaluation']:
            success_factors.append({
                'type': 'evaluation_excellence',
                'factor': 'Meet or exceed all evaluation criteria',
                'description': 'Ensure proposal addresses all evaluation criteria with compelling evidence',
                'priority': 'critical',
                'success_criteria': [
                    'All evaluation criteria fully addressed',
                    'Compelling evidence and differentiation provided',
                    'Scoring optimization achieved'
                ]
            })
        
        if 'timeline' in sections and sections['timeline']:
            success_factors.append({
                'type': 'schedule_adherence',
                'factor': 'Strict adherence to project timeline',
                'description': 'Meet all project milestones and delivery deadlines',
                'priority': 'high',
                'success_criteria': [
                    'All milestones met on schedule',
                    'Buffer time maintained for contingencies',
                    'Regular progress monitoring and adjustment'
                ]
            })
        
        # From requirements complexity
        req_summary = requirement_result.get('analysis_summary', {})
        complex_req_percentage = req_summary.get('risk_metrics', {}).get('high_complexity_percentage', 0)
        
        if complex_req_percentage > 30:
            success_factors.append({
                'type': 'complexity_management',
                'factor': 'Effective management of complex requirements',
                'description': f'Successfully handle {complex_req_percentage:.1f}% of requirements marked as high complexity',
                'priority': 'high',
                'success_criteria': [
                    'Complex requirements broken down into manageable components',
                    'Specialized expertise engaged for complex areas',
                    'Additional validation and testing for complex features'
                ]
            })
        
        # Integrate compliance factors
        compliance_reqs = [r for r in requirement_result.get('requirements', []) 
                          if r.get('type') == 'compliance']
        
        if compliance_reqs:
            success_factors.append({
                'type': 'compliance_assurance',
                'factor': 'Full compliance with all regulatory requirements',
                'description': f'Ensure complete compliance across {len(compliance_reqs)} compliance requirements',
                'priority': 'critical',
                'success_criteria': [
                    'All compliance requirements validated',
                    'Documentation and audit trails maintained',
                    'Regular compliance reviews conducted'
                ]
            })
        
        return success_factors
    
    async def _perform_compliance_analysis(self, document_content: str, 
                                         requirement_result: Dict, 
                                         compliance_standards: List[str]) -> Dict[str, Any]:
        """Perform comprehensive compliance analysis."""
        compliance_analysis = {
            'standards_assessment': {},
            'compliance_matrix': {},
            'gaps_and_risks': [],
            'certification_requirements': [],
            'audit_preparation': {}
        }
        
        # Analyze each compliance standard
        for standard in compliance_standards:
            standard_analysis = {
                'standard_name': standard,
                'requirements_mapped': [],
                'coverage_assessment': 'Not Assessed',
                'compliance_level': 'Unknown',
                'action_items': []
            }
            
            # Map requirements to standard
            for req in requirement_result.get('requirements', []):
                req_standards = req.get('compliance_standards', [])
                req_text = req.get('text', '').lower()
                
                # Check if requirement relates to this standard
                if (standard.lower() in req_text or 
                    any(std.lower() == standard.lower() for std in req_standards)):
                    standard_analysis['requirements_mapped'].append({
                        'requirement_id': req.get('id'),
                        'requirement_text': req.get('text'),
                        'priority': req.get('priority'),
                        'compliance_risk': self._assess_compliance_risk(req, standard)
                    })
            
            # Assess coverage
            mapped_count = len(standard_analysis['requirements_mapped'])
            if mapped_count == 0:
                standard_analysis['coverage_assessment'] = 'No Requirements Identified'
                standard_analysis['compliance_level'] = 'At Risk'
                standard_analysis['action_items'].append('Identify specific requirements for this standard')
            elif mapped_count < 3:
                standard_analysis['coverage_assessment'] = 'Limited Coverage'
                standard_analysis['compliance_level'] = 'Needs Attention'
                standard_analysis['action_items'].append('Expand requirement coverage for comprehensive compliance')
            else:
                standard_analysis['coverage_assessment'] = 'Adequate Coverage'
                standard_analysis['compliance_level'] = 'On Track'
                standard_analysis['action_items'].append('Validate implementation meets standard requirements')
            
            compliance_analysis['standards_assessment'][standard] = standard_analysis
        
        # Generate compliance matrix
        compliance_analysis['compliance_matrix'] = await self._generate_compliance_matrix(
            requirement_result.get('requirements', []), compliance_standards
        )
        
        # Identify gaps and risks
        compliance_analysis['gaps_and_risks'] = await self._identify_compliance_gaps(
            document_content, requirement_result, compliance_standards
        )
        
        # Certification requirements
        compliance_analysis['certification_requirements'] = await self._identify_certification_requirements(
            compliance_standards
        )
        
        return compliance_analysis
    
    async def _generate_integrated_insights(self, parsing_result: Dict, 
                                          requirement_result: Dict, 
                                          risk_result: Dict) -> Dict[str, Any]:
        """Generate integrated insights from all analysis components."""
        insights = {
            'opportunity_assessment': {},
            'complexity_analysis': {},
            'strategic_recommendations': [],
            'win_probability_factors': {},
            'resource_implications': {}
        }
        
        # Opportunity assessment
        total_requirements = len(requirement_result.get('requirements', []))
        mandatory_requirements = len([r for r in requirement_result.get('requirements', []) 
                                    if r.get('priority') == 'mandatory'])
        high_risk_count = len(risk_result.get('risk_matrix', {}).get('high_risks', []))
        critical_risk_count = len(risk_result.get('risk_matrix', {}).get('critical_risks', []))
        
        insights['opportunity_assessment'] = {
            'total_requirements': total_requirements,
            'mandatory_requirements': mandatory_requirements,
            'mandatory_percentage': (mandatory_requirements / max(total_requirements, 1)) * 100,
            'high_risk_count': high_risk_count,
            'critical_risk_count': critical_risk_count,
            'overall_opportunity_risk': self._assess_opportunity_risk(
                mandatory_requirements, total_requirements, high_risk_count, critical_risk_count
            )
        }
        
        # Complexity analysis
        complexity_metrics = requirement_result.get('analysis_summary', {}).get('complexity_breakdown', {})
        overall_risk_score = risk_result.get('risk_matrix', {}).get('overall_metrics', {}).get('average_risk_score', 0)
        
        insights['complexity_analysis'] = {
            'requirement_complexity': complexity_metrics,
            'risk_complexity': overall_risk_score,
            'integration_complexity': self._assess_integration_complexity(parsing_result),
            'overall_complexity_rating': self._calculate_overall_complexity(
                complexity_metrics, overall_risk_score
            )
        }
        
        # Strategic recommendations
        insights['strategic_recommendations'] = await self._generate_strategic_recommendations(
            parsing_result, requirement_result, risk_result
        )
        
        # Win probability factors
        insights['win_probability_factors'] = {
            'positive_factors': self._identify_positive_factors(parsing_result, requirement_result),
            'negative_factors': self._identify_negative_factors(risk_result),
            'differentiation_opportunities': self._identify_differentiation_opportunities(
                requirement_result, risk_result
            ),
            'competitive_advantages': self._assess_competitive_advantages(parsing_result)
        }
        
        # Resource implications
        insights['resource_implications'] = await self._assess_resource_implications(
            requirement_result, risk_result
        )
        
        return insights
    
    async def _generate_comprehensive_recommendations(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations based on integrated analysis."""
        recommendations = []
        
        # Document structure recommendations
        doc_analysis = analysis_result.get('document_analysis', {})
        if doc_analysis.get('document_structure', {}).get('hierarchy_depth', 0) > 5:
            recommendations.append({
                'category': 'document_structure',
                'priority': 'medium',
                'recommendation': 'Create simplified requirement mapping due to complex document structure',
                'rationale': 'Deep hierarchical structure may complicate requirement traceability',
                'action_items': [
                    'Create simplified requirement index',
                    'Map requirements to key sections',
                    'Develop navigation aids for complex sections'
                ]
            })
        
        # Requirement-based recommendations
        req_analysis = analysis_result.get('requirement_analysis', {})
        req_summary = req_analysis.get('analysis_summary', {})
        
        if req_summary.get('risk_metrics', {}).get('high_complexity_percentage', 0) > 40:
            recommendations.append({
                'category': 'requirement_management',
                'priority': 'high',
                'recommendation': 'Implement enhanced requirement management processes',
                'rationale': 'High percentage of complex requirements requires additional oversight',
                'action_items': [
                    'Assign technical leads to complex requirements',
                    'Conduct additional requirement validation sessions',
                    'Plan for iterative requirement refinement'
                ]
            })
        
        # Risk-based recommendations
        risk_analysis = analysis_result.get('risk_assessment', {})
        risk_matrix = risk_analysis.get('risk_matrix', {})
        
        if len(risk_matrix.get('critical_risks', [])) > 0:
            recommendations.append({
                'category': 'risk_management',
                'priority': 'critical',
                'recommendation': 'Establish executive risk oversight committee',
                'rationale': 'Critical risks identified requiring senior management attention',
                'action_items': [
                    'Form risk oversight committee with executive sponsor',
                    'Implement daily risk monitoring for critical risks',
                    'Prepare risk escalation and communication plans'
                ]
            })
        
        # Compliance recommendations
        compliance_analysis = analysis_result.get('compliance_analysis', {})
        if compliance_analysis:
            at_risk_standards = [
                std for std, analysis in compliance_analysis.get('standards_assessment', {}).items()
                if analysis.get('compliance_level') == 'At Risk'
            ]
            
            if at_risk_standards:
                recommendations.append({
                    'category': 'compliance',
                    'priority': 'high',
                    'recommendation': f'Address compliance gaps for {len(at_risk_standards)} standards',
                    'rationale': 'Compliance gaps identified that could impact proposal success',
                    'action_items': [
                        f'Conduct detailed analysis for: {", ".join(at_risk_standards)}',
                        'Engage compliance subject matter experts',
                        'Plan for compliance validation and audit preparation'
                    ]
                })
        
        # Success factor recommendations
        success_factors = analysis_result.get('critical_success_factors', [])
        critical_factors = [f for f in success_factors if f.get('priority') == 'critical']
        
        if critical_factors:
            recommendations.append({
                'category': 'success_factors',
                'priority': 'high',
                'recommendation': 'Establish success factor monitoring and accountability',
                'rationale': f'{len(critical_factors)} critical success factors require dedicated attention',
                'action_items': [
                    'Assign ownership for each critical success factor',
                    'Establish success criteria and measurement methods',
                    'Implement regular success factor review meetings'
                ]
            })
        
        # Resource and timeline recommendations
        integrated_insights = analysis_result.get('integrated_insights', {})
        complexity_rating = integrated_insights.get('complexity_analysis', {}).get('overall_complexity_rating', 'medium')
        
        if complexity_rating in ['high', 'critical']:
            recommendations.append({
                'category': 'resource_planning',
                'priority': 'high',
                'recommendation': 'Augment team with specialized expertise and additional resources',
                'rationale': f'Overall complexity rating of {complexity_rating} requires enhanced capabilities',
                'action_items': [
                    'Identify specialized skills needed for complex areas',
                    'Plan for additional development and testing time',
                    'Consider external expert consultation or partnership'
                ]
            })
        
        # Add strategic recommendations from integrated insights
        strategic_recs = integrated_insights.get('strategic_recommendations', [])
        for strategic_rec in strategic_recs:
            recommendations.append({
                'category': 'strategic',
                'priority': strategic_rec.get('priority', 'medium'),
                'recommendation': strategic_rec.get('title', ''),
                'rationale': strategic_rec.get('rationale', ''),
                'action_items': strategic_rec.get('action_items', [])
            })
        
        return recommendations
    
    async def _create_executive_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary of the comprehensive analysis."""
        summary = {
            'overview': {},
            'key_findings': {},
            'critical_risks': [],
            'success_factors': [],
            'resource_requirements': {},
            'recommendations_summary': [],
            'go_no_go_assessment': {}
        }
        
        # Overview
        doc_info = analysis_result.get('document_analysis', {}).get('document_info', {})
        req_count = len(analysis_result.get('requirement_analysis', {}).get('requirements', []))
        risk_count = len(analysis_result.get('risk_assessment', {}).get('identified_risks', []))
        
        summary['overview'] = {
            'document_name': doc_info.get('file_name', 'Unknown'),
            'document_type': analysis_result.get('document_analysis', {}).get('document_type', 'Unknown'),
            'total_requirements': req_count,
            'total_risks_identified': risk_count,
            'analysis_completion_date': analysis_result.get('analysis_metadata', {}).get('analysis_timestamp', '')
        }
        
        # Key findings
        req_summary = analysis_result.get('requirement_analysis', {}).get('analysis_summary', {})
        risk_metrics = analysis_result.get('risk_assessment', {}).get('risk_matrix', {}).get('overall_metrics', {})
        
        summary['key_findings'] = {
            'mandatory_requirements': req_summary.get('priority_breakdown', {}).get('mandatory', 0),
            'high_complexity_requirements': req_summary.get('complexity_breakdown', {}).get('high', 0),
            'critical_risks': len(analysis_result.get('risk_assessment', {}).get('risk_matrix', {}).get('critical_risks', [])),
            'overall_risk_level': risk_metrics.get('risk_level', 'Unknown'),
            'compliance_standards_analyzed': len(analysis_result.get('compliance_analysis', {}).get('standards_assessment', {}))
        }
        
        # Critical risks (top 3)
        critical_risks = analysis_result.get('risk_assessment', {}).get('risk_matrix', {}).get('critical_risks', [])
        high_risks = analysis_result.get('risk_assessment', {}).get('risk_matrix', {}).get('high_risks', [])
        
        top_risks = (critical_risks + high_risks)[:3]
        summary['critical_risks'] = [
            {
                'title': risk.get('title', ''),
                'category': risk.get('category', ''),
                'risk_score': risk.get('risk_score', 0),
                'primary_mitigation': risk.get('mitigation_strategies', [''])[0] if risk.get('mitigation_strategies') else ''
            }
            for risk in top_risks
        ]
        
        # Success factors (top 3 critical)
        success_factors = analysis_result.get('critical_success_factors', [])
        critical_success_factors = [f for f in success_factors if f.get('priority') == 'critical'][:3]
        
        summary['success_factors'] = [
            {
                'factor': factor.get('factor', ''),
                'type': factor.get('type', ''),
                'description': factor.get('description', '')
            }
            for factor in critical_success_factors
        ]
        
        # Resource requirements
        resource_implications = analysis_result.get('integrated_insights', {}).get('resource_implications', {})
        summary['resource_requirements'] = {
            'estimated_additional_effort': resource_implications.get('additional_effort_estimate', 'To be determined'),
            'specialized_skills_needed': resource_implications.get('specialized_skills', []),
            'budget_impact': resource_implications.get('budget_impact', 'To be assessed')
        }
        
        # Recommendations summary (top 3 by priority)
        all_recommendations = analysis_result.get('recommendations', [])
        top_recommendations = sorted(
            all_recommendations, 
            key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('priority', 'medium'), 2)
        )[:3]
        
        summary['recommendations_summary'] = [
            {
                'recommendation': rec.get('recommendation', ''),
                'priority': rec.get('priority', ''),
                'category': rec.get('category', '')
            }
            for rec in top_recommendations
        ]
        
        # Go/No-Go assessment
        opportunity_assessment = analysis_result.get('integrated_insights', {}).get('opportunity_assessment', {})
        overall_risk = opportunity_assessment.get('overall_opportunity_risk', 'medium')
        
        if overall_risk == 'low':
            go_no_go = 'GO - Low risk opportunity with manageable complexity'
        elif overall_risk == 'medium':
            go_no_go = 'GO with caution - Monitor risks and ensure adequate resources'
        elif overall_risk == 'high':
            go_no_go = 'CONDITIONAL GO - Requires significant risk mitigation and additional resources'
        else:
            go_no_go = 'NO-GO - Risk level too high without substantial risk reduction'
        
        summary['go_no_go_assessment'] = {
            'recommendation': go_no_go,
            'overall_risk_level': overall_risk,
            'key_decision_factors': [
                f"Risk level: {overall_risk}",
                f"Critical risks: {len(critical_risks)}",
                f"Mandatory requirements: {req_summary.get('priority_breakdown', {}).get('mandatory', 0)}",
                f"Complexity rating: {analysis_result.get('integrated_insights', {}).get('complexity_analysis', {}).get('overall_complexity_rating', 'unknown')}"
            ]
        }
        
        return summary
    
    # Helper methods for integrated analysis
    def _assess_compliance_risk(self, requirement: Dict, standard: str) -> str:
        """Assess compliance risk for a requirement against a standard."""
        if requirement.get('priority') == 'mandatory' and requirement.get('complexity') in ['high', 'critical']:
            return 'high'
        elif requirement.get('priority') == 'mandatory':
            return 'medium'
        else:
            return 'low'
    
    async def _generate_compliance_matrix(self, requirements: List[Dict], 
                                        compliance_standards: List[str]) -> Dict[str, Any]:
        """Generate compliance traceability matrix."""
        matrix = {}
        
        for standard in compliance_standards:
            matrix[standard] = {
                'mapped_requirements': [],
                'coverage_percentage': 0,
                'compliance_status': 'Not Assessed'
            }
            
            # Map requirements to standard
            for req in requirements:
                if (standard.lower() in req.get('text', '').lower() or 
                    standard in req.get('compliance_standards', [])):
                    matrix[standard]['mapped_requirements'].append(req.get('id'))
            
            # Calculate coverage
            total_compliance_reqs = len([r for r in requirements if r.get('type') == 'compliance'])
            mapped_count = len(matrix[standard]['mapped_requirements'])
            
            if total_compliance_reqs > 0:
                matrix[standard]['coverage_percentage'] = (mapped_count / total_compliance_reqs) * 100
            
            # Assess status
            if mapped_count == 0:
                matrix[standard]['compliance_status'] = 'No Coverage'
            elif matrix[standard]['coverage_percentage'] < 50:
                matrix[standard]['compliance_status'] = 'Partial Coverage'
            else:
                matrix[standard]['compliance_status'] = 'Good Coverage'
        
        return matrix
    
    async def _identify_compliance_gaps(self, document_content: str, 
                                      requirement_result: Dict, 
                                      compliance_standards: List[str]) -> List[Dict[str, Any]]:
        """Identify potential compliance gaps."""
        gaps = []
        
        for standard in compliance_standards:
            standard_lower = standard.lower()
            
            # Check if standard is mentioned in document
            if standard_lower not in document_content.lower():
                gaps.append({
                    'type': 'missing_standard_reference',
                    'standard': standard,
                    'description': f'Standard {standard} not explicitly referenced in document',
                    'risk_level': 'medium',
                    'recommendation': f'Verify if {standard} compliance is required and add explicit requirements'
                })
            
            # Check for requirements mapped to standard
            mapped_reqs = [r for r in requirement_result.get('requirements', [])
                          if standard in r.get('compliance_standards', []) or 
                             standard_lower in r.get('text', '').lower()]
            
            if not mapped_reqs:
                gaps.append({
                    'type': 'no_requirements_mapped',
                    'standard': standard,
                    'description': f'No specific requirements identified for {standard} compliance',
                    'risk_level': 'high',
                    'recommendation': f'Conduct detailed analysis to identify {standard} requirements'
                })
        
        return gaps
    
    async def _identify_certification_requirements(self, compliance_standards: List[str]) -> List[Dict[str, Any]]:
        """Identify potential certification requirements."""
        certification_map = {
            'ISO 9001': {'type': 'Quality Management', 'audit_required': True},
            'ISO 27001': {'type': 'Information Security', 'audit_required': True},
            'SOC 2': {'type': 'Security Controls', 'audit_required': True},
            'NIST': {'type': 'Cybersecurity Framework', 'audit_required': False},
            'HIPAA': {'type': 'Healthcare Privacy', 'audit_required': True},
            'PCI DSS': {'type': 'Payment Card Security', 'audit_required': True}
        }
        
        certifications = []
        for standard in compliance_standards:
            if standard in certification_map:
                cert_info = certification_map[standard]
                certifications.append({
                    'standard': standard,
                    'certification_type': cert_info['type'],
                    'audit_required': cert_info['audit_required'],
                    'estimated_timeline': '3-6 months' if cert_info['audit_required'] else '1-3 months',
                    'estimated_cost': 'High' if cert_info['audit_required'] else 'Medium'
                })
        
        return certifications
    
    def _assess_opportunity_risk(self, mandatory_reqs: int, total_reqs: int, 
                               high_risks: int, critical_risks: int) -> str:
        """Assess overall opportunity risk level."""
        mandatory_percentage = (mandatory_reqs / max(total_reqs, 1)) * 100
        total_high_risks = high_risks + critical_risks
        
        risk_score = 0
        
        # Mandatory requirement factor
        if mandatory_percentage > 70:
            risk_score += 2
        elif mandatory_percentage > 50:
            risk_score += 1
        
        # Risk factor
        if critical_risks > 0:
            risk_score += 3
        elif high_risks > 3:
            risk_score += 2
        elif high_risks > 0:
            risk_score += 1
        
        if risk_score >= 4:
            return 'critical'
        elif risk_score >= 3:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _assess_integration_complexity(self, parsing_result: Dict) -> str:
        """Assess integration complexity from document structure."""
        tables = parsing_result.get('tables', [])
        sections = parsing_result.get('sections', {})
        
        complexity_score = 0
        
        # Table complexity
        if len(tables) > 5:
            complexity_score += 2
        elif len(tables) > 2:
            complexity_score += 1
        
        # Section complexity
        total_sections = sum(len(section_list) for section_list in sections.values())
        if total_sections > 20:
            complexity_score += 2
        elif total_sections > 10:
            complexity_score += 1
        
        if complexity_score >= 3:
            return 'high'
        elif complexity_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_overall_complexity(self, complexity_metrics: Dict, risk_score: float) -> str:
        """Calculate overall complexity rating."""
        req_complexity_score = 0
        
        high_complex = complexity_metrics.get('high', 0)
        critical_complex = complexity_metrics.get('critical', 0)
        total_reqs = sum(complexity_metrics.values()) if complexity_metrics else 1
        
        high_percentage = ((high_complex + critical_complex) / total_reqs) * 100
        
        if high_percentage > 40:
            req_complexity_score = 3
        elif high_percentage > 25:
            req_complexity_score = 2
        elif high_percentage > 10:
            req_complexity_score = 1
        
        # Combine with risk score (normalized to 0-3 scale)
        normalized_risk_score = min(risk_score / 5.0 * 3, 3)
        
        combined_score = (req_complexity_score + normalized_risk_score) / 2
        
        if combined_score >= 2.5:
            return 'critical'
        elif combined_score >= 2.0:
            return 'high'
        elif combined_score >= 1.0:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_strategic_recommendations(self, parsing_result: Dict, 
                                                requirement_result: Dict, 
                                                risk_result: Dict) -> List[Dict[str, Any]]:
        """Generate strategic recommendations for the opportunity."""
        recommendations = []
        
        # Document complexity strategy
        doc_structure = parsing_result.get('document_structure', {})
        if doc_structure.get('hierarchy_depth', 0) > 4:
            recommendations.append({
                'title': 'Implement structured response approach',
                'priority': 'medium',
                'rationale': 'Complex document structure requires organized response strategy',
                'action_items': [
                    'Create response outline matching RFP structure',
                    'Assign section ownership to team members',
                    'Implement cross-reference validation process'
                ]
            })
        
        # Requirement management strategy
        req_metrics = requirement_result.get('analysis_summary', {}).get('risk_metrics', {})
        if req_metrics.get('high_complexity_percentage', 0) > 30:
            recommendations.append({
                'title': 'Establish technical excellence centers',
                'priority': 'high',
                'rationale': 'High complexity requirements need specialized expertise',
                'action_items': [
                    'Identify technical subject matter experts for complex areas',
                    'Create technical review boards for complex requirements',
                    'Plan additional validation and testing phases'
                ]
            })
        
        # Risk mitigation strategy
        critical_risks = risk_result.get('risk_matrix', {}).get('critical_risks', [])
        if len(critical_risks) > 0:
            recommendations.append({
                'title': 'Implement enterprise risk management framework',
                'priority': 'critical',
                'rationale': f'{len(critical_risks)} critical risks require systematic management',
                'action_items': [
                    'Establish executive risk steering committee',
                    'Implement daily critical risk monitoring',
                    'Prepare comprehensive contingency plans'
                ]
            })
        
        return recommendations
    
    def _identify_positive_factors(self, parsing_result: Dict, requirement_result: Dict) -> List[str]:
        """Identify positive factors for win probability."""
        factors = []
        
        # Clear document structure
        if parsing_result.get('document_structure', {}).get('hierarchy_depth', 0) <= 3:
            factors.append('Well-structured RFP with clear requirements')
        
        # Reasonable requirement complexity
        complexity_metrics = requirement_result.get('analysis_summary', {}).get('complexity_breakdown', {})
        high_complex = complexity_metrics.get('high', 0) + complexity_metrics.get('critical', 0)
        total_reqs = sum(complexity_metrics.values()) if complexity_metrics else 1
        
        if (high_complex / total_reqs) < 0.3:
            factors.append('Manageable requirement complexity profile')
        
        # Good requirement clarity
        if len(requirement_result.get('requirements', [])) > 0:
            factors.append('Requirements successfully extracted and categorized')
        
        return factors
    
    def _identify_negative_factors(self, risk_result: Dict) -> List[str]:
        """Identify negative factors for win probability."""
        factors = []
        
        critical_risks = len(risk_result.get('risk_matrix', {}).get('critical_risks', []))
        high_risks = len(risk_result.get('risk_matrix', {}).get('high_risks', []))
        
        if critical_risks > 0:
            factors.append(f'{critical_risks} critical risks identified')
        
        if high_risks > 5:
            factors.append(f'High number of significant risks ({high_risks})')
        
        overall_risk = risk_result.get('risk_matrix', {}).get('overall_metrics', {}).get('risk_level', '')
        if overall_risk in ['High', 'Critical']:
            factors.append(f'Overall risk level assessed as {overall_risk}')
        
        return factors
    
    def _identify_differentiation_opportunities(self, requirement_result: Dict, 
                                              risk_result: Dict) -> List[str]:
        """Identify opportunities for competitive differentiation."""
        opportunities = []
        
        # Technical differentiation
        tech_reqs = [r for r in requirement_result.get('requirements', []) 
                    if r.get('type') == 'technical']
        if tech_reqs:
            opportunities.append('Technical innovation in solution architecture')
        
        # Risk management differentiation
        if len(risk_result.get('identified_risks', [])) > 10:
            opportunities.append('Comprehensive risk management and mitigation approach')
        
        # Compliance differentiation
        compliance_reqs = [r for r in requirement_result.get('requirements', []) 
                          if r.get('type') == 'compliance']
        if compliance_reqs:
            opportunities.append('Strong compliance and security posture')
        
        return opportunities
    
    def _assess_competitive_advantages(self, parsing_result: Dict) -> List[str]:
        """Assess potential competitive advantages."""
        advantages = []
        
        # Document understanding
        if parsing_result.get('parsing_status') != 'failed':
            advantages.append('Comprehensive understanding of RFP requirements')
        
        # Structured approach
        if parsing_result.get('sections'):
            advantages.append('Systematic analysis of all RFP sections')
        
        # Risk awareness
        advantages.append('Proactive risk identification and mitigation planning')
        
        return advantages
    
    async def _assess_resource_implications(self, requirement_result: Dict, 
                                          risk_result: Dict) -> Dict[str, Any]:
        """Assess resource implications of the opportunity."""
        implications = {
            'additional_effort_estimate': 'To be determined',
            'specialized_skills': [],
            'budget_impact': 'To be assessed',
            'timeline_impact': 'Minimal to moderate',
            'team_augmentation_needed': False
        }
        
        # Analyze requirement complexity
        complexity_metrics = requirement_result.get('analysis_summary', {}).get('complexity_breakdown', {})
        high_complex = complexity_metrics.get('high', 0) + complexity_metrics.get('critical', 0)
        total_reqs = sum(complexity_metrics.values()) if complexity_metrics else 1
        
        if (high_complex / total_reqs) > 0.3:
            implications['additional_effort_estimate'] = '20-40% above baseline'
            implications['team_augmentation_needed'] = True
            implications['specialized_skills'].extend([
                'Senior technical architects',
                'Domain subject matter experts',
                'Additional testing resources'
            ])
        
        # Analyze risk impact
        critical_risks = len(risk_result.get('risk_matrix', {}).get('critical_risks', []))
        if critical_risks > 0:
            implications['budget_impact'] = 'Moderate to significant - contingency budget recommended'
            implications['timeline_impact'] = 'Potentially significant - buffer time needed'
            implications['specialized_skills'].append('Risk management specialist')
        
        # Compliance implications
        compliance_reqs = [r for r in requirement_result.get('requirements', []) 
                          if r.get('type') == 'compliance']
        if len(compliance_reqs) > 5:
            implications['specialized_skills'].append('Compliance and audit specialist')
        
        return implications
    
    async def _fallback_analysis(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when main orchestration fails."""
        logger.info("Using fallback document analysis")
        
        file_path = inputs.get('file_path', 'unknown')
        
        return {
            'analysis_metadata': {
                'file_path': str(file_path),
                'analysis_timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'fallback_used': True
            },
            'document_analysis': {'error': 'Document parsing failed'},
            'requirement_analysis': {'error': 'Requirement extraction failed'},
            'risk_assessment': {'error': 'Risk assessment failed'},
            'critical_success_factors': [],
            'compliance_analysis': {},
            'integrated_insights': {'error': 'Integrated analysis not available'},
            'recommendations': [{
                'category': 'system',
                'priority': 'high',
                'recommendation': 'Manual document analysis required',
                'rationale': 'Automated analysis failed - expert review needed',
                'action_items': [
                    'Engage subject matter experts for manual analysis',
                    'Review document structure and requirements manually',
                    'Conduct manual risk assessment'
                ]
            }],
            'error': 'Comprehensive analysis failed - fallback response provided'
        }
