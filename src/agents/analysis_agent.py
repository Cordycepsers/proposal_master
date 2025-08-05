"""
Analysis Agent for RFP and document analysis.

This agent specializes in analyzing RFP documents, extracting requirements,
identifying key criteria, and assessing proposal fit.
"""

from typing import Dict, Any, List, Optional
import re
import json
from src.agents.base_agent import BaseAgent
from src.core.document_processor import DocumentProcessor
from src.prompts.analysis_prompts import AnalysisPrompts


class AnalysisAgent(BaseAgent):
    """Agent specialized in document and RFP analysis using AI prompts."""
    
    def __init__(self, ai_client=None):
        super().__init__(
            name="AnalysisAgent",
            description="Analyzes RFP documents and extracts key requirements, criteria, and constraints using AI"
        )
        self.doc_processor = DocumentProcessor()
        self.prompts = AnalysisPrompts()
        self.ai_client = ai_client  # Could be OpenAI, Anthropic, etc.
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process RFP document and extract analysis using AI prompts.
        
        Args:
            input_data: Dictionary containing document path or content
            
        Returns:
            Analysis results including requirements, criteria, and risks
        """
        self.log_operation("Starting AI-powered RFP analysis", input_data)
        
        try:
            # Extract document content
            content = await self._extract_content(input_data)
            
            # Run multiple analysis tasks using AI prompts
            analysis_result = {}
            
            # 1. Extract requirements using structured AI prompt
            if input_data.get('extract_requirements', True):
                requirements = await self._extract_requirements_with_ai(content)
                analysis_result['requirements'] = requirements
            
            # 2. Analyze evaluation criteria
            if input_data.get('analyze_criteria', True):
                criteria = await self._analyze_evaluation_criteria(content)
                analysis_result['evaluation_criteria'] = criteria
            
            # 3. Perform risk assessment
            if input_data.get('assess_risks', True):
                risks = await self._assess_risks_with_ai(content)
                analysis_result['risks'] = risks
            
            # 4. Generate document summary
            if input_data.get('generate_summary', True):
                summary = await self._generate_document_summary(content)
                analysis_result['document_summary'] = summary
            
            # 5. Calculate win probability if capabilities provided
            if input_data.get('our_capabilities'):
                win_prob = await self._assess_win_probability(content, input_data['our_capabilities'])
                analysis_result['win_probability'] = win_prob
            
            # Add metadata
            analysis_result['metadata'] = {
                'document_length': len(content),
                'analysis_timestamp': self._get_timestamp(),
                'agent_version': '1.0',
                'prompt_version': 'v1.0'
            }
            
            self.log_operation("AI-powered RFP analysis completed", {
                'components_analyzed': len(analysis_result),
                'content_length': len(content)
            })
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")
            return {'error': str(e), 'fallback_analysis': await self._fallback_analysis(input_data)}
    
    async def _extract_requirements_with_ai(self, content: str) -> Dict[str, Any]:
        """Extract requirements using AI with structured prompt."""
        self.log_operation("Extracting requirements with AI")
        
        # Get the structured prompt for requirement extraction
        prompt = self.prompts.get_prompt('requirement_extraction', document_content=content)
        
        if self.ai_client:
            # Use AI client for structured extraction
            try:
                response = await self._call_ai_service(
                    system_prompt=self.prompts.get_system_prompt(),
                    user_prompt=prompt,
                    response_format="json"
                )
                
                # Parse JSON response
                requirements_data = json.loads(response)
                return requirements_data
                
            except Exception as e:
                self.logger.warning(f"AI service failed, using fallback: {e}")
                return await self._fallback_requirement_extraction(content)
        else:
            # Fallback to rule-based extraction
            return await self._fallback_requirement_extraction(content)
    
    async def _analyze_evaluation_criteria(self, content: str) -> Dict[str, Any]:
        """Analyze evaluation criteria using AI prompt."""
        self.log_operation("Analyzing evaluation criteria with AI")
        
        prompt = self.prompts.get_prompt('evaluation_criteria', document_content=content)
        
        if self.ai_client:
            try:
                response = await self._call_ai_service(
                    system_prompt=self.prompts.get_system_prompt(),
                    user_prompt=prompt
                )
                
                return {
                    'ai_analysis': response,
                    'extraction_method': 'ai_powered',
                    'confidence': 'high'
                }
                
            except Exception as e:
                self.logger.warning(f"AI service failed for criteria analysis: {e}")
                return await self._fallback_criteria_analysis(content)
        else:
            return await self._fallback_criteria_analysis(content)
    
    async def _assess_risks_with_ai(self, content: str) -> Dict[str, Any]:
        """Perform risk assessment using AI prompt."""
        self.log_operation("Performing AI-powered risk assessment")
        
        prompt = self.prompts.get_prompt('risk_assessment', document_content=content)
        
        if self.ai_client:
            try:
                response = await self._call_ai_service(
                    system_prompt=self.prompts.get_system_prompt(),
                    user_prompt=prompt
                )
                
                return {
                    'risk_analysis': response,
                    'assessment_method': 'ai_powered',
                    'risk_categories': ['technical', 'schedule', 'commercial', 'competitive'],
                    'overall_risk_level': self._extract_risk_level_from_response(response)
                }
                
            except Exception as e:
                self.logger.warning(f"AI service failed for risk assessment: {e}")
                return await self._fallback_risk_assessment(content)
        else:
            return await self._fallback_risk_assessment(content)
    
    async def _generate_document_summary(self, content: str) -> Dict[str, Any]:
        """Generate executive summary using AI prompt."""
        self.log_operation("Generating document summary with AI")
        
        prompt = self.prompts.get_prompt('document_summary', document_content=content)
        
        if self.ai_client:
            try:
                response = await self._call_ai_service(
                    system_prompt=self.prompts.get_system_prompt(),
                    user_prompt=prompt
                )
                
                return {
                    'executive_summary': response,
                    'generation_method': 'ai_powered',
                    'summary_length': len(response),
                    'key_topics_covered': self._extract_topics_from_summary(response)
                }
                
            except Exception as e:
                self.logger.warning(f"AI service failed for summary generation: {e}")
                return await self._fallback_summary_generation(content)
        else:
            return await self._fallback_summary_generation(content)
    
    async def _assess_win_probability(self, rfp_content: str, our_capabilities: str) -> Dict[str, Any]:
        """Assess win probability using AI prompt."""
        self.log_operation("Assessing win probability with AI")
        
        prompt = self.prompts.get_prompt(
            'win_probability',
            document_content=rfp_content,
            our_capabilities=our_capabilities
        )
        
        if self.ai_client:
            try:
                response = await self._call_ai_service(
                    system_prompt=self.prompts.get_system_prompt(),
                    user_prompt=prompt
                )
                
                return {
                    'win_assessment': response,
                    'assessment_method': 'ai_powered',
                    'probability_score': self._extract_probability_from_response(response),
                    'key_factors': self._extract_win_factors_from_response(response)
                }
                
            except Exception as e:
                self.logger.warning(f"AI service failed for win probability: {e}")
                return await self._fallback_win_probability(rfp_content, our_capabilities)
        else:
            return await self._fallback_win_probability(rfp_content, our_capabilities)
    
    async def _call_ai_service(self, system_prompt: str, user_prompt: str, response_format: str = "text") -> str:
        """
        Call AI service with prompts (OpenAI, Anthropic, etc.).
        
        This is a placeholder for actual AI service integration.
        """
        if not self.ai_client:
            raise ValueError("No AI client configured")
        
        # Example structure for different AI services
        if hasattr(self.ai_client, 'chat'):
            # OpenAI-style API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.ai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        elif hasattr(self.ai_client, 'messages'):
            # Anthropic-style API
            response = await self.ai_client.messages.create(
                model="claude-3-sonnet-20240229",
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.1,
                max_tokens=4000
            )
            
            return response.content[0].text
        
        else:
            # Generic AI client
            return await self.ai_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1
            )
    
    def _extract_risk_level_from_response(self, response: str) -> str:
        """Extract overall risk level from AI response."""
        response_lower = response.lower()
        if 'high risk' in response_lower or 'significant risk' in response_lower:
            return 'high'
        elif 'medium risk' in response_lower or 'moderate risk' in response_lower:
            return 'medium'
        elif 'low risk' in response_lower or 'minimal risk' in response_lower:
            return 'low'
        else:
            return 'unknown'
    
    def _extract_probability_from_response(self, response: str) -> Optional[float]:
        """Extract win probability percentage from AI response."""
        import re
        
        # Look for percentage patterns
        percentage_patterns = [
            r'(\d+(?:\.\d+)?)%',
            r'probability[:\s]+(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*percent'
        ]
        
        for pattern in percentage_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0]) / 100 if float(matches[0]) > 1 else float(matches[0])
                except ValueError:
                    continue
        
        return None
    
    def _extract_topics_from_summary(self, summary: str) -> List[str]:
        """Extract key topics from AI-generated summary."""
        # Simple topic extraction based on common summary patterns
        topics = []
        
        # Look for bullet points or numbered lists
        bullet_points = re.findall(r'[•\-\*]\s*([^.\n]+)', summary)
        topics.extend([point.strip() for point in bullet_points])
        
        # Look for section headers with colons
        headers = re.findall(r'\*\*([^*]+)\*\*:', summary)
        topics.extend([header.strip() for header in headers])
        
        return topics[:10]  # Return top 10 topics
    
    def _extract_win_factors_from_response(self, response: str) -> List[str]:
        """Extract key win factors from AI response."""
        factors = []
        
        # Look for common factor indicators
        factor_patterns = [
            r'(?:key factors?|success factors?|win factors?)[:\s]*([^.]+)',
            r'(?:strengths?|advantages?)[:\s]*([^.]+)',
            r'(?:opportunities?|differentiators?)[:\s]*([^.]+)'
        ]
        
        for pattern in factor_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            factors.extend([match.strip() for match in matches])
        
        return factors[:5]  # Return top 5 factors
    
    # Fallback methods (original rule-based analysis)
    async def _fallback_requirement_extraction(self, content: str) -> Dict[str, Any]:
        """Fallback requirement extraction using rules."""
        requirements = self._extract_requirements(content)  # Original method
        return {
            'requirements': requirements,
            'extraction_method': 'rule_based',
            'confidence': 'medium',
            'total_requirements': len(requirements)
        }
    
    async def _fallback_criteria_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback criteria analysis using rules."""
        criteria = self._extract_evaluation_criteria(content)  # Original method
        return {
            'criteria': criteria,
            'analysis_method': 'rule_based',
            'confidence': 'medium'
        }
    
    async def _fallback_risk_assessment(self, content: str) -> Dict[str, Any]:
        """Fallback risk assessment using rules."""
        risks = self._assess_risks(content, [])  # Original method
        return {
            'risks': risks,
            'assessment_method': 'rule_based',
            'overall_risk_level': 'medium'
        }
    
    async def _fallback_summary_generation(self, content: str) -> Dict[str, Any]:
        """Fallback summary generation using rules."""
        # Simple extractive summary
        sentences = content.split('.')[:5]  # First 5 sentences
        summary = '. '.join(sentences) + '.'
        
        return {
            'executive_summary': summary,
            'generation_method': 'extractive',
            'summary_length': len(summary)
        }
    
    async def _fallback_win_probability(self, rfp_content: str, our_capabilities: str) -> Dict[str, Any]:
        """Fallback win probability assessment."""
        probability = self._estimate_win_probability(rfp_content, [])  # Original method
        
        return {
            'win_probability': probability,
            'assessment_method': 'rule_based',
            'confidence': 'low'
        }
    
    async def _fallback_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete fallback analysis using original methods."""
        content = await self._extract_content(input_data)
        
        requirements = self._extract_requirements(content)
        criteria = self._extract_evaluation_criteria(content)
        constraints = self._extract_constraints(content)
        timeline = self._extract_timeline(content)
        budget = self._extract_budget_info(content)
        risks = self._assess_risks(content, requirements)
        
        return {
            'requirements': requirements,
            'evaluation_criteria': criteria,
            'constraints': constraints,
            'timeline': timeline,
            'budget': budget,
            'risks': risks,
            'complexity_score': self._calculate_complexity(requirements, constraints),
            'win_probability': self._estimate_win_probability(content, requirements),
            'analysis_method': 'fallback_rules'
        }
    
    async def _extract_content(self, input_data: Dict[str, Any]) -> str:
        """Extract content from input data."""
        if 'content' in input_data:
            return input_data['content']
        elif 'file_path' in input_data:
            from pathlib import Path
            doc_info = self.doc_processor.process_document(Path(input_data['file_path']))
            return doc_info['content']
        else:
            raise ValueError("No content or file_path provided in input_data")
    
    def _extract_requirements(self, content: str) -> List[Dict[str, Any]]:
        """Extract functional and non-functional requirements."""
        requirements = []
        
        # Patterns for requirement identification
        patterns = [
            r'(?i)(?:must|shall|should|required?)\s+(.{10,100})',  # Modal verbs
            r'(?i)requirement[s]?[:\s]+(.{10,100})',  # Explicit requirements
            r'(?i)the\s+system\s+(?:must|shall|should)\s+(.{10,100})',  # System requirements
            r'(?i)deliverable[s]?[:\s]+(.{10,100})',  # Deliverables
        ]
        
        req_id = 1
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                clean_req = match.strip().rstrip('.,;')
                if len(clean_req) > 10:  # Filter out very short matches
                    requirements.append({
                        'id': f'REQ-{req_id:03d}',
                        'text': clean_req,
                        'type': 'functional',
                        'priority': 'high' if any(word in clean_req.lower() for word in ['must', 'shall', 'critical']) else 'medium'
                    })
                    req_id += 1
        
        return requirements[:20]  # Limit to top 20 requirements
    
    def _extract_evaluation_criteria(self, content: str) -> List[Dict[str, str]]:
        """Extract evaluation criteria from the RFP."""
        criteria = []
        
        # Common evaluation criteria patterns
        patterns = [
            r'(?i)evaluat(?:ed|ion)\s+(?:on|based\s+on|criteria)[:\s]+(.{10,100})',
            r'(?i)(?:score|weight|points?)[:\s]+(.{10,100})',
            r'(?i)criteria[:\s]+(.{10,100})',
            r'(?i)technical\s+(?:score|evaluation)[:\s]+(.{10,100})',
            r'(?i)cost\s+(?:score|evaluation)[:\s]+(.{10,100})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                clean_criteria = match.strip().rstrip('.,;')
                if len(clean_criteria) > 10:
                    criteria.append({
                        'text': clean_criteria,
                        'category': self._categorize_criteria(clean_criteria)
                    })
        
        return criteria[:10]  # Limit to top 10 criteria
    
    def _categorize_criteria(self, criteria_text: str) -> str:
        """Categorize evaluation criteria."""
        text_lower = criteria_text.lower()
        
        if any(word in text_lower for word in ['cost', 'price', 'budget', 'financial']):
            return 'cost'
        elif any(word in text_lower for word in ['technical', 'technology', 'solution', 'approach']):
            return 'technical'
        elif any(word in text_lower for word in ['experience', 'qualification', 'team', 'expertise']):
            return 'qualifications'
        elif any(word in text_lower for word in ['schedule', 'timeline', 'delivery', 'time']):
            return 'schedule'
        else:
            return 'other'
    
    def _extract_constraints(self, content: str) -> List[str]:
        """Extract project constraints."""
        constraints = []
        
        # Constraint patterns
        patterns = [
            r'(?i)constraint[s]?[:\s]+(.{10,100})',
            r'(?i)limitation[s]?[:\s]+(.{10,100})',
            r'(?i)restriction[s]?[:\s]+(.{10,100})',
            r'(?i)not\s+(?:allowed|permitted)[:\s]+(.{10,100})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                clean_constraint = match.strip().rstrip('.,;')
                if len(clean_constraint) > 10:
                    constraints.append(clean_constraint)
        
        return constraints[:10]
    
    def _extract_timeline(self, content: str) -> Dict[str, Any]:
        """Extract timeline information."""
        timeline = {}
        
        # Date patterns
        date_patterns = [
            r'(?i)due\s+(?:date|by)[:\s]+(.{5,30})',
            r'(?i)deadline[:\s]+(.{5,30})',
            r'(?i)completion\s+date[:\s]+(.{5,30})',
            r'(?i)project\s+duration[:\s]+(.{5,30})',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            if matches:
                timeline['deadline'] = matches[0].strip()
                break
        
        # Duration patterns
        duration_patterns = [
            r'(?i)(\d+)\s+(?:months?|weeks?|days?)',
            r'(?i)duration[:\s]+(.{5,30})',
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, content)
            if matches:
                timeline['duration'] = matches[0].strip()
                break
        
        return timeline
    
    def _extract_budget_info(self, content: str) -> Dict[str, Any]:
        """Extract budget and cost information."""
        budget = {}
        
        # Budget patterns
        budget_patterns = [
            r'(?i)budget[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)',
            r'(?i)cost[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)',
            r'(?i)\$([0-9,]+(?:\.[0-9]+)?)',
        ]
        
        for pattern in budget_patterns:
            matches = re.findall(pattern, content)
            if matches:
                budget['amount'] = matches[0].replace(',', '')
                break
        
        return budget
    
    def _assess_risks(self, content: str, requirements: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Assess project risks based on content and requirements."""
        risks = []
        
        # Risk indicators
        high_risk_indicators = [
            'aggressive timeline', 'tight deadline', 'complex integration',
            'multiple stakeholders', 'regulatory compliance', 'security requirements'
        ]
        
        content_lower = content.lower()
        req_text = ' '.join([req['text'].lower() for req in requirements])
        
        for indicator in high_risk_indicators:
            if indicator in content_lower or indicator in req_text:
                risks.append({
                    'type': indicator.replace(' ', '_'),
                    'description': f"Potential risk identified: {indicator}",
                    'impact': 'high' if 'deadline' in indicator or 'compliance' in indicator else 'medium'
                })
        
        return risks
    
    def _calculate_complexity(self, requirements: List[Dict[str, Any]], constraints: List[str]) -> float:
        """Calculate project complexity score (0-1)."""
        complexity_factors = [
            len(requirements) * 0.02,  # Number of requirements
            len(constraints) * 0.05,   # Number of constraints
            0.1 if any('integration' in req['text'].lower() for req in requirements) else 0,
            0.1 if any('security' in req['text'].lower() for req in requirements) else 0,
            0.1 if any('compliance' in req['text'].lower() for req in requirements) else 0,
        ]
        
        return min(sum(complexity_factors), 1.0)
    
    def _estimate_win_probability(self, content: str, requirements: List[Dict[str, Any]]) -> float:
        """Estimate win probability based on requirements analysis."""
        # Simplified win probability estimation
        base_probability = 0.3
        
        # Adjust based on various factors
        adjustments = 0
        
        # Clear requirements boost probability
        if len(requirements) > 5:
            adjustments += 0.1
        
        # Complexity factors
        content_lower = content.lower()
        if 'competitive' in content_lower:
            adjustments -= 0.1
        if 'preferred vendor' in content_lower:
            adjustments += 0.2
        if 'lowest cost' in content_lower:
            adjustments -= 0.1
        
        return max(0.1, min(0.9, base_probability + adjustments))
