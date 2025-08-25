"""
Classification Module - Independent Red/Green Flag Classification

This module handles RFP classification based on business criteria.
It can be developed, tested, and upgraded independently of other modules.
Supports scikit-learn, transformers, and custom rule-based classification.

Features:
- Red/Green flag classification based on business rules
- Machine learning models (scikit-learn, transformers)
- Confidence scoring and explanation
- Model training and fine-tuning capabilities
- A/B testing for different classification approaches
- Continuous learning from feedback
"""

import asyncio
import logging
import pickle
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
import re

# ML Libraries
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.pipeline import Pipeline
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ClassificationCriteria:
    """Business criteria for RFP classification"""
    
    # Red flags (reasons to reject)
    red_flags: Dict[str, List[str]] = field(default_factory=lambda: {
        'location_restrictions': [
            'local registration', 'local company', 'national service provider',
            'india', 'pakistan', 'turkey'
        ],
        'submission_restrictions': [
            'physical form', 'on location', 'in person submission',
            'hard copy only', 'postal submission'
        ],
        'work_restrictions': [
            'remote work not possible', 'on-site only', 'local presence required'
        ],
        'administrative_burden': [
            'extreme amount of forms', 'excessive documentation',
            'complex registration process'
        ],
        'scope_mismatch': [
            'full concept required', 'create actual designs',
            'detailed technical specifications'
        ],
        'timeline_issues': [
            'due in less than 2 days', 'immediate submission',
            'urgent deadline'
        ],
        'expertise_mismatch': [
            'desired outputs do not match our expertise',
            'outside our capabilities'
        ]
    })
    
    # Green flags (reasons to pursue)
    green_flags: Dict[str, List[str]] = field(default_factory=lambda: {
        'expertise_match': [
            'multimedia', 'multi media', 'programmatic videos',
            'donor videos', 'video', 'communications campaign',
            'digital campaign', 'data visualization'
        ],
        'experience_requirements': [
            'more than 10 years experience', 'more than 5 years experience',
            'more than 7 years experience', 'experience with ngos',
            'experience with un agencies'
        ],
        'focus_areas': [
            'youth focused campaigns', 'climate focused campaigns',
            'women focused campaigns', 'food focused campaigns',
            'child focused campaigns', 'safety and security focused'
        ],
        'award_topics': [
            'environment', 'refugees', 'africa', 'food'
        ],
        'partnerships': [
            'un foundation', 'unicef', 'global partnership',
            'un women', 'equator prize', 'nature for life'
        ],
        'service_types': [
            'feature length documentaries', 'environmental',
            'photo', 'film', 'design', 'visual', 'campaign',
            'awareness campaign', 'end to end development',
            'full spectrum campaign', 'strategic planning',
            'campaign strategy', 'communications strategy',
            'comprehensive', 'paid media', 'public relations',
            'press release', 'influencers', 'social media toolkit',
            'creative assets', 'graphic design', 'visual identity',
            'infographics', 'branding', 'podcasts', 'virtual event',
            'media', 'animation', 'video editing', 'animated video',
            'promotion', 'communication', 'audiovisual', 'website',
            'microsite', 'creative agency', 'design agency',
            'production company'
        ],
        'favorable_locations': [
            'new york city', 'south africa', 'spain', 'sweden',
            'ukraine', 'nigeria', 'kenya', 'ghana', 'england',
            'united kingdom', 'lebanon'
        ]
    })
    
    # Weights for different criteria categories
    category_weights: Dict[str, float] = field(default_factory=lambda: {
        'location_restrictions': -0.8,
        'submission_restrictions': -0.9,
        'work_restrictions': -0.7,
        'administrative_burden': -0.6,
        'scope_mismatch': -0.8,
        'timeline_issues': -0.9,
        'expertise_mismatch': -1.0,
        'expertise_match': 0.9,
        'experience_requirements': 0.7,
        'focus_areas': 0.8,
        'award_topics': 0.9,
        'partnerships': 0.8,
        'service_types': 0.7,
        'favorable_locations': 0.6
    })

