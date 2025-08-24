"""
Content Generator Sub-Agent

Specialized sub-agent for generating proposal content based on requirements analysis,
client profiles, and project specifications. Creates tailored content sections.
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

from ...agents.base_agent import BaseAgent
from ...prompts.proposal_prompts import ProposalPrompts
from ...utils.mock_tools import get_client_details, get_project_details
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from google.generativeai.types import Tool
from google.generativeai.types import GenerationConfig
import os

logger = logging.getLogger(__name__)


class ContentGenerator(BaseAgent):
    """Sub-agent for generating proposal content based on analysis results."""
    
    def __init__(self):
        super().__init__(
            name="Content Generator",
            description="Generates proposal content based on requirements and analysis"
        )
        self.configure_gemini()
        
        # Content sections and their priorities
        self.content_sections = {
            'executive_summary': {
                'priority': 1,
                'required': True,
                'max_length': 500,
                'description': 'High-level overview and key points'
            },
            'project_overview': {
                'priority': 2,
                'required': True,
                'max_length': 800,
                'description': 'Detailed project description and objectives'
            },
            'technical_approach': {
                'priority': 3,
                'required': True,
                'max_length': 1200,
                'description': 'Technical solution and implementation approach'
            },
            'timeline_deliverables': {
                'priority': 4,
                'required': True,
                'max_length': 800,
                'description': 'Project timeline and key deliverables'
            },
            'team_qualifications': {
                'priority': 5,
                'required': True,
                'max_length': 600,
                'description': 'Team expertise and qualifications'
            },
            'budget_pricing': {
                'priority': 6,
                'required': True,
                'max_length': 400,
                'description': 'Project budget and pricing structure'
            },
            'risk_management': {
                'priority': 7,
                'required': False,
                'max_length': 600,
                'description': 'Risk assessment and mitigation strategies'
            },
            'quality_assurance': {
                'priority': 8,
                'required': False,
                'max_length': 400,
                'description': 'Quality assurance and testing approach'
            },
            'client_references': {
                'priority': 9,
                'required': False,
                'max_length': 300,
                'description': 'Relevant client references and case studies'
            },
            'terms_conditions': {
                'priority': 10,
                'required': False,
                'max_length': 400,
                'description': 'Contract terms and conditions'
            }
        }
        
        # Content generation styles
        self.content_styles = {
            'formal': {
                'tone': 'professional and formal',
                'structure': 'traditional business proposal format'
            },
            'technical': {
                'tone': 'detailed and technical',
                'structure': 'technical specification format'
            },
            'consultative': {
                'tone': 'advisory and solution-focused',
                'structure': 'consultative approach format'
            },
            'competitive': {
                'tone': 'competitive and differentiating',
                'structure': 'competitive advantage format'
            }
        }
        
        self.generation_stats = {
            'proposals_generated': 0,
            'avg_word_count': 0,
            'sections_created': 0
        }
        self.model = None
        self.tools = [
            Tool(function_declarations=[
                genai.protos.FunctionDeclaration(
                    name='get_client_details',
                    description='Get details about a client from the CRM.',
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            'client_name': genai.protos.Schema(type=genai.protos.Type.STRING)
                        },
                        required=['client_name']
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name='get_project_details',
                    description='Get details about a project from the project management tool.',
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            'project_name': genai.protos.Schema(type=genai.protos.Type.STRING)
                        },
                        required=['project_name']
                    )
                )
            ])
        ]
        self.tool_functions = {
            "get_client_details": get_client_details,
            "get_project_details": get_project_details,
        }

    def configure_gemini(self):
        """Configure the Gemini API key."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found. Content generation will use templates.")
            return
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate content using Gemini."""
        if not self.model:
            return "Gemini model not configured. Using template."
        try:
            generation_config = GenerationConfig(
                temperature=0.7,
                top_p=1.0,
                top_k=40,
            )
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config,
                tools=self.tools
            )

            if response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                function_name = function_call.name
                function_args = function_call.args

                if function_name in self.tool_functions:
                    function_response = self.tool_functions[function_name](**function_args)

                    response = await self.model.generate_content_async(
                        [
                            prompt,
                            response.candidates[0].content,
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=function_name,
                                    response={"result": function_response},
                                )
                            ),
                        ]
                    )

            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            return f"Error generating content: {e}"

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate proposal content based on analysis results.
        
        Args:
            input_data: Dictionary containing:
                - requirements_analysis: Extracted requirements and analysis
                - client_profile: Client information and preferences
                - project_specifications: Project details and constraints
                - content_preferences: Content style and section preferences
                
        Returns:
            Dictionary containing generated proposal content
        """
        try:
            self.log_operation("Starting content generation", input_data)
            
            requirements_analysis = input_data.get('requirements_analysis', {})
            client_profile = input_data.get('client_profile', {})
            project_specifications = input_data.get('project_specifications', {})
            content_preferences = input_data.get('content_preferences', {})
            
            if not requirements_analysis:
                raise ValueError("Requirements analysis is required for content generation")
            
            # Determine content style and sections to include
            content_style = content_preferences.get('style', 'formal')
            sections_to_include = content_preferences.get('sections', list(self.content_sections.keys()))
            
            # Generate content for each section
            generated_sections = await self._generate_content_sections(
                sections_to_include, requirements_analysis, client_profile, 
                project_specifications, content_style
            )
            
            # Create proposal structure
            proposal_structure = await self._create_proposal_structure(generated_sections)
            
            # Generate executive summary (special handling)
            executive_summary = await self._generate_executive_summary(
                generated_sections, requirements_analysis, client_profile
            )
            
            # Calculate content metrics
            content_metrics = await self._calculate_content_metrics(generated_sections)
            
            # Generate content recommendations
            content_recommendations = await self._generate_content_recommendations(
                generated_sections, content_metrics, requirements_analysis
            )
            
            # Update statistics
            total_word_count = sum(section.get('word_count', 0) for section in generated_sections.values())
            self.generation_stats['proposals_generated'] += 1
            self.generation_stats['avg_word_count'] = (
                (self.generation_stats['avg_word_count'] * (self.generation_stats['proposals_generated'] - 1) + 
                 total_word_count) / self.generation_stats['proposals_generated']
            )
            self.generation_stats['sections_created'] += len(generated_sections)
            
            result = {
                'status': 'success',
                'proposal_id': f"proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generated_sections': generated_sections,
                'proposal_structure': proposal_structure,
                'executive_summary': executive_summary,
                'content_metrics': content_metrics,
                'content_recommendations': content_recommendations,
                'generation_stats': self.generation_stats.copy()
            }
            
            self.log_operation("Content generation completed", {
                'sections_generated': len(generated_sections),
                'total_words': total_word_count
            })
            return result
            
        except Exception as e:
            error_msg = f"Content generation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg
            }
    
    async def _generate_content_sections(self, sections_to_include: List[str], 
                                       requirements_analysis: Dict[str, Any], 
                                       client_profile: Dict[str, Any], 
                                       project_specifications: Dict[str, Any], 
                                       content_style: str) -> Dict[str, Dict[str, Any]]:
        """Generate content for specified sections."""
        try:
            generated_sections = {}
            
            # Sort sections by priority
            sections_sorted = sorted(
                [(section, self.content_sections[section]) for section in sections_to_include 
                 if section in self.content_sections],
                key=lambda x: x[1]['priority']
            )
            
            for section_name, section_config in sections_sorted:
                content = await self._generate_section_content(
                    section_name, requirements_analysis, client_profile, 
                    project_specifications, content_style
                )
                
                generated_sections[section_name] = {
                    'title': section_name.replace('_', ' ').title(),
                    'content': content,
                    'word_count': len(content.split()),
                    'priority': section_config['priority'],
                    'required': section_config['required'],
                    'max_length': section_config['max_length'],
                    'generated_at': datetime.now().isoformat()
                }
            
            return generated_sections
            
        except Exception as e:
            self.logger.error(f"Section generation failed: {e}")
            return {}
    
    async def _generate_section_content(self, section_name: str,
                                      requirements_analysis: Dict[str, Any],
                                      client_profile: Dict[str, Any],
                                      project_specifications: Dict[str, Any],
                                      content_style: str) -> str:
        """Generate content for a specific section using Gemini."""
        if not self.model:
            return await self._generate_generic_content(section_name, requirements_analysis, client_profile, project_specifications)

        try:
            prompt = ProposalPrompts.get_prompt(
                prompt_type=section_name,
                rfp_requirements=requirements_analysis,
                solution_overview=project_specifications,
                differentiators={}, # Placeholder
                client_profile=client_profile,
                win_themes=[], # Placeholder
                technical_requirements=requirements_analysis.get('requirements', {}).get('technical', []),
                technical_solution=project_specifications,
                architecture_overview={}, # Placeholder
                technology_stack=project_specifications.get('technologies', []),
                methodology="Agile", # Placeholder
            )
        except ValueError:
            prompt = ProposalPrompts.get_prompt(
                prompt_type='requirement_response',
                requirement_section=section_name.replace('_', ' ').title(),
                requirements_list=[], # Placeholder
                our_capabilities={}, # Placeholder
                solution_details=project_specifications
            )

        return await self._generate_with_gemini(prompt)

    async def _generate_generic_content(self, section_name: str, 
                                      requirements_analysis: Dict[str, Any], 
                                      client_profile: Dict[str, Any], 
                                      project_specifications: Dict[str, Any]) -> str:
        """Generate generic content for undefined sections."""
        section_title = section_name.replace('_', ' ').title()
        return f"""**{section_title}**

This section provides important information about {section_name.replace('_', ' ')} relevant to your project.

Based on our analysis of your requirements and project specifications, we have developed a comprehensive approach to address all aspects of {section_name.replace('_', ' ')}.

Our team will work closely with you to ensure this area receives appropriate attention and resources throughout the project lifecycle.

Detailed specifications and implementation details for this section will be provided during the project planning phase."""
    
    async def _create_proposal_structure(self, generated_sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create the overall proposal structure."""
        try:
            # Sort sections by priority
            sections_by_priority = sorted(
                generated_sections.items(),
                key=lambda x: x[1]['priority']
            )
            
            structure = {
                'total_sections': len(generated_sections),
                'required_sections': len([s for s in generated_sections.values() if s['required']]),
                'optional_sections': len([s for s in generated_sections.values() if not s['required']]),
                'section_order': [section_name for section_name, _ in sections_by_priority],
                'estimated_page_count': sum(section['word_count'] for section in generated_sections.values()) // 250  # ~250 words per page
            }
            
            return structure
            
        except Exception as e:
            self.logger.error(f"Structure creation failed: {e}")
            return {}
    
    async def _generate_executive_summary(self, generated_sections: Dict[str, Dict[str, Any]], 
                                        requirements_analysis: Dict[str, Any], 
                                        client_profile: Dict[str, Any]) -> str:
        """Generate executive summary from other sections."""
        try:
            client_name = client_profile.get('name', 'Your Organization')
            
            # Extract key points from other sections
            key_points = []
            
            if 'project_overview' in generated_sections:
                key_points.append("Comprehensive solution designed to meet all strategic objectives")
            
            if 'technical_approach' in generated_sections:
                key_points.append("Proven technical approach with industry best practices")
            
            if 'timeline_deliverables' in generated_sections:
                key_points.append("Structured timeline with clear milestones and deliverables")
            
            if 'team_qualifications' in generated_sections:
                key_points.append("Experienced team with relevant expertise and qualifications")
            
            # Add requirements summary
            req_summary = requirements_analysis.get('summary', {})
            total_reqs = req_summary.get('total_requirements', 0)
            
            exec_summary = f"""**Executive Summary**

This proposal presents a comprehensive solution for {client_name}'s project requirements, addressing {total_reqs} distinct requirements across multiple functional and technical domains.

**Key Highlights:**

{chr(10).join(f'• {point}' for point in key_points)}

**Value Proposition:**
Our solution delivers measurable business value through enhanced operational efficiency, improved decision-making capabilities, and reduced operational risks. The investment provides both immediate benefits and long-term strategic value.

**Recommendation:**
We recommend proceeding with this proposal to achieve your strategic objectives while minimizing project risks and ensuring successful delivery within the specified timeline and budget constraints.

**Next Steps:**
Upon approval, we are prepared to begin immediately with project initiation and detailed planning activities."""
            
            return exec_summary
            
        except Exception as e:
            self.logger.error(f"Executive summary generation failed: {e}")
            return "Executive summary could not be generated."
    
    async def _calculate_content_metrics(self, generated_sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate content metrics and statistics."""
        try:
            total_words = sum(section['word_count'] for section in generated_sections.values())
            avg_section_length = total_words / len(generated_sections) if generated_sections else 0
            
            # Count sections by type
            required_sections = len([s for s in generated_sections.values() if s['required']])
            optional_sections = len([s for s in generated_sections.values() if not s['required']])
            
            # Calculate readability metrics (simplified)
            readability_score = 7.5  # Placeholder - would calculate actual readability in production
            
            return {
                'total_word_count': total_words,
                'total_sections': len(generated_sections),
                'required_sections': required_sections,
                'optional_sections': optional_sections,
                'average_section_length': round(avg_section_length, 0),
                'estimated_reading_time_minutes': round(total_words / 200, 1),  # ~200 words per minute
                'estimated_page_count': round(total_words / 250, 1),  # ~250 words per page
                'readability_score': readability_score
            }
            
        except Exception as e:
            self.logger.error(f"Metrics calculation failed: {e}")
            return {}
    
    async def _generate_content_recommendations(self, generated_sections: Dict[str, Dict[str, Any]], 
                                              content_metrics: Dict[str, Any], 
                                              requirements_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations for content improvement."""
        try:
            recommendations = []
            
            total_words = content_metrics.get('total_word_count', 0)
            
            # Length recommendations
            if total_words > 5000:
                recommendations.append({
                    'type': 'length',
                    'priority': 'medium',
                    'recommendation': 'Consider condensing content for better readability',
                    'rationale': f'Current length of {total_words} words may be too detailed for executive review'
                })
            elif total_words < 2000:
                recommendations.append({
                    'type': 'length',
                    'priority': 'low',
                    'recommendation': 'Consider adding more detail to key sections',
                    'rationale': f'Current length of {total_words} words may lack sufficient detail'
                })
            
            # Section balance recommendations
            required_sections = content_metrics.get('required_sections', 0)
            total_sections = content_metrics.get('total_sections', 0)
            
            if required_sections < 5:
                recommendations.append({
                    'type': 'completeness',
                    'priority': 'high',
                    'recommendation': 'Include all essential proposal sections',
                    'rationale': 'Missing key sections may impact proposal effectiveness'
                })
            
            # Content quality recommendations
            recommendations.extend([
                {
                    'type': 'enhancement',
                    'priority': 'medium',
                    'recommendation': 'Add specific client examples and case studies',
                    'rationale': 'Concrete examples increase credibility and relevance'
                },
                {
                    'type': 'enhancement',
                    'priority': 'low',
                    'recommendation': 'Include visual elements and diagrams where appropriate',
                    'rationale': 'Visual elements improve comprehension and engagement'
                }
            ])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Content recommendations generation failed: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get content generation statistics."""
        return self.generation_stats.copy()
