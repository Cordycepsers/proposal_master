"""
Requirement Extractor Sub-Agent

Specialized sub-agent for extracting and categorizing project requirements from RFPs,
project documents, and proposals. Identifies functional, non-functional, and compliance requirements.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set
import asyncio

from ...agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class RequirementExtractor(BaseAgent):
    """Sub-agent for extracting and categorizing project requirements."""
    
    def __init__(self):
        super().__init__(
            name="Requirement Extractor",
            description="Identifies and categorizes project requirements from documents"
        )
        
        # Requirement categories
        self.requirement_types = {
            'functional': ['must', 'shall', 'should', 'will', 'required', 'needs to'],
            'non_functional': ['performance', 'scalability', 'security', 'reliability', 'availability'],
            'compliance': ['comply', 'standard', 'regulation', 'policy', 'guideline', 'certification'],
            'technical': ['technology', 'platform', 'framework', 'language', 'database', 'architecture'],
            'business': ['budget', 'timeline', 'deadline', 'milestone', 'deliverable', 'scope']
        }
        
        # Priority keywords
        self.priority_keywords = {
            'critical': ['critical', 'essential', 'mandatory', 'must have'],
            'high': ['important', 'high priority', 'should have', 'significant'],
            'medium': ['desirable', 'would like', 'preferred', 'nice to have'],
            'low': ['optional', 'if possible', 'future enhancement']
        }
        
        self.extraction_stats = {
            'documents_processed': 0,
            'requirements_extracted': 0,
            'avg_requirements_per_doc': 0.0
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract requirements from document content.
        
        Args:
            input_data: Dictionary containing:
                - content: Document content (text)
                - document_id: Optional document identifier
                - extraction_options: Optional configuration
                
        Returns:
            Dictionary containing extracted requirements and analysis
        """
        try:
            self.log_operation("Starting requirement extraction", input_data)
            
            content = input_data.get('content', '')
            if not content:
                raise ValueError("Content is required for requirement extraction")
            
            document_id = input_data.get('document_id', 'unknown')
            options = input_data.get('extraction_options', {})
            
            # Extract requirements by category
            requirements = await self._extract_requirements(content, options)
            
            # Analyze requirement priorities
            prioritized_requirements = await self._analyze_priorities(requirements)
            
            # Extract compliance requirements
            compliance_requirements = await self._extract_compliance(content)
            
            # Extract technical specifications
            technical_specs = await self._extract_technical_specs(content)
            
            # Generate requirement summary
            summary = await self._generate_summary(prioritized_requirements, compliance_requirements, technical_specs)
            
            # Update statistics
            total_reqs = sum(len(reqs) for reqs in prioritized_requirements.values())
            self.extraction_stats['documents_processed'] += 1
            self.extraction_stats['requirements_extracted'] += total_reqs
            self.extraction_stats['avg_requirements_per_doc'] = (
                self.extraction_stats['requirements_extracted'] / 
                self.extraction_stats['documents_processed']
            )
            
            result = {
                'status': 'success',
                'document_id': document_id,
                'requirements': prioritized_requirements,
                'compliance_requirements': compliance_requirements,
                'technical_specifications': technical_specs,
                'summary': summary,
                'extraction_stats': self.extraction_stats.copy()
            }
            
            self.log_operation("Requirement extraction completed", {
                'document_id': document_id,
                'total_requirements': total_reqs
            })
            return result
            
        except Exception as e:
            error_msg = f"Requirement extraction failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'document_id': input_data.get('document_id', 'unknown')
            }
    
    async def _extract_requirements(self, content: str, options: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract requirements by category from content."""
        try:
            requirements = {req_type: [] for req_type in self.requirement_types.keys()}
            
            # Split content into sentences
            sentences = self._split_into_sentences(content)
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                
                # Check each requirement type
                for req_type, keywords in self.requirement_types.items():
                    if any(keyword in sentence_lower for keyword in keywords):
                        requirement = {
                            'text': sentence.strip(),
                            'type': req_type,
                            'keywords_matched': [kw for kw in keywords if kw in sentence_lower],
                            'confidence': self._calculate_confidence(sentence, keywords)
                        }
                        requirements[req_type].append(requirement)
                        break  # Assign to first matching category
            
            return requirements
            
        except Exception as e:
            self.logger.error(f"Requirement extraction failed: {e}")
            return {req_type: [] for req_type in self.requirement_types.keys()}
    
    async def _analyze_priorities(self, requirements: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze and assign priorities to requirements."""
        try:
            prioritized = {}
            
            for req_type, req_list in requirements.items():
                prioritized[req_type] = []
                
                for req in req_list:
                    text_lower = req['text'].lower()
                    priority = 'medium'  # default
                    
                    # Check priority keywords
                    for priority_level, keywords in self.priority_keywords.items():
                        if any(keyword in text_lower for keyword in keywords):
                            priority = priority_level
                            break
                    
                    req['priority'] = priority
                    req['priority_score'] = self._get_priority_score(priority)
                    prioritized[req_type].append(req)
                
                # Sort by priority score (higher is more important)
                prioritized[req_type].sort(key=lambda x: x['priority_score'], reverse=True)
            
            return prioritized
            
        except Exception as e:
            self.logger.error(f"Priority analysis failed: {e}")
            return requirements
    
    async def _extract_compliance(self, content: str) -> List[Dict[str, Any]]:
        """Extract compliance and regulatory requirements."""
        try:
            compliance_patterns = [
                r'comply with\s+([A-Z][A-Za-z\s]+)',
                r'must meet\s+([A-Z][A-Za-z\s]+)',
                r'adhere to\s+([A-Z][A-Za-z\s]+)',
                r'in accordance with\s+([A-Z][A-Za-z\s]+)',
                r'([A-Z]{2,}[\s\-]\d+)',  # Standards like ISO-9001, NIST-800
            ]
            
            compliance_reqs = []
            
            for pattern in compliance_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    compliance_reqs.append({
                        'requirement': match.group(0),
                        'standard': match.group(1) if match.lastindex else match.group(0),
                        'context': self._get_context(content, match.start(), match.end())
                    })
            
            # Remove duplicates
            seen = set()
            unique_compliance = []
            for req in compliance_reqs:
                key = req['standard'].lower()
                if key not in seen:
                    seen.add(key)
                    unique_compliance.append(req)
            
            return unique_compliance
            
        except Exception as e:
            self.logger.error(f"Compliance extraction failed: {e}")
            return []
    
    async def _extract_technical_specs(self, content: str) -> Dict[str, List[str]]:
        """Extract technical specifications and constraints."""
        try:
            specs = {
                'technologies': [],
                'platforms': [],
                'databases': [],
                'frameworks': [],
                'languages': [],
                'constraints': []
            }
            
            # Technology patterns
            tech_patterns = {
                'technologies': [r'\b(?:Java|Python|JavaScript|Node\.js|React|Angular|Vue)\b'],
                'platforms': [r'\b(?:AWS|Azure|Google Cloud|Docker|Kubernetes)\b'],
                'databases': [r'\b(?:MySQL|PostgreSQL|MongoDB|Oracle|SQL Server)\b'],
                'frameworks': [r'\b(?:Spring|Django|Express|Laravel|Rails)\b'],
                'languages': [r'\b(?:English|Spanish|French|German|Chinese)\b'],
                'constraints': [r'must not exceed\s+([0-9]+)', r'within\s+([0-9]+\s+(?:seconds|minutes|hours))']
            }
            
            content_lower = content.lower()
            
            for spec_type, patterns in tech_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        specs[spec_type].append(match.group(0))
            
            # Remove duplicates
            for spec_type in specs:
                specs[spec_type] = list(set(specs[spec_type]))
            
            return specs
            
        except Exception as e:
            self.logger.error(f"Technical spec extraction failed: {e}")
            return {}
    
    async def _generate_summary(self, requirements: Dict[str, List[Dict[str, Any]]], 
                              compliance: List[Dict[str, Any]], 
                              technical: Dict[str, List[str]]) -> Dict[str, Any]:
        """Generate a summary of extracted requirements."""
        try:
            # Count requirements by type and priority
            req_counts = {}
            priority_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            
            for req_type, req_list in requirements.items():
                req_counts[req_type] = len(req_list)
                for req in req_list:
                    priority = req.get('priority', 'medium')
                    priority_counts[priority] += 1
            
            total_requirements = sum(req_counts.values())
            
            return {
                'total_requirements': total_requirements,
                'requirements_by_type': req_counts,
                'requirements_by_priority': priority_counts,
                'compliance_requirements': len(compliance),
                'technical_specifications': {k: len(v) for k, v in technical.items()},
                'complexity_score': self._calculate_complexity_score(total_requirements, compliance, technical)
            }
            
        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}")
            return {}
    
    def _split_into_sentences(self, content: str) -> List[str]:
        """Split content into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', content)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_confidence(self, sentence: str, keywords: List[str]) -> float:
        """Calculate confidence score for requirement classification."""
        matches = sum(1 for keyword in keywords if keyword in sentence.lower())
        return min(matches / len(keywords), 1.0)
    
    def _get_priority_score(self, priority: str) -> int:
        """Get numeric score for priority level."""
        scores = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        return scores.get(priority, 2)
    
    def _get_context(self, content: str, start: int, end: int, context_size: int = 100) -> str:
        """Get context around a match."""
        context_start = max(0, start - context_size)
        context_end = min(len(content), end + context_size)
        return content[context_start:context_end].strip()
    
    def _calculate_complexity_score(self, total_reqs: int, compliance: List, technical: Dict) -> float:
        """Calculate project complexity score based on requirements."""
        base_score = min(total_reqs * 0.1, 5.0)  # Base score from requirement count
        compliance_score = len(compliance) * 0.5  # Compliance adds complexity
        tech_score = sum(len(specs) for specs in technical.values()) * 0.2
        
        return min(base_score + compliance_score + tech_score, 10.0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        return self.extraction_stats.copy()