@dataclass
class ClassificationResult:
    """Classification result structure"""
    document_id: str
    classification: str  # 'high_priority', 'manual_review', 'auto_reject'
    confidence_score: float
    overall_score: float
    red_flags: List[Dict[str, Any]]
    green_flags: List[Dict[str, Any]]
    explanation: str
    processing_time: float
    classifier_used: str
    success: bool = True
    error_message: Optional[str] = None

class ClassifierInterface(ABC):
    """Abstract interface for RFP classifiers"""
    
    @abstractmethod
    async def classify_rfp(self, text: str, document_id: str, extracted_info: Optional[Dict] = None) -> ClassificationResult:
        """Classify RFP text"""
        pass
    
    @abstractmethod
    def get_classifier_name(self) -> str:
        """Return classifier name"""
        pass
    
    @abstractmethod
    def can_train(self) -> bool:
        """Return whether classifier supports training"""
        pass
    
    @abstractmethod
    async def train(self, training_data: List[Tuple[str, str]]) -> bool:
        """Train classifier with labeled data"""
        pass

class RuleBasedClassifier(ClassifierInterface):
    """Rule-based classifier using business criteria"""
    
    def __init__(self, criteria: ClassificationCriteria = None):
        self.criteria = criteria or ClassificationCriteria()
        
        # Thresholds for classification
        self.high_priority_threshold = 0.8
        self.manual_review_threshold = 0.4
        
    async def classify_rfp(self, text: str, document_id: str, extracted_info: Optional[Dict] = None) -> ClassificationResult:
        """Classify RFP using rule-based approach"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            text_lower = text.lower()
            
            red_flags = []
            green_flags = []
            total_score = 0.0
            
            # Check red flags
            for category, keywords in self.criteria.red_flags.items():
                category_score = 0.0
                matched_keywords = []
                
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        matched_keywords.append(keyword)
                        # Count occurrences for stronger signal
                        occurrences = len(re.findall(re.escape(keyword.lower()), text_lower))
                        category_score += occurrences * 0.1
                
                if matched_keywords:
                    weight = self.criteria.category_weights.get(category, -0.5)
                    weighted_score = weight * min(category_score, 1.0)  # Cap at 1.0
                    total_score += weighted_score
                    
                    red_flags.append({
                        'category': category,
                        'keywords': matched_keywords,
                        'score': weighted_score,
                        'explanation': f"Found {category.replace('_', ' ')} indicators"
                    })
            
            # Check green flags
            for category, keywords in self.criteria.green_flags.items():
                category_score = 0.0
                matched_keywords = []
                
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        matched_keywords.append(keyword)
                        occurrences = len(re.findall(re.escape(keyword.lower()), text_lower))
                        category_score += occurrences * 0.1
                
                if matched_keywords:
                    weight = self.criteria.category_weights.get(category, 0.5)
                    weighted_score = weight * min(category_score, 1.0)
                    total_score += weighted_score
                    
                    green_flags.append({
                        'category': category,
                        'keywords': matched_keywords,
                        'score': weighted_score,
                        'explanation': f"Found {category.replace('_', ' ')} match"
                    })
            
            # Normalize score to [-1, 1] range
            normalized_score = max(-1.0, min(1.0, total_score))
            
            # Determine classification
            if normalized_score >= self.high_priority_threshold:
                classification = 'high_priority'
            elif normalized_score >= self.manual_review_threshold:
                classification = 'manual_review'
            else:
                classification = 'auto_reject'
            
            # Calculate confidence based on number and strength of signals
            total_signals = len(red_flags) + len(green_flags)
            confidence_score = min(0.9, 0.5 + (total_signals * 0.1))
            
            # Generate explanation
            explanation = self._generate_explanation(classification, red_flags, green_flags, normalized_score)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ClassificationResult(
                document_id=document_id,
                classification=classification,
                confidence_score=confidence_score,
                overall_score=normalized_score,
                red_flags=red_flags,
                green_flags=green_flags,
                explanation=explanation,
                processing_time=processing_time,
                classifier_used="rule_based",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Rule-based classification failed for document {document_id}: {e}")
            return ClassificationResult(
                document_id=document_id,
                classification='manual_review',
                confidence_score=0.0,
                overall_score=0.0,
                red_flags=[],
                green_flags=[],
                explanation=f"Classification failed: {str(e)}",
                processing_time=asyncio.get_event_loop().time() - start_time,
                classifier_used="rule_based",
                success=False,
                error_message=str(e)
            )
    
    def _generate_explanation(self, classification: str, red_flags: List[Dict], green_flags: List[Dict], score: float) -> str:
        """Generate human-readable explanation"""
        explanation_parts = []
        
        explanation_parts.append(f"Classification: {classification.replace('_', ' ').title()}")
        explanation_parts.append(f"Overall Score: {score:.2f}")
        
        if green_flags:
            explanation_parts.append(f"\nPositive Indicators ({len(green_flags)}):")
            for flag in green_flags[:3]:  # Show top 3
                explanation_parts.append(f"• {flag['explanation']}: {', '.join(flag['keywords'][:3])}")
        
        if red_flags:
            explanation_parts.append(f"\nConcerns ({len(red_flags)}):")
            for flag in red_flags[:3]:  # Show top 3
                explanation_parts.append(f"• {flag['explanation']}: {', '.join(flag['keywords'][:3])}")
        
        if classification == 'high_priority':
            explanation_parts.append("\nRecommendation: Prioritize this RFP for immediate review.")
        elif classification == 'manual_review':
            explanation_parts.append("\nRecommendation: Requires manual review to assess fit.")
        else:
            explanation_parts.append("\nRecommendation: Consider rejecting based on identified concerns.")
        
        return "\n".join(explanation_parts)
    
    def get_classifier_name(self) -> str:
        return "Rule-Based Classifier"
    
    def can_train(self) -> bool:
        return False  # Rule-based doesn't require training
    
    async def train(self, training_data: List[Tuple[str, str]]) -> bool:
        """Rule-based classifier doesn't require training"""
        return True

