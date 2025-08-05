"""
Report Generator Sub-Agent

Specialized sub-agent for creating comprehensive research reports and summaries
from gathered literature, competitive intelligence, and analysis results.
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

from ...agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ReportGenerator(BaseAgent):
    """Sub-agent for generating comprehensive research reports and summaries."""
    
    def __init__(self):
        super().__init__(
            name="Report Generator",
            description="Creates comprehensive research reports and summaries"
        )
        
        # Report templates and sections
        self.report_templates = {
            'executive_summary': {
                'sections': ['overview', 'key_findings', 'recommendations', 'next_steps'],
                'max_length': 500
            },
            'technical_report': {
                'sections': ['introduction', 'methodology', 'findings', 'analysis', 'conclusions'],
                'max_length': 2000
            },
            'competitive_analysis': {
                'sections': ['market_overview', 'competitors', 'opportunities', 'threats', 'recommendations'],
                'max_length': 1500
            },
            'literature_review': {
                'sections': ['scope', 'sources', 'key_themes', 'insights', 'implications'],
                'max_length': 1800
            }
        }
        
        # Report formatting options
        self.formatting_options = {
            'markdown': {'extension': '.md', 'headers': '#'},
            'html': {'extension': '.html', 'headers': '<h{}>'},
            'text': {'extension': '.txt', 'headers': ''},
            'structured': {'extension': '.json', 'headers': ''}
        }
        
        self.generation_stats = {
            'reports_generated': 0,
            'avg_report_length': 0,
            'total_sections_created': 0
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive research report from analysis results.
        
        Args:
            input_data: Dictionary containing:
                - report_type: Type of report to generate
                - source_data: Data from various analysis agents
                - report_options: Formatting and content options
                - project_context: Project information for context
                
        Returns:
            Dictionary containing generated report and metadata
        """
        try:
            self.log_operation("Starting report generation", input_data)
            
            report_type = input_data.get('report_type', 'executive_summary')
            source_data = input_data.get('source_data', {})
            report_options = input_data.get('report_options', {})
            project_context = input_data.get('project_context', {})
            
            if not source_data:
                raise ValueError("Source data is required for report generation")
            
            # Get report template
            template = self.report_templates.get(report_type, self.report_templates['executive_summary'])
            
            # Generate report sections
            report_sections = await self._generate_report_sections(template, source_data, project_context)
            
            # Format the report
            formatted_report = await self._format_report(
                report_sections, 
                report_type, 
                report_options.get('format', 'markdown')
            )
            
            # Generate executive summary if needed
            executive_summary = await self._generate_executive_summary(report_sections, source_data)
            
            # Create metadata
            metadata = await self._create_report_metadata(
                report_type, report_sections, source_data, project_context
            )
            
            # Calculate statistics
            report_length = len(formatted_report.get('content', ''))
            self.generation_stats['reports_generated'] += 1
            self.generation_stats['avg_report_length'] = (
                (self.generation_stats['avg_report_length'] * (self.generation_stats['reports_generated'] - 1) + 
                 report_length) / self.generation_stats['reports_generated']
            )
            self.generation_stats['total_sections_created'] += len(report_sections)
            
            result = {
                'status': 'success',
                'report_type': report_type,
                'formatted_report': formatted_report,
                'executive_summary': executive_summary,
                'metadata': metadata,
                'sections': report_sections,
                'generation_stats': self.generation_stats.copy()
            }
            
            self.log_operation("Report generation completed", {
                'report_type': report_type,
                'sections': len(report_sections),
                'length': report_length
            })
            return result
            
        except Exception as e:
            error_msg = f"Report generation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'report_type': input_data.get('report_type', 'unknown')
            }
    
    async def _generate_report_sections(self, template: Dict[str, Any], 
                                      source_data: Dict[str, Any], 
                                      project_context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Generate content for each report section."""
        try:
            sections = {}
            required_sections = template.get('sections', [])
            
            for section_name in required_sections:
                section_content = await self._generate_section_content(
                    section_name, source_data, project_context
                )
                
                sections[section_name] = {
                    'title': section_name.replace('_', ' ').title(),
                    'content': section_content,
                    'word_count': len(section_content.split()),
                    'generated_at': datetime.now().isoformat()
                }
            
            return sections
            
        except Exception as e:
            self.logger.error(f"Section generation failed: {e}")
            return {}
    
    async def _generate_section_content(self, section_name: str, 
                                      source_data: Dict[str, Any], 
                                      project_context: Dict[str, Any]) -> str:
        """Generate content for a specific section."""
        try:
            if section_name == 'overview':
                return await self._generate_overview(source_data, project_context)
            elif section_name == 'key_findings':
                return await self._generate_key_findings(source_data)
            elif section_name == 'recommendations':
                return await self._generate_recommendations(source_data)
            elif section_name == 'methodology':
                return await self._generate_methodology(source_data)
            elif section_name == 'findings':
                return await self._generate_findings(source_data)
            elif section_name == 'analysis':
                return await self._generate_analysis(source_data)
            elif section_name == 'competitors':
                return await self._generate_competitor_analysis(source_data)
            elif section_name == 'sources':
                return await self._generate_sources_section(source_data)
            elif section_name == 'key_themes':
                return await self._generate_key_themes(source_data)
            elif section_name == 'next_steps':
                return await self._generate_next_steps(source_data, project_context)
            else:
                return await self._generate_generic_section(section_name, source_data)
                
        except Exception as e:
            self.logger.error(f"Content generation failed for {section_name}: {e}")
            return f"Content generation failed for {section_name}: {str(e)}"
    
    async def _generate_overview(self, source_data: Dict[str, Any], 
                               project_context: Dict[str, Any]) -> str:
        """Generate overview section."""
        try:
            project_name = project_context.get('name', 'the project')
            project_domain = project_context.get('domain', 'the specified domain')
            
            # Extract key statistics
            stats = []
            
            # Literature search stats
            if 'literature_search' in source_data:
                lit_data = source_data['literature_search']
                total_sources = lit_data.get('summary', {}).get('total_sources_found', 0)
                if total_sources > 0:
                    stats.append(f"{total_sources} relevant sources analyzed")
            
            # Requirement analysis stats
            if 'requirements' in source_data:
                req_data = source_data['requirements']
                if 'summary' in req_data:
                    total_reqs = req_data['summary'].get('total_requirements', 0)
                    if total_reqs > 0:
                        stats.append(f"{total_reqs} requirements identified")
            
            # Risk assessment stats
            if 'risk_assessment' in source_data:
                risk_data = source_data['risk_assessment']
                overall_risk = risk_data.get('overall_risk', {})
                risk_level = overall_risk.get('level', 'unknown')
                stats.append(f"overall risk level: {risk_level}")
            
            stats_text = ". ".join(stats) if stats else "comprehensive analysis completed"
            
            overview = f"""This report presents a comprehensive analysis of {project_name} in {project_domain}. 
The research encompasses literature review, requirement analysis, risk assessment, and competitive intelligence gathering.

Key metrics from this analysis include: {stats_text}.

The findings presented in this report are based on systematic analysis of multiple data sources and provide 
actionable insights for project planning and implementation."""
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Overview generation failed: {e}")
            return "Overview section could not be generated due to data processing error."
    
    async def _generate_key_findings(self, source_data: Dict[str, Any]) -> str:
        """Generate key findings section."""
        try:
            findings = []
            
            # Literature search findings
            if 'literature_search' in source_data:
                lit_data = source_data['literature_search']
                insights = lit_data.get('insights', [])
                for insight in insights[:3]:  # Top 3 insights
                    findings.append(f"• {insight.get('insight', 'Key insight identified')}")
            
            # Risk assessment findings
            if 'risk_assessment' in source_data:
                risk_data = source_data['risk_assessment']
                overall_risk = risk_data.get('overall_risk', {})
                risk_level = overall_risk.get('level', 'unknown')
                findings.append(f"• Project risk level assessed as {risk_level}")
                
                # Add high-risk categories
                risk_assessment = risk_data.get('risk_assessment', {})
                high_risks = [category for category, data in risk_assessment.items() 
                             if data.get('severity') in ['high', 'critical']]
                if high_risks:
                    findings.append(f"• High-risk areas identified: {', '.join(high_risks)}")
            
            # Requirement findings
            if 'requirements' in source_data:
                req_data = source_data['requirements']
                summary = req_data.get('summary', {})
                priority_counts = summary.get('requirements_by_priority', {})
                critical_count = priority_counts.get('critical', 0)
                if critical_count > 0:
                    findings.append(f"• {critical_count} critical requirements identified")
            
            # Competitive intelligence findings
            if 'literature_search' in source_data:
                lit_data = source_data['literature_search']
                competitive_intel = lit_data.get('competitive_intelligence', {})
                market_leaders = competitive_intel.get('market_leaders', [])
                if market_leaders:
                    findings.append(f"• Key market players identified: {', '.join(market_leaders[:3])}")
            
            if not findings:
                findings = ["• Comprehensive analysis completed across all research areas"]
            
            return "\n".join(findings)
            
        except Exception as e:
            self.logger.error(f"Key findings generation failed: {e}")
            return "• Key findings could not be generated due to data processing error."
    
    async def _generate_recommendations(self, source_data: Dict[str, Any]) -> str:
        """Generate recommendations section."""
        try:
            recommendations = []
            
            # Risk-based recommendations
            if 'risk_assessment' in source_data:
                risk_data = source_data['risk_assessment']
                risk_recommendations = risk_data.get('recommendations', [])
                for rec in risk_recommendations[:3]:  # Top 3 recommendations
                    recommendations.append(f"• {rec.get('recommendation', 'Risk mitigation recommended')}")
            
            # Literature-based recommendations
            if 'literature_search' in source_data:
                lit_data = source_data['literature_search']
                summary = lit_data.get('summary', {})
                search_quality = summary.get('search_quality', 'medium')
                
                if search_quality == 'low':
                    recommendations.append("• Consider expanding research scope to gather more relevant sources")
                elif search_quality == 'high':
                    recommendations.append("• Leverage identified high-quality sources for detailed implementation guidance")
            
            # Requirement-based recommendations
            if 'requirements' in source_data:
                req_data = source_data['requirements']
                summary = req_data.get('summary', {})
                complexity_score = summary.get('complexity_score', 0)
                
                if complexity_score > 7:
                    recommendations.append("• Consider phased implementation approach due to high complexity")
                elif complexity_score < 3:
                    recommendations.append("• Project appears well-scoped for standard implementation approach")
            
            # General recommendations
            recommendations.extend([
                "• Establish regular monitoring and review cycles throughout project execution",
                "• Maintain updated documentation of all decisions and changes",
                "• Consider stakeholder communication plan for ongoing project updates"
            ])
            
            return "\n".join(recommendations[:5])  # Limit to 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendations generation failed: {e}")
            return "• Recommendations could not be generated due to data processing error."
    
    async def _generate_methodology(self, source_data: Dict[str, Any]) -> str:
        """Generate methodology section."""
        methodology = """The research methodology employed a multi-faceted approach combining:

1. **Literature Review**: Systematic search across academic and industry sources
2. **Requirement Analysis**: Extraction and categorization of project requirements
3. **Risk Assessment**: Evaluation of technical, operational, and business risks
4. **Content Analysis**: Natural language processing of source documents
5. **Competitive Intelligence**: Market and competitor analysis

Data sources were evaluated for relevance and reliability, with priority given to recent publications and authoritative sources."""
        
        return methodology
    
    async def _generate_findings(self, source_data: Dict[str, Any]) -> str:
        """Generate findings section."""
        try:
            findings_text = "The analysis revealed several key findings:\n\n"
            
            # Compile findings from each data source
            if 'literature_search' in source_data:
                lit_summary = source_data['literature_search'].get('summary', {})
                total_sources = lit_summary.get('total_sources_found', 0)
                findings_text += f"**Literature Analysis**: {total_sources} relevant sources were identified and analyzed. "
                
                quality = lit_summary.get('search_quality', 'medium')
                findings_text += f"The overall quality of sources was rated as {quality}.\n\n"
            
            if 'risk_assessment' in source_data:
                risk_data = source_data['risk_assessment']
                overall_risk = risk_data.get('overall_risk', {})
                findings_text += f"**Risk Assessment**: Overall project risk level determined to be {overall_risk.get('level', 'unknown')} "
                findings_text += f"with a score of {overall_risk.get('score', 0)}/4.0.\n\n"
            
            if 'requirements' in source_data:
                req_summary = source_data['requirements'].get('summary', {})
                total_reqs = req_summary.get('total_requirements', 0)
                findings_text += f"**Requirements Analysis**: {total_reqs} total requirements identified across multiple categories.\n\n"
            
            return findings_text
            
        except Exception as e:
            self.logger.error(f"Findings generation failed: {e}")
            return "Findings section could not be generated due to data processing error."
    
    async def _generate_analysis(self, source_data: Dict[str, Any]) -> str:
        """Generate analysis section."""
        analysis = """Based on the comprehensive data gathering and evaluation process, several patterns and implications emerge:

The convergence of multiple data sources provides confidence in the identified trends and recommendations. 
Cross-validation between literature findings, requirement analysis, and risk assessment strengthens the overall conclusions.

Key analytical insights include the alignment between industry best practices and project requirements, 
as well as the identification of potential challenges that require proactive management."""
        
        return analysis
    
    async def _generate_competitor_analysis(self, source_data: Dict[str, Any]) -> str:
        """Generate competitor analysis section."""
        try:
            if 'literature_search' not in source_data:
                return "Competitive analysis data not available."
            
            competitive_intel = source_data['literature_search'].get('competitive_intelligence', {})
            
            analysis = "**Competitive Landscape Analysis**\n\n"
            
            market_leaders = competitive_intel.get('market_leaders', [])
            if market_leaders:
                analysis += f"**Market Leaders**: {', '.join(market_leaders[:5])}\n\n"
            
            emerging_tech = competitive_intel.get('emerging_technologies', [])
            if emerging_tech:
                analysis += f"**Emerging Technologies**: {', '.join(emerging_tech[:5])}\n\n"
            
            trends = competitive_intel.get('industry_trends', [])
            if trends:
                analysis += f"**Industry Trends**: {', '.join(trends[:5])}\n\n"
            
            if not any([market_leaders, emerging_tech, trends]):
                analysis += "Competitive intelligence data is limited in the current dataset."
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Competitor analysis generation failed: {e}")
            return "Competitor analysis could not be generated due to data processing error."
    
    async def _generate_sources_section(self, source_data: Dict[str, Any]) -> str:
        """Generate sources section."""
        try:
            sources_text = "**Research Sources Summary**\n\n"
            
            if 'literature_search' in source_data:
                search_results = source_data['literature_search'].get('search_results', {})
                
                for category, results in search_results.items():
                    if results:
                        sources_text += f"**{category.title()} Sources** ({len(results)} sources):\n"
                        for result in results[:3]:  # Top 3 per category
                            title = result.get('title', 'Unknown Title')
                            source_type = result.get('source_type', 'unknown')
                            sources_text += f"- {title} ({source_type})\n"
                        sources_text += "\n"
            
            if sources_text == "**Research Sources Summary**\n\n":
                sources_text += "No source data available in current dataset."
            
            return sources_text
            
        except Exception as e:
            self.logger.error(f"Sources section generation failed: {e}")
            return "Sources section could not be generated due to data processing error."
    
    async def _generate_key_themes(self, source_data: Dict[str, Any]) -> str:
        """Generate key themes section."""
        try:
            themes_text = "**Identified Key Themes**\n\n"
            
            if 'literature_search' in source_data:
                insights = source_data['literature_search'].get('insights', [])
                
                for i, insight in enumerate(insights[:5], 1):
                    category = insight.get('category', 'general').title()
                    insight_text = insight.get('insight', 'Theme identified')
                    confidence = insight.get('confidence', 'medium')
                    
                    themes_text += f"{i}. **{category}**: {insight_text} (Confidence: {confidence})\n\n"
            
            if themes_text == "**Identified Key Themes**\n\n":
                themes_text += "No thematic analysis data available in current dataset."
            
            return themes_text
            
        except Exception as e:
            self.logger.error(f"Key themes generation failed: {e}")
            return "Key themes section could not be generated due to data processing error."
    
    async def _generate_next_steps(self, source_data: Dict[str, Any], 
                                 project_context: Dict[str, Any]) -> str:
        """Generate next steps section."""
        next_steps = """**Recommended Next Steps**

1. **Review and Validate Findings**: Conduct stakeholder review of all identified requirements and risk assessments

2. **Develop Implementation Plan**: Create detailed project timeline based on requirement priorities and risk mitigation strategies

3. **Resource Allocation**: Assign appropriate resources based on identified skill requirements and project complexity

4. **Monitoring Framework**: Establish regular checkpoints for progress tracking and risk monitoring

5. **Stakeholder Communication**: Implement communication plan to keep all parties informed of progress and decisions"""
        
        return next_steps
    
    async def _generate_generic_section(self, section_name: str, 
                                      source_data: Dict[str, Any]) -> str:
        """Generate generic section content."""
        return f"**{section_name.replace('_', ' ').title()}**\n\nThis section contains analysis and findings related to {section_name.replace('_', ' ')}. Content is based on the available source data and research findings."
    
    async def _format_report(self, sections: Dict[str, Dict[str, Any]], 
                           report_type: str, output_format: str) -> Dict[str, Any]:
        """Format the report according to specified format."""
        try:
            format_config = self.formatting_options.get(output_format, self.formatting_options['markdown'])
            
            if output_format == 'structured':
                # Return JSON structure
                return {
                    'format': 'json',
                    'content': sections,
                    'extension': format_config['extension']
                }
            
            # Generate formatted text
            content = f"# {report_type.replace('_', ' ').title()} Report\n\n"
            content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            content += "---\n\n"
            
            for section_name, section_data in sections.items():
                title = section_data.get('title', section_name)
                section_content = section_data.get('content', '')
                
                if output_format == 'markdown':
                    content += f"## {title}\n\n{section_content}\n\n"
                elif output_format == 'html':
                    content += f"<h2>{title}</h2>\n<p>{section_content}</p>\n\n"
                else:  # text format
                    content += f"{title.upper()}\n{'=' * len(title)}\n\n{section_content}\n\n"
            
            return {
                'format': output_format,
                'content': content,
                'extension': format_config['extension']
            }
            
        except Exception as e:
            self.logger.error(f"Report formatting failed: {e}")
            return {
                'format': 'text',
                'content': f"Report formatting failed: {str(e)}",
                'extension': '.txt'
            }
    
    async def _generate_executive_summary(self, sections: Dict[str, Dict[str, Any]], 
                                        source_data: Dict[str, Any]) -> str:
        """Generate executive summary from report sections."""
        try:
            summary = "**Executive Summary**\n\n"
            
            # Extract key points from overview and key findings
            if 'overview' in sections:
                overview_content = sections['overview']['content']
                # Take first two sentences
                sentences = overview_content.split('. ')[:2]
                summary += '. '.join(sentences) + ".\n\n"
            
            if 'key_findings' in sections:
                findings_content = sections['key_findings']['content']
                # Take first 3 bullet points
                lines = findings_content.split('\n')[:3]
                summary += "Key findings include:\n" + '\n'.join(lines) + "\n\n"
            
            if 'recommendations' in sections:
                rec_content = sections['recommendations']['content']
                # Take first 2 recommendations
                lines = rec_content.split('\n')[:2]
                summary += "Primary recommendations:\n" + '\n'.join(lines)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Executive summary generation failed: {e}")
            return "Executive summary could not be generated."
    
    async def _create_report_metadata(self, report_type: str, sections: Dict[str, Dict[str, Any]], 
                                    source_data: Dict[str, Any], 
                                    project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for the generated report."""
        try:
            total_words = sum(section.get('word_count', 0) for section in sections.values())
            
            metadata = {
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'sections_count': len(sections),
                'total_word_count': total_words,
                'project_context': project_context,
                'data_sources': list(source_data.keys()),
                'quality_indicators': {
                    'completeness': len(sections) / len(self.report_templates[report_type]['sections']),
                    'word_density': total_words / len(sections) if sections else 0
                }
            }
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata creation failed: {e}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get report generation statistics."""
        return self.generation_stats.copy()
