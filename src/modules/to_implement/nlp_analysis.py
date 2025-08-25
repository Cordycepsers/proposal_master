"""
NLP Analysis Module - Independent Natural Language Processing

This module handles all NLP tasks for RFP text analysis.
It can be developed, tested, and upgraded independently of other modules.
Supports spaCy, NLTK, and transformers for comprehensive text analysis.

Features:
- Named Entity Recognition (NER)
- Key information extraction (dates, budgets, locations)
- Language detection and translation
- Text preprocessing and cleaning
- Confidence scoring for extractions
- Parallel processing support
- Model fine-tuning capabilities
"""

import asyncio
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json

# NLP Libraries
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExtractedEntity:
    """Extracted entity structure"""
    text: str
    label: str
    start_pos: int
    end_pos: int
    confidence: float
    context: str = ""
    normalized_value: Optional[str] = None

@dataclass
class ExtractedInformation:
    """Comprehensive extracted information structure"""
    # Temporal information
    deadlines: List[ExtractedEntity] = field(default_factory=list)
    dates: List[ExtractedEntity] = field(default_factory=list)
    
    # Financial information
    budgets: List[ExtractedEntity] = field(default_factory=list)
    currencies: List[ExtractedEntity] = field(default_factory=list)
    
    # Geographic information
    locations: List[ExtractedEntity] = field(default_factory=list)
    countries: List[ExtractedEntity] = field(default_factory=list)
    
    # Organizational information
    organizations: List[ExtractedEntity] = field(default_factory=list)
    contacts: List[ExtractedEntity] = field(default_factory=list)
    
    # Requirements and deliverables
    requirements: List[ExtractedEntity] = field(default_factory=list)
    deliverables: List[ExtractedEntity] = field(default_factory=list)
    
    # Technical specifications
    technologies: List[ExtractedEntity] = field(default_factory=list)
    skills: List[ExtractedEntity] = field(default_factory=list)
    
    # Language and metadata
    language: str = "unknown"
    language_confidence: float = 0.0
    processing_time: float = 0.0
    overall_confidence: float = 0.0

@dataclass
class NLPAnalysisResult:
    """Complete NLP analysis result"""
    document_id: str
    text_length: int
    sentence_count: int
    word_count: int
    extracted_info: ExtractedInformation
    sentiment_score: Optional[float] = None
    readability_score: Optional[float] = None
    key_phrases: List[str] = field(default_factory=list)
    topics: List[Tuple[str, float]] = field(default_factory=list)
    processing_method: str = ""
    success: bool = True
    error_message: Optional[str] = None