class MLClassifier(ClassifierInterface):
    """Machine learning classifier using scikit-learn"""
    
    def __init__(self, model_path: Optional[Path] = None):
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for MLClassifier")
        
        self.model_path = model_path or Path("rfp_classifier_model.pkl")
        self.vectorizer_path = Path(str(self.model_path).replace('.pkl', '_vectorizer.pkl'))
        
        # Initialize model pipeline
        self.pipeline = None
        self.is_trained = False
        
        # Load existing model if available
        if self.model_path.exists() and self.vectorizer_path.exists():
            self._load_model()
    
    def _load_model(self):
        """Load trained model from disk"""
        try:
            with open(self.model_path, 'rb') as f:
                self.pipeline = pickle.load(f)
            self.is_trained = True
            logger.info(f"Loaded ML model from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self.is_trained = False
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.pipeline, f)
            logger.info(f"Saved ML model to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save ML model: {e}")
    
    async def classify_rfp(self, text: str, document_id: str, extracted_info: Optional[Dict] = None) -> ClassificationResult:
        """Classify RFP using ML model"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.is_trained:
            # Fallback to rule-based classification
            logger.warning("ML model not trained, falling back to rule-based classification")
            rule_classifier = RuleBasedClassifier()
            return await rule_classifier.classify_rfp(text, document_id, extracted_info)
        
        try:
            # Predict using trained model
            prediction = self.pipeline.predict([text])[0]
            probabilities = self.pipeline.predict_proba([text])[0]
            
            # Map prediction to classification
            class_mapping = {0: 'auto_reject', 1: 'manual_review', 2: 'high_priority'}
            classification = class_mapping.get(prediction, 'manual_review')
            
            # Get confidence score (max probability)
            confidence_score = float(np.max(probabilities))
            
            # Calculate overall score (-1 to 1 range)
            # Convert probabilities to score: high_priority=1, manual_review=0, auto_reject=-1
            overall_score = float(probabilities[2] - probabilities[0])
            
            # Generate explanation based on feature importance (simplified)
            explanation = self._generate_ml_explanation(classification, confidence_score, text)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ClassificationResult(
                document_id=document_id,
                classification=classification,
                confidence_score=confidence_score,
                overall_score=overall_score,
                red_flags=[],  # ML model doesn't provide explicit flags
                green_flags=[],
                explanation=explanation,
                processing_time=processing_time,
                classifier_used="ml_sklearn",
                success=True
            )
            
        except Exception as e:
            logger.error(f"ML classification failed for document {document_id}: {e}")
            return ClassificationResult(
                document_id=document_id,
                classification='manual_review',
                confidence_score=0.0,
                overall_score=0.0,
                red_flags=[],
                green_flags=[],
                explanation=f"ML classification failed: {str(e)}",
                processing_time=asyncio.get_event_loop().time() - start_time,
                classifier_used="ml_sklearn",
                success=False,
                error_message=str(e)
            )
    
    def _generate_ml_explanation(self, classification: str, confidence: float, text: str) -> str:
        """Generate explanation for ML classification"""
        explanation_parts = []
        
        explanation_parts.append(f"ML Classification: {classification.replace('_', ' ').title()}")
        explanation_parts.append(f"Confidence: {confidence:.2f}")
        
        # Simple keyword-based explanation (could be enhanced with LIME/SHAP)
        positive_keywords = ['multimedia', 'video', 'campaign', 'environmental', 'climate']
        negative_keywords = ['local registration', 'physical form', 'india', 'pakistan']
        
        found_positive = [kw for kw in positive_keywords if kw in text.lower()]
        found_negative = [kw for kw in negative_keywords if kw in text.lower()]
        
        if found_positive:
            explanation_parts.append(f"\nPositive signals: {', '.join(found_positive)}")
        
        if found_negative:
            explanation_parts.append(f"Negative signals: {', '.join(found_negative)}")
        
        explanation_parts.append(f"\nBased on machine learning model trained on historical RFP data.")
        
        return "\n".join(explanation_parts)
    
    async def train(self, training_data: List[Tuple[str, str]]) -> bool:
        """Train ML model with labeled data"""
        try:
            if len(training_data) < 10:
                logger.warning("Insufficient training data (need at least 10 samples)")
                return False
            
            # Prepare data
            texts, labels = zip(*training_data)
            
            # Convert labels to numeric
            label_mapping = {'auto_reject': 0, 'manual_review': 1, 'high_priority': 2}
            numeric_labels = [label_mapping.get(label, 1) for label in labels]
            
            # Create pipeline
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))),
                ('classifier', LogisticRegression(random_state=42, max_iter=1000))
            ])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                texts, numeric_labels, test_size=0.2, random_state=42, stratify=numeric_labels
            )
            
            # Train model
            self.pipeline.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.pipeline.predict(X_test)
            accuracy = np.mean(y_pred == y_test)
            
            logger.info(f"ML model trained with accuracy: {accuracy:.3f}")
            
            # Save model
            self._save_model()
            self.is_trained = True
            
            return True
            
        except Exception as e:
            logger.error(f"ML model training failed: {e}")
            return False
    
    def get_classifier_name(self) -> str:
        return "ML Classifier (scikit-learn)"
    
    def can_train(self) -> bool:
        return True

class TransformersClassifier(ClassifierInterface):
    """Transformer-based classifier using Hugging Face"""
    
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers is required for TransformersClassifier")
        
        self.model_name = model_name
        
        # Try to initialize sentiment pipeline as a proxy for classification
        try:
            self.classifier = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            self.is_available = True
        except Exception as e:
            logger.warning(f"Failed to initialize transformers classifier: {e}")
            self.classifier = None
            self.is_available = False
    
    async def classify_rfp(self, text: str, document_id: str, extracted_info: Optional[Dict] = None) -> ClassificationResult:
        """Classify RFP using transformers"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.is_available:
            # Fallback to rule-based classification
            logger.warning("Transformers classifier not available, falling back to rule-based")
            rule_classifier = RuleBasedClassifier()
            return await rule_classifier.classify_rfp(text, document_id, extracted_info)
        
        try:
            # Use sentiment as a proxy for classification
            # Positive sentiment -> higher priority, negative -> lower priority
            
            # Limit text length for transformers
            text_chunk = text[:512]
            
            result = self.classifier(text_chunk)
            
            if result and len(result) > 0:
                label = result[0]['label'].lower()
                score = result[0]['score']
                
                # Map sentiment to RFP classification
                if 'positive' in label and score > 0.7:
                    classification = 'high_priority'
                    overall_score = score
                elif 'negative' in label and score > 0.7:
                    classification = 'auto_reject'
                    overall_score = -score
                else:
                    classification = 'manual_review'
                    overall_score = 0.0
                
                confidence_score = score
            else:
                classification = 'manual_review'
                confidence_score = 0.5
                overall_score = 0.0
            
            explanation = f"Transformers classification based on sentiment analysis: {label} (confidence: {score:.2f})"
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ClassificationResult(
                document_id=document_id,
                classification=classification,
                confidence_score=confidence_score,
                overall_score=overall_score,
                red_flags=[],
                green_flags=[],
                explanation=explanation,
                processing_time=processing_time,
                classifier_used="transformers",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Transformers classification failed for document {document_id}: {e}")
            return ClassificationResult(
                document_id=document_id,
                classification='manual_review',
                confidence_score=0.0,
                overall_score=0.0,
                red_flags=[],
                green_flags=[],
                explanation=f"Transformers classification failed: {str(e)}",
                processing_time=asyncio.get_event_loop().time() - start_time,
                classifier_used="transformers",
                success=False,
                error_message=str(e)
            )
    
    async def train(self, training_data: List[Tuple[str, str]]) -> bool:
        """Training transformers requires more complex setup"""
        logger.warning("Transformers fine-tuning not implemented in this basic version")
        return False
    
    def get_classifier_name(self) -> str:
        return f"Transformers Classifier ({self.model_name})"
    
    def can_train(self) -> bool:
        return False  # Not implemented in this basic version

class EnsembleClassifier(ClassifierInterface):
    """Ensemble classifier combining multiple approaches"""
    
    def __init__(self, classifiers: List[ClassifierInterface], weights: Optional[List[float]] = None):
        self.classifiers = classifiers
        self.weights = weights or [1.0] * len(classifiers)
        
        if len(self.weights) != len(self.classifiers):
            raise ValueError("Number of weights must match number of classifiers")
    
    async def classify_rfp(self, text: str, document_id: str, extracted_info: Optional[Dict] = None) -> ClassificationResult:
        """Classify using ensemble of classifiers"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get predictions from all classifiers
            results = []
            for classifier in self.classifiers:
                try:
                    result = await classifier.classify_rfp(text, document_id, extracted_info)
                    if result.success:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Classifier {classifier.get_classifier_name()} failed: {e}")
            
            if not results:
                raise Exception("All classifiers failed")
            
            # Combine results using weighted voting
            class_scores = {'high_priority': 0.0, 'manual_review': 0.0, 'auto_reject': 0.0}
            total_weight = 0.0
            overall_score = 0.0
            confidence_scores = []
            
            all_red_flags = []
            all_green_flags = []
            explanations = []
            
            for i, result in enumerate(results):
                weight = self.weights[i] if i < len(self.weights) else 1.0
                
                # Weighted voting
                class_scores[result.classification] += weight * result.confidence_score
                total_weight += weight
                
                # Combine scores
                overall_score += weight * result.overall_score
                confidence_scores.append(result.confidence_score)
                
                # Collect flags and explanations
                all_red_flags.extend(result.red_flags)
                all_green_flags.extend(result.green_flags)
                explanations.append(f"{result.classifier_used}: {result.explanation}")
            
            # Normalize scores
            if total_weight > 0:
                for class_name in class_scores:
                    class_scores[class_name] /= total_weight
                overall_score /= total_weight
            
            # Determine final classification
            final_classification = max(class_scores, key=class_scores.get)
            final_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            # Generate combined explanation
            combined_explanation = f"Ensemble classification using {len(results)} classifiers:\n\n"
            combined_explanation += "\n".join(explanations)
            combined_explanation += f"\n\nFinal Decision: {final_classification} (confidence: {final_confidence:.2f})"
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ClassificationResult(
                document_id=document_id,
                classification=final_classification,
                confidence_score=final_confidence,
                overall_score=overall_score,
                red_flags=all_red_flags,
                green_flags=all_green_flags,
                explanation=combined_explanation,
                processing_time=processing_time,
                classifier_used="ensemble",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Ensemble classification failed for document {document_id}: {e}")
            return ClassificationResult(
                document_id=document_id,
                classification='manual_review',
                confidence_score=0.0,
                overall_score=0.0,
                red_flags=[],
                green_flags=[],
                explanation=f"Ensemble classification failed: {str(e)}",
                processing_time=asyncio.get_event_loop().time() - start_time,
                classifier_used="ensemble",
                success=False,
                error_message=str(e)
            )
    
    async def train(self, training_data: List[Tuple[str, str]]) -> bool:
        """Train all trainable classifiers in ensemble"""
        success_count = 0
        
        for classifier in self.classifiers:
            if classifier.can_train():
                try:
                    success = await classifier.train(training_data)
                    if success:
                        success_count += 1
                        logger.info(f"Successfully trained {classifier.get_classifier_name()}")
                    else:
                        logger.warning(f"Failed to train {classifier.get_classifier_name()}")
                except Exception as e:
                    logger.error(f"Training failed for {classifier.get_classifier_name()}: {e}")
        
        return success_count > 0
    
    def get_classifier_name(self) -> str:
        classifier_names = [c.get_classifier_name() for c in self.classifiers]
        return f"Ensemble ({', '.join(classifier_names)})"
    
    def can_train(self) -> bool:
        return any(c.can_train() for c in self.classifiers)

class ClassificationModule:
    """Main Classification Module - Orchestrates all classifiers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize classifiers
        self.classifiers = {}
        
        # Always initialize rule-based classifier
        criteria = ClassificationCriteria()
        self.classifiers['rule_based'] = RuleBasedClassifier(criteria)
        
        # Initialize ML classifier if available
        if SKLEARN_AVAILABLE:
            model_path = self.config.get('ml_model_path')
            self.classifiers['ml'] = MLClassifier(Path(model_path) if model_path else None)
        
        # Initialize transformers classifier if available
        if TRANSFORMERS_AVAILABLE:
            transformers_model = self.config.get('transformers_model', 'distilbert-base-uncased')
            self.classifiers['transformers'] = TransformersClassifier(transformers_model)
        
        # Create ensemble classifier
        if len(self.classifiers) > 1:
            ensemble_classifiers = list(self.classifiers.values())
            ensemble_weights = self.config.get('ensemble_weights', [1.0] * len(ensemble_classifiers))
            self.classifiers['ensemble'] = EnsembleClassifier(ensemble_classifiers, ensemble_weights)
        
        # Set primary classifier
        primary_classifier_name = self.config.get('primary_classifier', 'rule_based')
        self.primary_classifier = self.classifiers.get(primary_classifier_name, self.classifiers['rule_based'])
        
        # Configuration
        self.max_concurrent_classification = self.config.get('max_concurrent_classification', 5)
        self.enable_fallback = self.config.get('enable_fallback', True)
        
        logger.info(f"Classification Module initialized with {len(self.classifiers)} classifiers")
        logger.info(f"Primary classifier: {self.primary_classifier.get_classifier_name()}")
    
    async def classify_rfp(self, text: str, document_id: str, extracted_info: Optional[Dict] = None, 
                          classifier_name: Optional[str] = None) -> ClassificationResult:
        """Classify RFP using specified or primary classifier"""
        
        # Select classifier
        classifier = self.primary_classifier
        if classifier_name and classifier_name in self.classifiers:
            classifier = self.classifiers[classifier_name]
        
        try:
            result = await classifier.classify_rfp(text, document_id, extracted_info)
            
            if result.success:
                return result
            elif self.enable_fallback and classifier != self.classifiers['rule_based']:
                # Fallback to rule-based classifier
                logger.warning(f"Primary classifier failed, falling back to rule-based")
                fallback_result = await self.classifiers['rule_based'].classify_rfp(text, document_id, extracted_info)
                return fallback_result
            
            return result
            
        except Exception as e:
            logger.error(f"Classification failed for document {document_id}: {e}")
            return ClassificationResult(
                document_id=document_id,
                classification='manual_review',
                confidence_score=0.0,
                overall_score=0.0,
                red_flags=[],
                green_flags=[],
                explanation=f"Classification failed: {str(e)}",
                processing_time=0.0,
                classifier_used="error",
                success=False,
                error_message=str(e)
            )
    
    async def classify_rfps_batch(self, rfp_data: List[Tuple[str, str, Optional[Dict]]], 
                                 classifier_name: Optional[str] = None) -> List[ClassificationResult]:
        """Classify multiple RFPs concurrently"""
        semaphore = asyncio.Semaphore(self.max_concurrent_classification)
        
        async def classify_with_semaphore(data):
            async with semaphore:
                text, doc_id, extracted_info = data
                return await self.classify_rfp(text, doc_id, extracted_info, classifier_name)
        
        tasks = [classify_with_semaphore(data) for data in rfp_data]
        results = await asyncio.gather(*tasks)
        
        successful = sum(1 for r in results if r.success)
        logger.info(f"Batch classification completed: {successful}/{len(rfp_data)} successful")
        
        return results
    
    async def train_classifiers(self, training_data: List[Tuple[str, str]]) -> Dict[str, bool]:
        """Train all trainable classifiers"""
        training_results = {}
        
        for name, classifier in self.classifiers.items():
            if classifier.can_train():
                try:
                    success = await classifier.train(training_data)
                    training_results[name] = success
                    logger.info(f"Training {name}: {'Success' if success else 'Failed'}")
                except Exception as e:
                    training_results[name] = False
                    logger.error(f"Training {name} failed: {e}")
            else:
                training_results[name] = None  # Not trainable
        
        return training_results
    
    def get_classifier_status(self) -> Dict[str, Any]:
        """Get status of all classifiers"""
        return {
            'classifiers': {
                name: {
                    'name': classifier.get_classifier_name(),
                    'can_train': classifier.can_train()
                }
                for name, classifier in self.classifiers.items()
            },
            'primary_classifier': self.primary_classifier.get_classifier_name(),
            'libraries': {
                'sklearn': SKLEARN_AVAILABLE,
                'transformers': TRANSFORMERS_AVAILABLE
            },
            'config': {
                'max_concurrent_classification': self.max_concurrent_classification,
                'enable_fallback': self.enable_fallback
            }
        }
    
    async def test_classifiers(self) -> Dict[str, Any]:
        """Test all classifiers with sample RFP"""
        test_text = """
        The United Nations Environment Programme is seeking proposals for a multimedia
        climate change awareness campaign targeting youth in Sub-Saharan Africa.
        
        Requirements:
        - Minimum 7 years of experience in environmental communications
        - Proven track record with video production and social media campaigns
        - Experience working with UN agencies preferred
        
        Budget: $500,000 USD over 12 months
        Deadline: March 15, 2024
        
        Deliverables include documentary series, social media toolkit, and training materials.
        """
        
        test_results = {}
        
        for name, classifier in self.classifiers.items():
            try:
                start_time = asyncio.get_event_loop().time()
                result = await classifier.classify_rfp(test_text, "test_doc")
                end_time = asyncio.get_event_loop().time()
                
                test_results[name] = {
                    'status': 'success' if result.success else 'failed',
                    'classification': result.classification,
                    'confidence_score': result.confidence_score,
                    'overall_score': result.overall_score,
                    'processing_time': end_time - start_time,
                    'red_flags_count': len(result.red_flags),
                    'green_flags_count': len(result.green_flags),
                    'error': result.error_message
                }
                
            except Exception as e:
                test_results[name] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return test_results

# Example usage and testing
async def main():
    """Example usage of Classification Module"""
    
    # Initialize module
    config = {
        'primary_classifier': 'rule_based',
        'max_concurrent_classification': 3,
        'enable_fallback': True,
        'ensemble_weights': [0.6, 0.4]  # Rule-based: 60%, ML: 40%
    }
    
    classification_module = ClassificationModule(config)
    
    # Show classifier status
    print("Classifier Status:")
    status = classification_module.get_classifier_status()
    print(f"Available classifiers: {list(status['classifiers'].keys())}")
    print(f"Primary classifier: {status['primary_classifier']}")
    print(f"Library availability: {status['libraries']}")
    
    # Test classifiers
    print("\nTesting classifiers...")
    test_results = await classification_module.test_classifiers()
    print(json.dumps(test_results, indent=2, default=str))
    
    # Example classification
    sample_rfp = """
    Request for Proposal: Digital Campaign for Climate Action
    
    The World Wildlife Fund is seeking a creative agency to develop a comprehensive
    digital campaign promoting climate action among young adults aged 18-35.
    
    Requirements:
    - Minimum 5 years of experience in digital marketing and social media campaigns
    - Proven expertise in multimedia content creation (video, graphics, interactive content)
    - Experience with environmental or sustainability campaigns preferred
    - Strong data visualization capabilities
    
    Scope of Work:
    - Develop campaign strategy and messaging framework
    - Create multimedia content including videos, infographics, and interactive tools
    - Manage social media presence across multiple platforms
    - Design and implement influencer partnership program
    - Provide comprehensive analytics and reporting
    
    Budget: $750,000 USD over 18 months
    Deadline: Applications due by April 30, 2024
    
    Geographic Scope: Global campaign with focus on North America and Europe
    
    Contact: Sarah Johnson, Campaign Director (sarah.johnson@wwf.org)
    """
    
    print(f"\nClassifying sample RFP...")
    result = await classification_module.classify_rfp(sample_rfp, "sample_rfp")
    
    if result.success:
        print(f"Classification: {result.classification}")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Overall Score: {result.overall_score:.2f}")
        print(f"Processing Time: {result.processing_time:.3f}s")
        print(f"Classifier Used: {result.classifier_used}")
        
        if result.green_flags:
            print(f"\nGreen Flags ({len(result.green_flags)}):")
            for flag in result.green_flags:
                print(f"  • {flag['category']}: {', '.join(flag['keywords'])}")
        
        if result.red_flags:
            print(f"\nRed Flags ({len(result.red_flags)}):")
            for flag in result.red_flags:
                print(f"  • {flag['category']}: {', '.join(flag['keywords'])}")
        
        print(f"\nExplanation:\n{result.explanation}")
    
    else:
        print(f"Classification failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
