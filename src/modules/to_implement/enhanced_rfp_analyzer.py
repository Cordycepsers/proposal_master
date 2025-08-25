"""
Enhanced RFP Analyzer with NLP and Machine Learning
Implements Key Information Extraction and Red/Green Flag Classification
"""

import spacy
import pandas as pd
import numpy as np
import re
import yaml
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from langdetect import detect
import nltk
from datetime import datetime, timedelta
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExtractedInfo:
    deadlines: List[str]
    budgets: List[str]
    geographic_scope: List[str]
    deliverables: List[str]
    contact_info: List[str]
    language: str
    confidence: float

@dataclass
class ClassificationResult:
    green_flags: List[str]
    red_flags: List[str]
    qualification_score: float
    recommendation: str
    confidence: float

@dataclass
class RFPAnalysisResult:
    rfp_id: str
    title: str
    organization: str
    extracted_info: ExtractedInfo
    classification: ClassificationResult
    processing_time: float

class EnhancedRFPAnalyzer:
    """Enhanced RFP Analyzer with NLP and ML capabilities"""
    
    def __init__(self, config_path: str = "rfp_analyzer_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize NLP models
        self.nlp = None
        self.sentiment_analyzer = None
        self.classifier = None
        self.vectorizer = None
        
        # Initialize patterns
        self.extraction_patterns = self._compile_patterns()
        
        # Load models
        self._initialize_models()
        
        logger.info("Enhanced RFP Analyzer initialized successfully")
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if file loading fails"""
        return {
            'analysis': {'qualification_thresholds': {'high_priority': 80, 'manual_review': 40, 'auto_reject': 0}},
            'green_flags': {'expertise': [], 'experience': [], 'awards_topics': [], 'partnerships': [], 'geographic_advantages': []},
            'red_flags': {'requirements': [], 'geographic_challenges': {'high_risk': [], 'medium_risk': []}, 'timeline': [], 'language': {'unsupported': []}},
            'scoring': {'green_flag_weights': {}, 'red_flag_penalties': {}},
            'extraction_patterns': {'deadlines': [], 'budgets': [], 'geographic_scope': [], 'deliverables': []}
        }
    
    def _compile_patterns(self) -> Dict:
        """Compile regex patterns for information extraction"""
        patterns = {}
        for category, pattern_list in self.config.get('extraction_patterns', {}).items():
            patterns[category] = [re.compile(pattern, re.IGNORECASE) for pattern in pattern_list]
        return patterns
    
    def _initialize_models(self):
        """Initialize NLP and ML models"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            logger.info("Sentiment analyzer initialized")
            
            # Initialize or load classification model
            self._initialize_classifier()
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            # Fallback to basic functionality
            self.nlp = None
            self.sentiment_analyzer = None
    
    def _initialize_classifier(self):
        """Initialize or load the classification model"""
        model_path = "database/rfp_classifier.pkl"
        vectorizer_path = "database/rfp_vectorizer.pkl"
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            # Load existing model
            try:
                with open(model_path, 'rb') as f:
                    self.classifier = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                logger.info("Existing classifier loaded")
                return
            except Exception as e:
                logger.warning(f"Failed to load existing model: {e}")
        
        # Train new model with sample data
        self._train_classifier()
    
    def _train_classifier(self):
        """Train a new classification model with sample data"""
        try:
            # Sample training data (in production, this would be much larger)
            training_data = [
                ("multimedia video production environmental campaign", "high_priority"),
                ("local registration required physical submission only", "auto_reject"),
                ("data visualization documentary series UN agencies", "high_priority"),
                ("India Pakistan local company required", "auto_reject"),
                ("climate change awareness campaign video production", "high_priority"),
                ("proposal due tomorrow physical forms only", "auto_reject"),
                ("NGO partnership multimedia campaign Africa", "high_priority"),
                ("Turkey local pricing requirements", "manual_review"),
                ("BirdLife environmental documentary series", "high_priority"),
                ("Nepal Asia timezone challenges", "manual_review")
            ]
            
            texts, labels = zip(*training_data)
            
            # Create TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            X = self.vectorizer.fit_transform(texts)
            
            # Train classifier
            self.classifier = LogisticRegression(random_state=42)
            self.classifier.fit(X, labels)
            
            # Save model
            with open("database/rfp_classifier.pkl", 'wb') as f:
                pickle.dump(self.classifier, f)
            with open("database/rfp_vectorizer.pkl", 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            logger.info("New classifier trained and saved")
            
        except Exception as e:
            logger.error(f"Classifier training failed: {e}")
            self.classifier = None
            self.vectorizer = None
    
    def analyze_rfp(self, text: str, rfp_id: str = None, title: str = None, organization: str = None) -> RFPAnalysisResult:
        """Analyze RFP document and return comprehensive results"""
        start_time = datetime.now()
        
        if not rfp_id:
            rfp_id = f"rfp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting analysis for RFP: {rfp_id}")
        
        try:
            # Extract key information
            extracted_info = self._extract_key_information(text)
            
            # Perform classification
            classification = self._classify_rfp(text, extracted_info)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = RFPAnalysisResult(
                rfp_id=rfp_id,
                title=title or "Unknown",
                organization=organization or "Unknown",
                extracted_info=extracted_info,
                classification=classification,
                processing_time=processing_time
            )
            
            logger.info(f"Analysis completed for {rfp_id}: {classification.recommendation} (score: {classification.qualification_score})")
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed for {rfp_id}: {e}")
            # Return minimal result on error
            return RFPAnalysisResult(
                rfp_id=rfp_id,
                title=title or "Unknown",
                organization=organization or "Unknown",
                extracted_info=ExtractedInfo([], [], [], [], [], "unknown", 0.0),
                classification=ClassificationResult([], [], 0.0, "error", 0.0),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _extract_key_information(self, text: str) -> ExtractedInfo:
        """Extract key information using NLP and regex patterns"""
        
        # Detect language
        try:
            language = detect(text)
            confidence = 0.8  # Simplified confidence score
        except:
            language = "unknown"
            confidence = 0.0
        
        # Extract using regex patterns
        deadlines = self._extract_with_patterns(text, 'deadlines')
        budgets = self._extract_with_patterns(text, 'budgets')
        geographic_scope = self._extract_with_patterns(text, 'geographic_scope')
        deliverables = self._extract_with_patterns(text, 'deliverables')
        
        # Extract contact information using spaCy NER
        contact_info = self._extract_contact_info(text)
        
        # Extract additional geographic information using spaCy
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC"]:  # Geopolitical entities and locations
                    geographic_scope.append(ent.text)
        
        return ExtractedInfo(
            deadlines=list(set(deadlines)),
            budgets=list(set(budgets)),
            geographic_scope=list(set(geographic_scope)),
            deliverables=list(set(deliverables)),
            contact_info=list(set(contact_info)),
            language=language,
            confidence=confidence
        )
    
    def _extract_with_patterns(self, text: str, category: str) -> List[str]:
        """Extract information using compiled regex patterns"""
        results = []
        patterns = self.extraction_patterns.get(category, [])
        
        for pattern in patterns:
            matches = pattern.findall(text)
            results.extend(matches)
        
        return [match.strip() for match in results if match.strip()]
    
    def _extract_contact_info(self, text: str) -> List[str]:
        """Extract contact information using NER"""
        contact_info = []
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PERSON"]:
                    contact_info.append(ent.text)
        
        # Extract emails and phone numbers with regex
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
        
        contact_info.extend(email_pattern.findall(text))
        contact_info.extend(phone_pattern.findall(text))
        
        return contact_info
    
    def _classify_rfp(self, text: str, extracted_info: ExtractedInfo) -> ClassificationResult:
        """Classify RFP using rule-based and ML approaches"""
        
        # Rule-based classification
        green_flags, green_score = self._identify_green_flags(text, extracted_info)
        red_flags, red_penalty = self._identify_red_flags(text, extracted_info)
        
        # Calculate qualification score
        base_score = 50  # Starting score
        qualification_score = max(0, min(100, base_score + green_score + red_penalty))
        
        # Determine recommendation
        thresholds = self.config['analysis']['qualification_thresholds']
        if qualification_score >= thresholds['high_priority']:
            recommendation = "high_priority"
        elif qualification_score >= thresholds['manual_review']:
            recommendation = "manual_review"
        else:
            recommendation = "auto_reject"
        
        # ML-based confidence (if available)
        ml_confidence = self._get_ml_confidence(text)
        
        return ClassificationResult(
            green_flags=green_flags,
            red_flags=red_flags,
            qualification_score=qualification_score,
            recommendation=recommendation,
            confidence=ml_confidence
        )
    
    def _identify_green_flags(self, text: str, extracted_info: ExtractedInfo) -> Tuple[List[str], float]:
        """Identify green flags and calculate positive score"""
        green_flags = []
        total_score = 0
        text_lower = text.lower()
        
        weights = self.config['scoring']['green_flag_weights']
        
        # Check expertise keywords
        for keyword in self.config['green_flags']['expertise']:
            if keyword.lower() in text_lower:
                green_flags.append(f"Expertise match: {keyword}")
                total_score += weights.get('expertise', 10)
        
        # Check experience keywords
        for keyword in self.config['green_flags']['experience']:
            if keyword.lower() in text_lower:
                green_flags.append(f"Experience match: {keyword}")
                total_score += weights.get('experience', 15)
        
        # Check award topics
        for topic in self.config['green_flags']['awards_topics']:
            if topic.lower() in text_lower:
                green_flags.append(f"Award-winning topic: {topic}")
                total_score += weights.get('awards_topics', 20)
        
        # Check partnerships
        for partner in self.config['green_flags']['partnerships']:
            if partner.lower() in text_lower:
                green_flags.append(f"Strategic partnership: {partner}")
                total_score += weights.get('partnerships', 25)
        
        # Check geographic advantages
        for location in self.config['green_flags']['geographic_advantages']:
            if location.lower() in text_lower or any(location.lower() in geo.lower() for geo in extracted_info.geographic_scope):
                green_flags.append(f"Geographic advantage: {location}")
                total_score += weights.get('geographic_advantages', 15)
        
        return green_flags, total_score
    
    def _identify_red_flags(self, text: str, extracted_info: ExtractedInfo) -> Tuple[List[str], float]:
        """Identify red flags and calculate penalty score"""
        red_flags = []
        total_penalty = 0
        text_lower = text.lower()
        
        penalties = self.config['scoring']['red_flag_penalties']
        
        # Check requirement red flags
        for requirement in self.config['red_flags']['requirements']:
            if requirement.lower() in text_lower:
                red_flags.append(f"Requirement issue: {requirement}")
                total_penalty += penalties.get('requirements', -50)
        
        # Check geographic challenges
        for location in self.config['red_flags']['geographic_challenges']['high_risk']:
            if location.lower() in text_lower or any(location.lower() in geo.lower() for geo in extracted_info.geographic_scope):
                red_flags.append(f"High-risk geography: {location}")
                total_penalty += penalties.get('geographic_high_risk', -30)
        
        for location in self.config['red_flags']['geographic_challenges']['medium_risk']:
            if location.lower() in text_lower or any(location.lower() in geo.lower() for geo in extracted_info.geographic_scope):
                red_flags.append(f"Medium-risk geography: {location}")
                total_penalty += penalties.get('geographic_medium_risk', -10)
        
        # Check timeline issues
        for timeline_issue in self.config['red_flags']['timeline']:
            if timeline_issue.lower() in text_lower:
                red_flags.append(f"Timeline issue: {timeline_issue}")
                total_penalty += penalties.get('timeline', -40)
        
        # Check language support
        if extracted_info.language not in ['en', 'es', 'fr']:
            red_flags.append(f"Unsupported language: {extracted_info.language}")
            total_penalty += penalties.get('language', -100)
        
        return red_flags, total_penalty
    
    def _get_ml_confidence(self, text: str) -> float:
        """Get ML model confidence score"""
        if not self.classifier or not self.vectorizer:
            return 0.5  # Default confidence
        
        try:
            # Vectorize text
            X = self.vectorizer.transform([text])
            
            # Get prediction probabilities
            probabilities = self.classifier.predict_proba(X)[0]
            
            # Return max probability as confidence
            return float(max(probabilities))
            
        except Exception as e:
            logger.error(f"ML confidence calculation failed: {e}")
            return 0.5
    
    def export_results(self, results: List[RFPAnalysisResult], output_path: str = "rfp_analysis_results.json"):
        """Export analysis results to JSON file"""
        try:
            import json
            
            # Convert results to serializable format
            serializable_results = []
            for result in results:
                result_dict = {
                    'rfp_id': result.rfp_id,
                    'title': result.title,
                    'organization': result.organization,
                    'extracted_info': asdict(result.extracted_info),
                    'classification': asdict(result.classification),
                    'processing_time': result.processing_time
                }
                serializable_results.append(result_dict)
            
            with open(output_path, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            
            logger.info(f"Results exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Export failed: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = EnhancedRFPAnalyzer()
    
    # Sample RFP texts for testing
    sample_rfps = [
        {
            'id': 'rfp_001',
            'title': 'Environmental Documentary Series Production',
            'organization': 'UN Environment Programme',
            'text': '''
            The United Nations Environment Programme seeks a creative agency to produce a 
            multimedia documentary series on climate change in Africa. The project requires 
            video production, animation, and data visualization capabilities.
            
            Requirements:
            - Minimum 7 years experience in environmental campaigns
            - Expertise in multimedia production
            - Experience working with UN agencies
            - Strong presence in Africa (Kenya, Ghana preferred)
            - Data visualization capabilities
            
            Deliverables:
            - 6-part documentary series
            - Educational materials
            - Social media campaign
            
            Budget: $500,000
            Deadline: March 15, 2025
            Geographic scope: Africa (Kenya, Ghana, South Africa)
            '''
        },
        {
            'id': 'rfp_002',
            'title': 'Local Marketing Campaign - India',
            'organization': 'Local Government India',
            'text': '''
            Local government in Mumbai requires marketing campaign for local services.
            Must be local company with registration in India.
            Physical submission required at Mumbai office.
            Budget: 50,000 INR
            Proposal due tomorrow.
            Must speak Hindi and have local presence.
            '''
        },
        {
            'id': 'rfp_003',
            'title': 'Youth Climate Awareness Campaign',
            'organization': 'BirdLife International',
            'text': '''
            BirdLife International in partnership with UN agencies seeks creative agency 
            for youth climate awareness campaign. Project involves video production, 
            and data visualization of environmental impact.
            
            Requirements:
            - Experience with youth campaigns
            - Environmental focus
            - Video and multimedia capabilities
            - Data visualization expertise
            
            Budget: $750,000
            Deadline: April 30, 2025
            Locations: New York City, London
            '''
        }
    ]
    
    # Analyze sample RFPs
    results = []
    for rfp in sample_rfps:
        result = analyzer.analyze_rfp(
            text=rfp['text'],
            rfp_id=rfp['id'],
            title=rfp['title'],
            organization=rfp['organization']
        )
        results.append(result)
        
        # Print summary
        print("=" * 60)
        print(f"RFP ID: {result.rfp_id}")
        print(f"Title: {result.title}")
        print(f"Organization: {result.organization}")
        print(f"Status: {result.classification.recommendation}")
        print(f"Score: {result.classification.qualification_score}")
        print(f"Language: {result.extracted_info.language}")
        print(f"Confidence: {result.classification.confidence:.2f}")
        print(f"Green Flags ({len(result.classification.green_flags)}):")
        for flag in result.classification.green_flags:
            print(f"  + {flag}")
        print(f"Red Flags ({len(result.classification.red_flags)}):")
        for flag in result.classification.red_flags:
            print(f"  - {flag}")
        print("Key Information:")
        if result.extracted_info.deadlines:
            print(f"  deadlines: {result.extracted_info.deadlines}")
        if result.extracted_info.budgets:
            print(f"  budgets: {result.extracted_info.budgets}")
        if result.extracted_info.geographic_scope:
            print(f"  geographic_scope: {result.extracted_info.geographic_scope}")
        if result.extracted_info.deliverables:
            print(f"  deliverables: {result.extracted_info.deliverables}")
        if result.extracted_info.contact_info:
            print(f"  contact_info: {result.extracted_info.contact_info}")
    
    # Export results
    analyzer.export_results(results)
    logger.info("Analysis complete!")