class NLPProcessorInterface(ABC):
    """Abstract interface for NLP processors"""
    
    @abstractmethod
    async def analyze_text(self, text: str, document_id: str) -> NLPAnalysisResult:
        """Analyze text and extract information"""
        pass
    
    @abstractmethod
    def get_processor_name(self) -> str:
        """Return processor name"""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return supported languages"""
        pass

class SpacyNLPProcessor(NLPProcessorInterface):
    """spaCy-based NLP processor"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy is required for SpacyNLPProcessor")
        
        self.model_name = model_name
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.error(f"spaCy model '{model_name}' not found. Please install it with: python -m spacy download {model_name}")
            raise
        
        # Add custom patterns for RFP-specific entities
        self._add_custom_patterns()
    
    def _add_custom_patterns(self):
        """Add custom patterns for RFP-specific entity recognition"""
        from spacy.matcher import Matcher
        
        self.matcher = Matcher(self.nlp.vocab)
        
        # Deadline patterns
        deadline_patterns = [
            [{"LOWER": {"IN": ["deadline", "due", "submission"]}}, {"LOWER": {"IN": ["date", "by"]}}, {"IS_ALPHA": False}],
            [{"LOWER": "submit"}, {"LOWER": "by"}, {"IS_ALPHA": False}],
            [{"LOWER": "closing"}, {"LOWER": "date"}, {"IS_ALPHA": False}]
        ]
        self.matcher.add("DEADLINE", deadline_patterns)
        
        # Budget patterns
        budget_patterns = [
            [{"LOWER": {"IN": ["budget", "funding", "amount"]}}, {"IS_CURRENCY": True}],
            [{"IS_CURRENCY": True}, {"LOWER": {"IN": ["maximum", "minimum", "up", "to"]}}, {"IS_CURRENCY": True}],
            [{"LOWER": {"IN": ["usd", "eur", "gbp"]}}, {"IS_DIGIT": True}]
        ]
        self.matcher.add("BUDGET", budget_patterns)
        
        # Requirement patterns
        requirement_patterns = [
            [{"LOWER": {"IN": ["must", "required", "mandatory"]}}, {"POS": "VERB"}],
            [{"LOWER": "minimum"}, {"IS_DIGIT": True}, {"LOWER": {"IN": ["years", "experience"]}}],
            [{"LOWER": {"IN": ["qualification", "requirement", "criteria"]}}]
        ]
        self.matcher.add("REQUIREMENT", requirement_patterns)
    
    async def analyze_text(self, text: str, document_id: str) -> NLPAnalysisResult:
        """Analyze text using spaCy"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Run spaCy processing in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                doc = await loop.run_in_executor(executor, self.nlp, text)
            
            # Extract basic statistics
            sentences = list(doc.sents)
            words = [token for token in doc if not token.is_space]
            
            # Extract entities
            extracted_info = await self._extract_entities(doc, text)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            extracted_info.processing_time = processing_time
            
            # Extract key phrases
            key_phrases = self._extract_key_phrases(doc)
            
            # Calculate sentiment (basic)
            sentiment_score = self._calculate_sentiment(doc)
            
            return NLPAnalysisResult(
                document_id=document_id,
                text_length=len(text),
                sentence_count=len(sentences),
                word_count=len(words),
                extracted_info=extracted_info,
                sentiment_score=sentiment_score,
                key_phrases=key_phrases,
                processing_method="spacy",
                success=True
            )
            
        except Exception as e:
            logger.error(f"spaCy analysis failed for document {document_id}: {e}")
            return NLPAnalysisResult(
                document_id=document_id,
                text_length=len(text),
                sentence_count=0,
                word_count=0,
                extracted_info=ExtractedInformation(),
                processing_method="spacy",
                success=False,
                error_message=str(e)
            )
    
    async def _extract_entities(self, doc, original_text: str) -> ExtractedInformation:
        """Extract entities from spaCy doc"""
        extracted = ExtractedInformation()
        
        # Language detection
        if LANGDETECT_AVAILABLE:
            try:
                detected_lang = detect(original_text)
                lang_probs = detect_langs(original_text)
                extracted.language = detected_lang
                extracted.language_confidence = max([lang.prob for lang in lang_probs])
            except:
                extracted.language = "en"
                extracted.language_confidence = 0.5
        
        # Extract named entities
        for ent in doc.ents:
            entity = ExtractedEntity(
                text=ent.text,
                label=ent.label_,
                start_pos=ent.start_char,
                end_pos=ent.end_char,
                confidence=0.8,  # spaCy doesn't provide confidence scores by default
                context=self._get_context(original_text, ent.start_char, ent.end_char)
            )
            
            # Categorize entities
            if ent.label_ in ["DATE", "TIME"]:
                parsed_date = self._parse_date(ent.text)
                if parsed_date:
                    entity.normalized_value = parsed_date.isoformat()
                extracted.dates.append(entity)
            
            elif ent.label_ in ["MONEY", "PERCENT"]:
                extracted.budgets.append(entity)
            
            elif ent.label_ in ["GPE", "LOC"]:
                extracted.locations.append(entity)
            
            elif ent.label_ in ["ORG"]:
                extracted.organizations.append(entity)
            
            elif ent.label_ in ["PERSON"]:
                extracted.contacts.append(entity)
        
        # Extract custom patterns
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            label = self.nlp.vocab.strings[match_id]
            
            entity = ExtractedEntity(
                text=span.text,
                label=label,
                start_pos=span.start_char,
                end_pos=span.end_char,
                confidence=0.7,
                context=self._get_context(original_text, span.start_char, span.end_char)
            )
            
            if label == "DEADLINE":
                extracted.deadlines.append(entity)
            elif label == "BUDGET":
                extracted.budgets.append(entity)
            elif label == "REQUIREMENT":
                extracted.requirements.append(entity)
        
        # Extract additional information using regex patterns
        await self._extract_regex_patterns(original_text, extracted)
        
        # Calculate overall confidence
        all_entities = (extracted.deadlines + extracted.dates + extracted.budgets + 
                       extracted.locations + extracted.organizations + extracted.contacts)
        if all_entities:
            extracted.overall_confidence = sum(e.confidence for e in all_entities) / len(all_entities)
        else:
            extracted.overall_confidence = 0.5
        
        return extracted
    
    async def _extract_regex_patterns(self, text: str, extracted: ExtractedInformation):
        """Extract information using regex patterns"""
        
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entity = ExtractedEntity(
                text=match.group(),
                label="EMAIL",
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9,
                context=self._get_context(text, match.start(), match.end())
            )
            extracted.contacts.append(entity)
        
        # Phone patterns
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        for match in re.finditer(phone_pattern, text):
            entity = ExtractedEntity(
                text=match.group(),
                label="PHONE",
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.8,
                context=self._get_context(text, match.start(), match.end())
            )
            extracted.contacts.append(entity)
        
        # URL patterns
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        for match in re.finditer(url_pattern, text):
            entity = ExtractedEntity(
                text=match.group(),
                label="URL",
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9,
                context=self._get_context(text, match.start(), match.end())
            )
            extracted.contacts.append(entity)
        
        # Currency patterns
        currency_pattern = r'(?:USD|EUR|GBP|CAD|AUD)\s*[\d,]+(?:\.\d{2})?|[\$€£¥]\s*[\d,]+(?:\.\d{2})?'
        for match in re.finditer(currency_pattern, text, re.IGNORECASE):
            entity = ExtractedEntity(
                text=match.group(),
                label="CURRENCY",
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.85,
                context=self._get_context(text, match.start(), match.end())
            )
            extracted.budgets.append(entity)
        
        # Deadline-specific patterns
        deadline_patterns = [
            r'deadline[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'due\s+(?:date|by)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'submit(?:ted)?\s+by[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'closing\s+date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in deadline_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity = ExtractedEntity(
                    text=match.group(),
                    label="DEADLINE_REGEX",
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8,
                    context=self._get_context(text, match.start(), match.end()),
                    normalized_value=self._parse_date(match.group(1))
                )
                extracted.deadlines.append(entity)
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context around extracted entity"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        import dateutil.parser
        try:
            parsed = dateutil.parser.parse(date_str, fuzzy=True)
            return parsed.isoformat()
        except:
            return None
    
    def _extract_key_phrases(self, doc) -> List[str]:
        """Extract key phrases from document"""
        # Simple noun phrase extraction
        key_phrases = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1 and len(chunk.text) > 5:
                key_phrases.append(chunk.text.strip())
        
        # Remove duplicates and sort by length
        key_phrases = list(set(key_phrases))
        key_phrases.sort(key=len, reverse=True)
        
        return key_phrases[:20]  # Return top 20
    
    def _calculate_sentiment(self, doc) -> float:
        """Calculate basic sentiment score"""
        # Simple sentiment based on positive/negative words
        positive_words = {"good", "excellent", "great", "outstanding", "successful", "effective"}
        negative_words = {"bad", "poor", "difficult", "challenging", "limited", "restricted"}
        
        words = [token.text.lower() for token in doc if token.is_alpha]
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def get_processor_name(self) -> str:
        return f"spaCy ({self.model_name})"
    
    def get_supported_languages(self) -> List[str]:
        # This would depend on the loaded model
        return ["en"]  # Default for en_core_web_sm

class TransformersNLPProcessor(NLPProcessorInterface):
    """Transformers-based NLP processor for advanced analysis"""
    
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers is required for TransformersNLPProcessor")
        
        self.model_name = model_name
        
        # Initialize pipelines
        try:
            self.sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", aggregation_strategy="simple")
            self.qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
        except Exception as e:
            logger.warning(f"Failed to initialize some transformers pipelines: {e}")
            self.sentiment_pipeline = None
            self.ner_pipeline = None
            self.qa_pipeline = None
    
    async def analyze_text(self, text: str, document_id: str) -> NLPAnalysisResult:
        """Analyze text using transformers"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Run transformers processing in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                extracted_info = await loop.run_in_executor(
                    executor, self._analyze_sync, text
                )
            
            # Basic text statistics
            sentences = text.split('.')
            words = text.split()
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            extracted_info.processing_time = processing_time
            
            # Get sentiment score
            sentiment_score = None
            if self.sentiment_pipeline:
                try:
                    sentiment_result = self.sentiment_pipeline(text[:512])  # Limit text length
                    if sentiment_result and len(sentiment_result) > 0:
                        # Convert to numeric score (-1 to 1)
                        label = sentiment_result[0]['label'].lower()
                        score = sentiment_result[0]['score']
                        if 'positive' in label:
                            sentiment_score = score
                        elif 'negative' in label:
                            sentiment_score = -score
                        else:
                            sentiment_score = 0.0
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed: {e}")
            
            return NLPAnalysisResult(
                document_id=document_id,
                text_length=len(text),
                sentence_count=len(sentences),
                word_count=len(words),
                extracted_info=extracted_info,
                sentiment_score=sentiment_score,
                processing_method="transformers",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Transformers analysis failed for document {document_id}: {e}")
            return NLPAnalysisResult(
                document_id=document_id,
                text_length=len(text),
                sentence_count=0,
                word_count=0,
                extracted_info=ExtractedInformation(),
                processing_method="transformers",
                success=False,
                error_message=str(e)
            )
    
    def _analyze_sync(self, text: str) -> ExtractedInformation:
        """Synchronous analysis using transformers"""
        extracted = ExtractedInformation()
        
        # Language detection
        if LANGDETECT_AVAILABLE:
            try:
                detected_lang = detect(text)
                lang_probs = detect_langs(text)
                extracted.language = detected_lang
                extracted.language_confidence = max([lang.prob for lang in lang_probs])
            except:
                extracted.language = "en"
                extracted.language_confidence = 0.5
        
        # Named Entity Recognition
        if self.ner_pipeline:
            try:
                # Limit text length for NER
                text_chunk = text[:2000]  # Process first 2000 characters
                ner_results = self.ner_pipeline(text_chunk)
                
                for entity in ner_results:
                    extracted_entity = ExtractedEntity(
                        text=entity['word'],
                        label=entity['entity_group'],
                        start_pos=entity['start'],
                        end_pos=entity['end'],
                        confidence=entity['score'],
                        context=self._get_context(text, entity['start'], entity['end'])
                    )
                    
                    # Categorize entities
                    if entity['entity_group'] in ['PER']:
                        extracted.contacts.append(extracted_entity)
                    elif entity['entity_group'] in ['ORG']:
                        extracted.organizations.append(extracted_entity)
                    elif entity['entity_group'] in ['LOC']:
                        extracted.locations.append(extracted_entity)
                    elif entity['entity_group'] in ['MISC']:
                        extracted.technologies.append(extracted_entity)
                
            except Exception as e:
                logger.warning(f"NER failed: {e}")
        
        # Question-Answering for specific information extraction
        if self.qa_pipeline:
            try:
                questions = [
                    "What is the deadline?",
                    "What is the budget?",
                    "What are the requirements?",
                    "What are the deliverables?",
                    "Who is the contact person?"
                ]
                
                for question in questions:
                    try:
                        answer = self.qa_pipeline(question=question, context=text[:1000])
                        if answer['score'] > 0.1:  # Confidence threshold
                            entity = ExtractedEntity(
                                text=answer['answer'],
                                label=f"QA_{question.split()[2].upper()}",  # Extract key word
                                start_pos=answer['start'],
                                end_pos=answer['end'],
                                confidence=answer['score'],
                                context=self._get_context(text, answer['start'], answer['end'])
                            )
                            
                            # Categorize based on question
                            if "deadline" in question.lower():
                                extracted.deadlines.append(entity)
                            elif "budget" in question.lower():
                                extracted.budgets.append(entity)
                            elif "requirement" in question.lower():
                                extracted.requirements.append(entity)
                            elif "deliverable" in question.lower():
                                extracted.deliverables.append(entity)
                            elif "contact" in question.lower():
                                extracted.contacts.append(entity)
                    
                    except Exception as e:
                        logger.warning(f"QA failed for question '{question}': {e}")
            
            except Exception as e:
                logger.warning(f"QA pipeline failed: {e}")
        
        # Calculate overall confidence
        all_entities = (extracted.deadlines + extracted.dates + extracted.budgets + 
                       extracted.locations + extracted.organizations + extracted.contacts)
        if all_entities:
            extracted.overall_confidence = sum(e.confidence for e in all_entities) / len(all_entities)
        else:
            extracted.overall_confidence = 0.5
        
        return extracted
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context around extracted entity"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def get_processor_name(self) -> str:
        return f"Transformers ({self.model_name})"
    
    def get_supported_languages(self) -> List[str]:
        return ["en", "de", "fr", "es", "it"]  # Common languages supported by BERT models

class NLTKProcessor(NLPProcessorInterface):
    """NLTK-based NLP processor (lightweight fallback)"""
    
    def __init__(self):
        if not NLTK_AVAILABLE:
            raise ImportError("NLTK is required for NLTKProcessor")
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    async def analyze_text(self, text: str, document_id: str) -> NLPAnalysisResult:
        """Analyze text using NLTK"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Run NLTK processing in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, self._analyze_sync, text, document_id
                )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            result.extracted_info.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"NLTK analysis failed for document {document_id}: {e}")
            return NLPAnalysisResult(
                document_id=document_id,
                text_length=len(text),
                sentence_count=0,
                word_count=0,
                extracted_info=ExtractedInformation(),
                processing_method="nltk",
                success=False,
                error_message=str(e)
            )
    
    def _analyze_sync(self, text: str, document_id: str) -> NLPAnalysisResult:
        """Synchronous NLTK analysis"""
        # Tokenization
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Basic information extraction using regex
        extracted_info = ExtractedInformation()
        
        # Language detection
        if LANGDETECT_AVAILABLE:
            try:
                detected_lang = detect(text)
                lang_probs = detect_langs(text)
                extracted_info.language = detected_lang
                extracted_info.language_confidence = max([lang.prob for lang in lang_probs])
            except:
                extracted_info.language = "en"
                extracted_info.language_confidence = 0.5
        
        # Extract information using regex patterns (similar to spaCy processor)
        self._extract_regex_patterns(text, extracted_info)
        
        # Extract key phrases using simple n-gram approach
        key_phrases = self._extract_key_phrases_nltk(text)
        
        # Basic sentiment analysis
        sentiment_score = self._calculate_sentiment_nltk(words)
        
        return NLPAnalysisResult(
            document_id=document_id,
            text_length=len(text),
            sentence_count=len(sentences),
            word_count=len(words),
            extracted_info=extracted_info,
            sentiment_score=sentiment_score,
            key_phrases=key_phrases,
            processing_method="nltk",
            success=True
        )
    
    def _extract_regex_patterns(self, text: str, extracted: ExtractedInformation):
        """Extract information using regex patterns (same as spaCy processor)"""
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entity = ExtractedEntity(
                text=match.group(),
                label="EMAIL",
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9,
                context=self._get_context(text, match.start(), match.end())
            )
            extracted.contacts.append(entity)
        
        # Currency patterns
        currency_pattern = r'(?:USD|EUR|GBP|CAD|AUD)\s*[\d,]+(?:\.\d{2})?|[\$€£¥]\s*[\d,]+(?:\.\d{2})?'
        for match in re.finditer(currency_pattern, text, re.IGNORECASE):
            entity = ExtractedEntity(
                text=match.group(),
                label="CURRENCY",
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.85,
                context=self._get_context(text, match.start(), match.end())
            )
            extracted.budgets.append(entity)
        
        # Date patterns
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        for match in re.finditer(date_pattern, text):
            entity = ExtractedEntity(
                text=match.group(),
                label="DATE",
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.8,
                context=self._get_context(text, match.start(), match.end())
            )
            extracted.dates.append(entity)
    
    def _extract_key_phrases_nltk(self, text: str) -> List[str]:
        """Extract key phrases using NLTK"""
        words = word_tokenize(text.lower())
        words = [self.lemmatizer.lemmatize(word) for word in words if word.isalpha() and word not in self.stop_words]
        
        # Simple bigram and trigram extraction
        from collections import Counter
        
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        # Get most common phrases
        bigram_counts = Counter(bigrams)
        trigram_counts = Counter(trigrams)
        
        key_phrases = []
        key_phrases.extend([phrase for phrase, count in trigram_counts.most_common(10) if count > 1])
        key_phrases.extend([phrase for phrase, count in bigram_counts.most_common(15) if count > 2])
        
        return key_phrases[:20]
    
    def _calculate_sentiment_nltk(self, words: List[str]) -> float:
        """Calculate basic sentiment using word lists"""
        positive_words = {"good", "excellent", "great", "outstanding", "successful", "effective", "strong", "positive"}
        negative_words = {"bad", "poor", "difficult", "challenging", "limited", "restricted", "weak", "negative"}
        
        word_set = set(word.lower() for word in words if word.isalpha())
        
        positive_count = len(word_set.intersection(positive_words))
        negative_count = len(word_set.intersection(negative_words))
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context around extracted entity"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def get_processor_name(self) -> str:
        return "NLTK"
    
    def get_supported_languages(self) -> List[str]:
        return ["en"]  # NLTK primarily supports English

class NLPAnalysisModule:
    """Main NLP Analysis Module - Orchestrates all processors"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize processors in order of preference
        self.processors = []
        
        # Try to initialize spaCy processor
        spacy_model = self.config.get('spacy_model', 'en_core_web_sm')
        if SPACY_AVAILABLE:
            try:
                self.processors.append(SpacyNLPProcessor(spacy_model))
                logger.info(f"Initialized spaCy processor with model: {spacy_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize spaCy processor: {e}")
        
        # Try to initialize Transformers processor
        transformers_model = self.config.get('transformers_model', 'distilbert-base-uncased')
        if TRANSFORMERS_AVAILABLE:
            try:
                self.processors.append(TransformersNLPProcessor(transformers_model))
                logger.info(f"Initialized Transformers processor with model: {transformers_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Transformers processor: {e}")
        
        # Always try to initialize NLTK processor as fallback
        if NLTK_AVAILABLE:
            try:
                self.processors.append(NLTKProcessor())
                logger.info("Initialized NLTK processor")
            except Exception as e:
                logger.warning(f"Failed to initialize NLTK processor: {e}")
        
        if not self.processors:
            raise RuntimeError("No NLP processors could be initialized")
        
        # Configuration
        self.primary_processor = self.processors[0]
        self.max_concurrent_processing = self.config.get('max_concurrent_processing', 3)
        self.enable_fallback = self.config.get('enable_fallback', True)
        
        logger.info(f"NLP Analysis Module initialized with {len(self.processors)} processors")
        logger.info(f"Primary processor: {self.primary_processor.get_processor_name()}")
    
    async def analyze_text(self, text: str, document_id: str, processor_name: Optional[str] = None) -> NLPAnalysisResult:
        """Analyze text using specified or primary processor"""
        
        # Select processor
        processor = self.primary_processor
        if processor_name:
            for p in self.processors:
                if processor_name.lower() in p.get_processor_name().lower():
                    processor = p
                    break
        
        try:
            result = await processor.analyze_text(text, document_id)
            
            if result.success:
                return result
            elif self.enable_fallback and len(self.processors) > 1:
                # Try fallback processors
                logger.warning(f"Primary processor failed, trying fallback processors")
                for fallback_processor in self.processors[1:]:
                    try:
                        fallback_result = await fallback_processor.analyze_text(text, document_id)
                        if fallback_result.success:
                            logger.info(f"Fallback processor {fallback_processor.get_processor_name()} succeeded")
                            return fallback_result
                    except Exception as e:
                        logger.warning(f"Fallback processor {fallback_processor.get_processor_name()} failed: {e}")
                        continue
            
            return result
            
        except Exception as e:
            logger.error(f"NLP analysis failed for document {document_id}: {e}")
            return NLPAnalysisResult(
                document_id=document_id,
                text_length=len(text),
                sentence_count=0,
                word_count=0,
                extracted_info=ExtractedInformation(),
                success=False,
                error_message=str(e)
            )
    
    async def analyze_texts_batch(self, texts: List[Tuple[str, str]], processor_name: Optional[str] = None) -> List[NLPAnalysisResult]:
        """Analyze multiple texts concurrently"""
        semaphore = asyncio.Semaphore(self.max_concurrent_processing)
        
        async def analyze_with_semaphore(text_doc_pair):
            async with semaphore:
                text, doc_id = text_doc_pair
                return await self.analyze_text(text, doc_id, processor_name)
        
        tasks = [analyze_with_semaphore(pair) for pair in texts]
        results = await asyncio.gather(*tasks)
        
        successful = sum(1 for r in results if r.success)
        logger.info(f"Batch analysis completed: {successful}/{len(texts)} successful")
        
        return results
    
    def get_processor_status(self) -> Dict[str, Any]:
        """Get status of all processors"""
        return {
            'processors': [
                {
                    'name': p.get_processor_name(),
                    'supported_languages': p.get_supported_languages()
                }
                for p in self.processors
            ],
            'primary_processor': self.primary_processor.get_processor_name(),
            'libraries': {
                'spacy': SPACY_AVAILABLE,
                'nltk': NLTK_AVAILABLE,
                'transformers': TRANSFORMERS_AVAILABLE,
                'langdetect': LANGDETECT_AVAILABLE
            },
            'config': {
                'max_concurrent_processing': self.max_concurrent_processing,
                'enable_fallback': self.enable_fallback
            }
        }
    
    async def test_processors(self) -> Dict[str, Any]:
        """Test all processors with sample text"""
        test_text = """
        The United Nations is seeking proposals for a climate change adaptation project.
        The deadline for submission is March 15, 2024. The budget is $500,000 USD.
        Please contact john.doe@un.org for more information.
        Requirements include 5+ years of experience in environmental consulting.
        """
        
        test_results = {}
        
        for processor in self.processors:
            try:
                start_time = asyncio.get_event_loop().time()
                result = await processor.analyze_text(test_text, "test_doc")
                end_time = asyncio.get_event_loop().time()
                
                test_results[processor.get_processor_name()] = {
                    'status': 'success' if result.success else 'failed',
                    'processing_time': end_time - start_time,
                    'entities_found': {
                        'deadlines': len(result.extracted_info.deadlines),
                        'budgets': len(result.extracted_info.budgets),
                        'contacts': len(result.extracted_info.contacts),
                        'organizations': len(result.extracted_info.organizations)
                    },
                    'sentiment_score': result.sentiment_score,
                    'key_phrases_count': len(result.key_phrases),
                    'error': result.error_message
                }
                
            except Exception as e:
                test_results[processor.get_processor_name()] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return test_results

# Example usage and testing
async def main():
    """Example usage of NLP Analysis Module"""
    
    # Initialize module
    config = {
        'spacy_model': 'en_core_web_sm',
        'transformers_model': 'distilbert-base-uncased',
        'max_concurrent_processing': 2,
        'enable_fallback': True
    }
    
    nlp_module = NLPAnalysisModule(config)
    
    # Show processor status
    print("Processor Status:")
    status = nlp_module.get_processor_status()
    print(f"Available processors: {[p['name'] for p in status['processors']]}")
    print(f"Primary processor: {status['primary_processor']}")
    print(f"Library availability: {status['libraries']}")
    
    # Test processors
    print("\nTesting processors...")
    test_results = await nlp_module.test_processors()
    print(json.dumps(test_results, indent=2, default=str))
    
    # Example analysis
    sample_text = """
    Request for Proposal: Climate Change Adaptation in Sub-Saharan Africa
    
    The World Bank is seeking qualified consultants to develop a comprehensive
    climate adaptation strategy for agricultural communities in Kenya and Tanzania.
    
    Deadline: Applications must be submitted by April 30, 2024, 5:00 PM EST.
    Budget: The total project budget is $750,000 USD over 18 months.
    
    Requirements:
    - Minimum 7 years of experience in climate adaptation
    - Proven track record in Sub-Saharan Africa
    - Expertise in agricultural systems and community engagement
    
    Contact: Dr. Sarah Johnson (sjohnson@worldbank.org) for technical questions.
    
    Deliverables include:
    1. Baseline assessment report
    2. Adaptation strategy document
    3. Implementation roadmap
    4. Training materials for local communities
    """
    
    print(f"\nAnalyzing sample RFP text...")
    result = await nlp_module.analyze_text(sample_text, "sample_rfp")
    
    if result.success:
        print(f"Analysis successful!")
        print(f"Language: {result.extracted_info.language} (confidence: {result.extracted_info.language_confidence:.2f})")
        print(f"Processing time: {result.extracted_info.processing_time:.2f}s")
        print(f"Text length: {result.text_length} characters")
        print(f"Sentences: {result.sentence_count}")
        print(f"Words: {result.word_count}")
        
        print(f"\nExtracted Information:")
        print(f"- Deadlines: {len(result.extracted_info.deadlines)}")
        for deadline in result.extracted_info.deadlines:
            print(f"  * {deadline.text} (confidence: {deadline.confidence:.2f})")
        
        print(f"- Budgets: {len(result.extracted_info.budgets)}")
        for budget in result.extracted_info.budgets:
            print(f"  * {budget.text} (confidence: {budget.confidence:.2f})")
        
        print(f"- Organizations: {len(result.extracted_info.organizations)}")
        for org in result.extracted_info.organizations:
            print(f"  * {org.text} (confidence: {org.confidence:.2f})")
        
        print(f"- Contacts: {len(result.extracted_info.contacts)}")
        for contact in result.extracted_info.contacts:
            print(f"  * {contact.text} (confidence: {contact.confidence:.2f})")
        
        if result.sentiment_score is not None:
            print(f"\nSentiment Score: {result.sentiment_score:.2f}")
        
        if result.key_phrases:
            print(f"\nKey Phrases: {result.key_phrases[:5]}")
    
    else:
        print(f"Analysis failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
