"""
Document analyzer for comprehensive document analysis.

This module provides advanced document analysis capabilities
including structure analysis, content extraction, and metadata processing.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from pathlib import Path
import re
from collections import Counter

logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """Advanced document analysis capabilities."""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """
        Analyze document structure and organization.
        
        Args:
            content: Document content text
            
        Returns:
            Dictionary containing structure analysis
        """
        structure = {
            'total_length': len(content),
            'word_count': len(content.split()),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'sections': self._identify_sections(content),
            'headings': self._extract_headings(content),
            'lists': self._extract_lists(content),
            'tables': self._identify_tables(content),
            'readability_score': self._calculate_readability(content)
        }
        
        return structure
    
    def extract_key_entities(self, content: str) -> Dict[str, List[str]]:
        """
        Extract key entities like dates, amounts, organizations, etc.
        
        Args:
            content: Document content text
            
        Returns:
            Dictionary of entity types and their occurrences
        """
        entities = {
            'dates': self._extract_dates(content),
            'monetary_amounts': self._extract_monetary_amounts(content),
            'percentages': self._extract_percentages(content),
            'organizations': self._extract_organizations(content),
            'email_addresses': self._extract_emails(content),
            'phone_numbers': self._extract_phone_numbers(content),
            'urls': self._extract_urls(content)
        }
        
        return entities
    
    def analyze_content_themes(self, content: str) -> Dict[str, Any]:
        """
        Analyze content themes and topics.
        
        Args:
            content: Document content text
            
        Returns:
            Dictionary containing theme analysis
        """
        words = self._preprocess_text(content)
        word_freq = Counter(words)
        
        themes = {
            'top_keywords': word_freq.most_common(20),
            'technical_terms': self._identify_technical_terms(content),
            'business_terms': self._identify_business_terms(content),
            'action_items': self._extract_action_items(content),
            'requirements_indicators': self._find_requirement_indicators(content)
        }
        
        return themes
    
    def _identify_sections(self, content: str) -> List[Dict[str, Any]]:
        """Identify document sections based on common patterns."""
        sections = []
        
        # Common section patterns
        section_patterns = [
            r'^([A-Z\s]+):?$',  # ALL CAPS headers
            r'^(\d+\.?\s+[A-Z][^.]*):?$',  # Numbered sections
            r'^([A-Z][^.]*):$',  # Title case headers with colon
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    sections.append({
                        'title': match.group(1).strip(),
                        'line_number': i + 1,
                        'type': 'header'
                    })
                    break
        
        return sections
    
    def _extract_headings(self, content: str) -> List[str]:
        """Extract document headings."""
        headings = []
        
        # Markdown-style headings
        markdown_headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        headings.extend(markdown_headings)
        
        # Underlined headings
        lines = content.split('\n')
        for i in range(len(lines) - 1):
            if lines[i].strip() and lines[i + 1].strip():
                if all(c in '-=_' for c in lines[i + 1].strip()):
                    headings.append(lines[i].strip())
        
        return list(set(headings))  # Remove duplicates
    
    def _extract_lists(self, content: str) -> Dict[str, int]:
        """Extract and count different types of lists."""
        bullet_lists = len(re.findall(r'^\s*[•\-\*]\s+', content, re.MULTILINE))
        numbered_lists = len(re.findall(r'^\s*\d+\.?\s+', content, re.MULTILINE))
        lettered_lists = len(re.findall(r'^\s*[a-z]\)\s+', content, re.MULTILINE))
        
        return {
            'bullet_points': bullet_lists,
            'numbered_items': numbered_lists,
            'lettered_items': lettered_lists
        }
    
    def _identify_tables(self, content: str) -> int:
        """Identify potential tables in the content."""
        # Simple table detection based on common patterns
        table_indicators = [
            len(re.findall(r'\|.*\|', content)),  # Pipe-separated
            len(re.findall(r'\t.*\t', content)),  # Tab-separated
            len(re.findall(r'^\s*\w+\s+\w+\s+\w+', content, re.MULTILINE))  # Space-separated columns
        ]
        
        return max(table_indicators)
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate simple readability score."""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        if not words or not sentences:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_syllables_per_word = sum(self._count_syllables(word) for word in words) / len(words)
        
        # Simplified Flesch Reading Ease formula
        score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        return max(0, min(100, score))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (approximation)."""
        word = word.lower().strip('.,!?;')
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        # Handle silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _extract_dates(self, content: str) -> List[str]:
        """Extract date patterns from content."""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
            r'\b\w+\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, content))
        
        return list(set(dates))
    
    def _extract_monetary_amounts(self, content: str) -> List[str]:
        """Extract monetary amounts from content."""
        money_patterns = [
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',  # $1,000.00
            r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|dollars?)',  # 1000 USD
        ]
        
        amounts = []
        for pattern in money_patterns:
            amounts.extend(re.findall(pattern, content, re.IGNORECASE))
        
        return amounts
    
    def _extract_percentages(self, content: str) -> List[str]:
        """Extract percentage values from content."""
        return re.findall(r'\d+(?:\.\d+)?%', content)
    
    def _extract_organizations(self, content: str) -> List[str]:
        """Extract potential organization names."""
        # Simple pattern for organizations (capitalized words)
        org_pattern = r'\b(?:[A-Z][a-z]+\s+){1,3}(?:Inc|LLC|Corp|Company|Ltd|Organization|Agency|Department)\b'
        return re.findall(org_pattern, content)
    
    def _extract_emails(self, content: str) -> List[str]:
        """Extract email addresses."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, content)
    
    def _extract_phone_numbers(self, content: str) -> List[str]:
        """Extract phone numbers."""
        phone_patterns = [
            r'\(\d{3}\)\s*\d{3}-\d{4}',  # (123) 456-7890
            r'\d{3}-\d{3}-\d{4}',        # 123-456-7890
            r'\d{3}\.\d{3}\.\d{4}',      # 123.456.7890
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, content))
        
        return phones
    
    def _extract_urls(self, content: str) -> List[str]:
        """Extract URLs from content."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, content)
    
    def _preprocess_text(self, content: str) -> List[str]:
        """Preprocess text for analysis."""
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', ' ', content.lower())
        words = text.split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        return [word for word in words if len(word) > 2 and word not in stop_words]
    
    def _identify_technical_terms(self, content: str) -> List[str]:
        """Identify technical terms and jargon."""
        technical_indicators = [
            r'\b\w*(?:tion|sion|ment|ness|ity|ism|ics|ogy|ing)\b',  # Technical suffixes
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+(?:-\w+)+\b',  # Hyphenated terms
        ]
        
        technical_terms = []
        for pattern in technical_indicators:
            matches = re.findall(pattern, content)
            technical_terms.extend([term.lower() for term in matches if len(term) > 3])
        
        return list(set(technical_terms))[:20]  # Top 20 unique terms
    
    def _identify_business_terms(self, content: str) -> List[str]:
        """Identify business and commercial terms."""
        business_keywords = [
            'contract', 'agreement', 'proposal', 'budget', 'cost', 'price',
            'timeline', 'deadline', 'deliverable', 'milestone', 'requirement',
            'specification', 'scope', 'objective', 'goal', 'outcome', 'result',
            'client', 'customer', 'vendor', 'supplier', 'stakeholder',
            'management', 'strategy', 'solution', 'service', 'product'
        ]
        
        content_lower = content.lower()
        found_terms = [term for term in business_keywords if term in content_lower]
        
        return found_terms
    
    def _extract_action_items(self, content: str) -> List[str]:
        """Extract potential action items and tasks."""
        action_patterns = [
            r'(?:must|shall|should|will|need to|required to)\s+([^.!?]*)',
            r'action\s+item[:\s]+([^.!?]*)',
            r'todo[:\s]+([^.!?]*)',
            r'task[:\s]+([^.!?]*)',
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            actions.extend([action.strip() for action in matches if len(action.strip()) > 10])
        
        return actions[:10]  # Top 10 action items
    
    def _find_requirement_indicators(self, content: str) -> List[str]:
        """Find phrases that indicate requirements."""
        requirement_phrases = [
            'must have', 'shall provide', 'required to', 'needs to',
            'should include', 'will deliver', 'expected to', 'responsible for'
        ]
        
        found_indicators = []
        content_lower = content.lower()
        
        for phrase in requirement_phrases:
            if phrase in content_lower:
                # Find context around the phrase
                pattern = f'.{{0,50}}{re.escape(phrase)}.{{0,50}}'
                matches = re.findall(pattern, content_lower)
                found_indicators.extend(matches)
        
        return found_indicators[:15]  # Top 15 requirement contexts
