"""
Document Parser Agent for comprehensive document analysis and extraction.

This agent handles multi-format document parsing with intelligent content extraction,
structure analysis, and metadata extraction optimized for RFP analysis.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import re

from .base_agent import BaseAgent
from ..core.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class DocumentParserAgent(BaseAgent):
    """
    Specialized agent for parsing and analyzing documents.
    
    Capabilities:
    - Multi-format document parsing (PDF, DOCX, TXT, MD)
    - Intelligent content extraction and structuring
    - Metadata analysis and document classification
    - Section identification and hierarchy mapping
    - Table and figure extraction
    - Requirements identification preprocessing
    """
    
    def __init__(self, ai_client: Optional[Any] = None):
        super().__init__(ai_client)
        self.document_processor = DocumentProcessor()
        self.section_patterns = {
            'requirements': [
                r'requirements?\s*section',
                r'technical\s+requirements?',
                r'functional\s+requirements?',
                r'system\s+requirements?',
                r'specifications?',
                r'scope\s+of\s+work'
            ],
            'evaluation': [
                r'evaluation\s+criteria',
                r'scoring\s+method',
                r'selection\s+criteria',
                r'award\s+criteria',
                r'proposal\s+evaluation'
            ],
            'timeline': [
                r'schedule',
                r'timeline',
                r'milestones?',
                r'key\s+dates',
                r'deliverables?\s+schedule'
            ],
            'budget': [
                r'budget',
                r'cost\s+information',
                r'pricing',
                r'financial\s+requirements?',
                r'payment\s+terms'
            ]
        }
    
    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process document parsing request.
        
        Args:
            inputs: Dictionary containing:
                - file_path: Path to document to parse
                - analysis_depth: 'basic', 'detailed', or 'comprehensive'
                - extract_sections: Boolean for section extraction
                - extract_tables: Boolean for table extraction
                - identify_requirements: Boolean for requirement preprocessing
        
        Returns:
            Dictionary containing parsed document analysis
        """
        try:
            file_path = Path(inputs.get('file_path', ''))
            analysis_depth = inputs.get('analysis_depth', 'detailed')
            extract_sections = inputs.get('extract_sections', True)
            extract_tables = inputs.get('extract_tables', True)
            identify_requirements = inputs.get('identify_requirements', True)
            
            logger.info(f"Starting document parsing: {file_path}")
            
            # Process the document
            doc_info = self.document_processor.process_document(file_path)
            
            # Enhanced parsing based on analysis depth
            parsed_result = {
                'document_info': doc_info,
                'parsing_metadata': {
                    'analysis_depth': analysis_depth,
                    'parsing_timestamp': str(asyncio.get_event_loop().time()),
                    'agent_version': '1.0.0'
                }
            }
            
            # Basic analysis
            parsed_result.update(await self._basic_analysis(doc_info))
            
            if analysis_depth in ['detailed', 'comprehensive']:
                # Section extraction
                if extract_sections:
                    parsed_result['sections'] = await self._extract_sections(doc_info['content'])
                
                # Table extraction
                if extract_tables:
                    parsed_result['tables'] = await self._extract_tables(doc_info['content'])
                
                # Requirement preprocessing
                if identify_requirements:
                    parsed_result['requirement_indicators'] = await self._identify_requirement_patterns(doc_info['content'])
            
            if analysis_depth == 'comprehensive':
                # AI-powered analysis if available
                if self.ai_client:
                    parsed_result['ai_analysis'] = await self._ai_document_analysis(doc_info['content'])
                
                # Advanced structure analysis
                parsed_result['document_structure'] = await self._analyze_document_structure(doc_info['content'])
                
                # Content classification
                parsed_result['content_classification'] = await self._classify_content(doc_info['content'])
            
            logger.info(f"Document parsing completed: {len(parsed_result)} analysis components")
            return parsed_result
            
        except Exception as e:
            logger.error(f"Document parsing failed: {str(e)}")
            return await self._fallback_parsing(inputs)
    
    async def _basic_analysis(self, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic document analysis."""
        content = doc_info['content']
        
        # Content statistics
        stats = {
            'word_count': len(content.split()),
            'character_count': len(content),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'line_count': len(content.split('\n'))
        }
        
        # Document type classification
        doc_type = self._classify_document_type(content)
        
        # Key information extraction
        key_info = {
            'document_title': self._extract_title(content),
            'organization': self._extract_organization(content),
            'project_number': self._extract_project_number(content),
            'submission_deadline': self._extract_deadline(content)
        }
        
        return {
            'content_statistics': stats,
            'document_type': doc_type,
            'key_information': key_info
        }
    
    async def _extract_sections(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract and categorize document sections."""
        sections = {}
        
        for category, patterns in self.section_patterns.items():
            sections[category] = []
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Extract section context
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(content), match.end() + 500)
                    section_text = content[start_pos:end_pos]
                    
                    sections[category].append({
                        'pattern_matched': pattern,
                        'position': match.start(),
                        'section_text': section_text.strip(),
                        'confidence': self._calculate_section_confidence(pattern, section_text)
                    })
        
        return sections
    
    async def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract table-like structures from content."""
        tables = []
        
        # Look for table patterns (simplified)
        table_patterns = [
            r'\|[^\n]*\|',  # Markdown-style tables
            r'(?m)^[\w\s]+\t[\w\s\t]+$',  # Tab-separated values
            r'(?m)^[\w\s,]+,[\w\s,]+$'  # Comma-separated values
        ]
        
        for i, pattern in enumerate(table_patterns):
            matches = list(re.finditer(pattern, content))
            if matches:
                tables.append({
                    'table_id': f'table_{i+1}',
                    'pattern_type': ['markdown', 'tab_separated', 'comma_separated'][i],
                    'row_count': len(matches),
                    'content': [match.group() for match in matches[:10]]  # Limit to first 10 rows
                })
        
        return tables
    
    async def _identify_requirement_patterns(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Identify potential requirement statements for further processing."""
        requirement_patterns = {
            'shall_statements': r'(?i)(?:the\s+)?(?:system|solution|contractor|vendor|provider)\s+shall\s+([^.]+)',
            'must_statements': r'(?i)(?:the\s+)?(?:system|solution|contractor|vendor|provider)\s+must\s+([^.]+)',
            'will_statements': r'(?i)(?:the\s+)?(?:system|solution|contractor|vendor|provider)\s+will\s+([^.]+)',
            'required_statements': r'(?i)(?:is\s+)?required\s+to\s+([^.]+)',
            'mandatory_statements': r'(?i)(?:is\s+)?mandatory\s+([^.]+)'
        }
        
        requirement_indicators = {}
        
        for pattern_type, pattern in requirement_patterns.items():
            matches = re.finditer(pattern, content)
            requirement_indicators[pattern_type] = []
            
            for match in matches:
                requirement_indicators[pattern_type].append({
                    'text': match.group(),
                    'requirement_text': match.group(1) if match.groups() else match.group(),
                    'position': match.start(),
                    'confidence': self._calculate_requirement_confidence(match.group())
                })
        
        return requirement_indicators
    
    async def _ai_document_analysis(self, content: str) -> Dict[str, Any]:
        """Perform AI-powered document analysis if AI client is available."""
        try:
            if not self.ai_client:
                return {'status': 'ai_client_not_available'}
            
            analysis_prompt = f"""Analyze this document and provide insights on:
            
1. Document Type and Purpose
2. Key Stakeholders Mentioned
3. Critical Dates and Deadlines
4. Budget or Cost Information
5. Primary Objectives
6. Compliance Requirements
7. Risk Factors
8. Success Criteria

Document Content:
{content[:5000]}...  # Limit content for API

Provide a structured analysis with specific insights."""

            system_prompt = "You are an expert document analyst specializing in RFP and procurement documents. Provide detailed, actionable insights."
            
            response = await self.ai_client.generate(
                system_prompt=system_prompt,
                user_prompt=analysis_prompt
            )
            
            return {
                'status': 'completed',
                'analysis': response,
                'model_used': getattr(self.ai_client, 'model_name', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"AI document analysis failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """Analyze document structure and hierarchy."""
        lines = content.split('\n')
        
        structure = {
            'headings': [],
            'numbered_sections': [],
            'bullet_points': [],
            'hierarchy_depth': 0
        }
        
        heading_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headings
            r'^([A-Z][A-Z\s]+)$',  # All caps headings
            r'^\d+\.\s+(.+)$',  # Numbered headings
            r'^[A-Z]\.\s+(.+)$'  # Letter headings
        ]
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check for headings
            for pattern in heading_patterns:
                match = re.match(pattern, line)
                if match:
                    structure['headings'].append({
                        'line_number': line_num + 1,
                        'text': match.group(1) if match.groups() else line,
                        'level': self._determine_heading_level(line),
                        'pattern_type': pattern
                    })
                    break
            
            # Check for numbered sections
            if re.match(r'^\d+(\.\d+)*\s+', line):
                structure['numbered_sections'].append({
                    'line_number': line_num + 1,
                    'text': line,
                    'level': len(re.match(r'^(\d+(\.\d+)*)', line).group(1).split('.'))
                })
            
            # Check for bullet points
            if re.match(r'^[•\-\*]\s+', line):
                structure['bullet_points'].append({
                    'line_number': line_num + 1,
                    'text': line[2:].strip(),
                    'marker': line[0]
                })
        
        # Calculate hierarchy depth
        if structure['numbered_sections']:
            structure['hierarchy_depth'] = max(
                section['level'] for section in structure['numbered_sections']
            )
        
        return structure
    
    async def _classify_content(self, content: str) -> Dict[str, Any]:
        """Classify document content by type and purpose."""
        classification = {
            'document_categories': [],
            'content_types': [],
            'complexity_indicators': {},
            'domain_classification': []
        }
        
        # Document category classification
        category_keywords = {
            'rfp': ['request for proposal', 'rfp', 'solicitation'],
            'rfq': ['request for quote', 'rfq', 'quotation'],
            'rfi': ['request for information', 'rfi'],
            'contract': ['contract', 'agreement', 'terms and conditions'],
            'sow': ['statement of work', 'sow', 'scope of work'],
            'proposal': ['proposal', 'response', 'submission']
        }
        
        content_lower = content.lower()
        for category, keywords in category_keywords.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            if score > 0:
                classification['document_categories'].append({
                    'category': category,
                    'confidence_score': min(score / 10, 1.0),
                    'keyword_matches': score
                })
        
        # Content type analysis
        content_indicators = {
            'technical_specs': ['specification', 'requirements', 'architecture'],
            'financial_info': ['budget', 'cost', 'price', 'financial'],
            'timeline_info': ['schedule', 'timeline', 'deadline', 'milestone'],
            'compliance_info': ['compliance', 'regulation', 'standard', 'certification']
        }
        
        for content_type, indicators in content_indicators.items():
            score = sum(content_lower.count(indicator) for indicator in indicators)
            if score > 0:
                classification['content_types'].append({
                    'type': content_type,
                    'presence_score': min(score / 5, 1.0)
                })
        
        # Complexity indicators
        classification['complexity_indicators'] = {
            'technical_complexity': self._assess_technical_complexity(content),
            'document_length': len(content.split()),
            'section_count': len(re.findall(r'^\d+\.\s+', content, re.MULTILINE)),
            'requirement_density': len(re.findall(r'(?i)shall|must|will|required', content)) / max(len(content.split()), 1)
        }
        
        return classification
    
    def _classify_document_type(self, content: str) -> str:
        """Classify the type of document based on content analysis."""
        content_lower = content.lower()
        
        type_scores = {
            'rfp': content_lower.count('request for proposal') + content_lower.count('rfp'),
            'rfq': content_lower.count('request for quote') + content_lower.count('rfq'),
            'rfi': content_lower.count('request for information') + content_lower.count('rfi'),
            'contract': content_lower.count('contract') + content_lower.count('agreement'),
            'proposal': content_lower.count('proposal') + content_lower.count('response'),
            'sow': content_lower.count('statement of work') + content_lower.count('scope of work')
        }
        
        return max(type_scores.keys(), key=lambda k: type_scores[k]) if any(type_scores.values()) else 'unknown'
    
    def _extract_title(self, content: str) -> Optional[str]:
        """Extract document title from content."""
        lines = content.split('\n')[:10]  # Check first 10 lines
        
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                # Look for title patterns
                if any(keyword in line.lower() for keyword in ['request for', 'rfp', 'proposal', 'solicitation']):
                    return line
        
        return lines[0].strip() if lines and lines[0].strip() else None
    
    def _extract_organization(self, content: str) -> Optional[str]:
        """Extract organization name from content."""
        # Look for common organization patterns
        org_patterns = [
            r'(?i)(?:issued by|from):\s*([^\n]+)',
            r'(?i)([A-Z][A-Za-z\s&]+(?:Inc|LLC|Corp|Corporation|Company|Department|Agency))',
            r'(?i)(U\.S\.\s+[A-Z][A-Za-z\s]+)',
        ]
        
        for pattern in org_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_project_number(self, content: str) -> Optional[str]:
        """Extract project or solicitation number."""
        number_patterns = [
            r'(?i)(?:project|solicitation|rfp|contract)\s*(?:number|no|#)[\s:]*([A-Z0-9\-]+)',
            r'(?i)([A-Z]{2,}\-\d{4,})',  # Common government format
            r'(?i)(RFP[\-\s]*\d+)',
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_deadline(self, content: str) -> Optional[str]:
        """Extract submission deadline from content."""
        deadline_patterns = [
            r'(?i)(?:due|deadline|submit|submission).*?(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(?i)(?:due|deadline|submit|submission).*?([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'(?i)(?:no later than|by)\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _calculate_section_confidence(self, pattern: str, section_text: str) -> float:
        """Calculate confidence score for section classification."""
        # Simple confidence based on pattern strength and context
        base_confidence = 0.7
        
        # Boost confidence if section has related keywords
        related_keywords = {
            'requirements': ['shall', 'must', 'specification'],
            'evaluation': ['criteria', 'scoring', 'points', 'weight'],
            'timeline': ['date', 'schedule', 'milestone', 'deadline'],
            'budget': ['cost', 'price', 'budget', 'financial']
        }
        
        for category, keywords in related_keywords.items():
            if category in pattern:
                keyword_count = sum(section_text.lower().count(kw) for kw in keywords)
                base_confidence += min(keyword_count * 0.1, 0.3)
                break
        
        return min(base_confidence, 1.0)
    
    def _calculate_requirement_confidence(self, requirement_text: str) -> float:
        """Calculate confidence score for requirement identification."""
        confidence = 0.6
        
        # Boost confidence for strong requirement indicators
        strong_indicators = ['shall', 'must', 'required', 'mandatory']
        weak_indicators = ['should', 'may', 'could', 'preferred']
        
        text_lower = requirement_text.lower()
        
        for indicator in strong_indicators:
            if indicator in text_lower:
                confidence += 0.2
        
        for indicator in weak_indicators:
            if indicator in text_lower:
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _determine_heading_level(self, line: str) -> int:
        """Determine heading level based on formatting."""
        if line.startswith('#'):
            return line.count('#')
        elif re.match(r'^\d+\.\s+', line):
            return 1
        elif re.match(r'^\d+\.\d+\s+', line):
            return 2
        elif line.isupper():
            return 1
        else:
            return 3
    
    def _assess_technical_complexity(self, content: str) -> float:
        """Assess technical complexity of document content."""
        technical_terms = [
            'api', 'architecture', 'database', 'integration', 'security',
            'authentication', 'encryption', 'scalability', 'performance',
            'cloud', 'infrastructure', 'deployment', 'monitoring'
        ]
        
        content_lower = content.lower()
        complexity_score = sum(content_lower.count(term) for term in technical_terms)
        
        # Normalize by document length
        word_count = len(content.split())
        normalized_score = complexity_score / max(word_count / 1000, 1)
        
        return min(normalized_score, 10.0) / 10.0  # Scale to 0-1
    
    async def _fallback_parsing(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback parsing when main processing fails."""
        logger.info("Using fallback document parsing")
        
        try:
            file_path = Path(inputs.get('file_path', ''))
            
            # Basic file information
            if file_path.exists():
                return {
                    'document_info': {
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'file_size': file_path.stat().st_size,
                        'format': file_path.suffix.lower()
                    },
                    'parsing_status': 'fallback_basic_info_only',
                    'error': 'Full parsing failed, basic info extracted'
                }
            else:
                return {
                    'parsing_status': 'failed',
                    'error': f'File not found: {file_path}'
                }
                
        except Exception as e:
            return {
                'parsing_status': 'failed',
                'error': f'Fallback parsing failed: {str(e)}'
            }
