"""
Sentiment Analyzer Module

Provides sentiment analysis capabilities for text data.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field, validator
import json
import re
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

class SentimentLabel(str, Enum):
    """Sentiment labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class EmotionLabel(str, Enum):
    """Emotion labels."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    DISGUST = "disgust"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"

class SentimentResult(BaseModel):
    """Result of a sentiment analysis."""
    text: str
    sentiment: SentimentLabel
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    emotions: Dict[EmotionLabel, float] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)
    language: str = "en"
    tokens: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SentimentAnalyzerConfig(BaseModel):
    """Configuration for the sentiment analyzer."""
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
    use_gpu: bool = False
    batch_size: int = 32
    max_length: int = 512
    threshold: float = 0.1
    language: str = "en"
    cache_size: int = 1000

class SentimentAnalyzer:
    """
    Handles sentiment analysis of text using various models.
    
    This class provides methods to analyze the sentiment and emotions
    in text data, with support for multiple languages and models.
    """
    
    def __init__(self, config: Optional[Union[Dict[str, Any], SentimentAnalyzerConfig]] = None):
        """
        Initialize the sentiment analyzer.
        
        Args:
            config: Configuration as a dict or SentimentAnalyzerConfig
        """
        if config is None:
            config = {}
            
        if isinstance(config, dict):
            self.config = SentimentAnalyzerConfig(**config)
        else:
            self.config = config
            
        self._model = None
        self._tokenizer = None
        self._pipeline = None
        self._emotion_model = None
        self._language_detector = None
        self._cache = {}
        self._cache_order = []
        
        # Initialize the analyzer
        self._initialize_analyzer()
    
    def _initialize_analyzer(self) -> None:
        """Initialize the sentiment analysis models and components."""
        try:
            # Lazy loading of heavy dependencies
            import torch
            from transformers import (
                AutoModelForSequenceClassification,
                AutoTokenizer,
                pipeline,
                AutoModelForTokenClassification
            )
            from transformers.pipelines import TextClassificationPipeline
            
            # Set device
            self.device = 0 if torch.cuda.is_available() and self.config.use_gpu else -1
            
            # Load sentiment model
            self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self.config.model_name
            )
            
            # Create pipeline
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self._model,
                tokenizer=self._tokenizer,
                device=self.device,
                return_all_scores=True
            )
            
            # Try to load emotion model (optional)
            try:
                self._emotion_model = pipeline(
                    "text-classification",
                    model="bhadresh-savani/distilbert-base-uncased-emotion",
                    return_all_scores=True,
                    device=self.device
                )
            except Exception as e:
                logger.warning(f"Failed to load emotion model: {str(e)}")
            
            logger.info(f"Initialized sentiment analyzer with model: {self.config.model_name}")
            
        except ImportError as e:
            logger.error(f"Failed to import required packages: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analyzer: {str(e)}")
            raise
    
    async def analyze(
        self,
        text: str,
        detect_language: bool = False,
        include_emotions: bool = True,
        include_tokens: bool = False
    ) -> SentimentResult:
        """
        Analyze the sentiment of a text.
        
        Args:
            text: Text to analyze
            detect_language: Whether to detect the language of the text
            include_emotions: Whether to include emotion analysis
            include_tokens: Whether to include token information
            
        Returns:
            SentimentResult with analysis results
        """
        # Check cache first
        cache_key = self._generate_cache_key(text, detect_language, include_emotions, include_tokens)
        if cache_key in self._cache:
            self._cache_order.remove(cache_key)
            self._cache_order.append(cache_key)
            return self._cache[cache_key]
        
        try:
            # Detect language if needed
            language = self.config.language
            if detect_language or self.config.language == "auto":
                language = await self._detect_language(text) or self.config.language
            
            # Preprocess text
            processed_text = self._preprocess_text(text, language)
            
            # Analyze sentiment
            sentiment_result = await self._analyze_sentiment(processed_text)
            
            # Analyze emotions if requested
            emotions = {}
            if include_emotions and self._emotion_model:
                emotions = await self._analyze_emotions(processed_text)
            
            # Tokenize if requested
            tokens = None
            if include_tokens and self._tokenizer:
                tokens = self._tokenizer.tokenize(processed_text)
            
            # Create result
            result = SentimentResult(
                text=text,
                sentiment=sentiment_result["label"],
                sentiment_score=sentiment_result["score"],
                emotions=emotions,
                confidence=sentiment_result["confidence"],
                language=language,
                tokens=tokens
            )
            
            # Update cache
            self._update_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}", exc_info=True)
            # Return neutral result on error
            return SentimentResult(
                text=text,
                sentiment=SentimentLabel.NEUTRAL,
                sentiment_score=0.0,
                emotions={},
                confidence=0.0,
                language=language or self.config.language
            )
    
    async def analyze_batch(
        self,
        texts: List[str],
        detect_language: bool = False,
        include_emotions: bool = True,
        include_tokens: bool = False
    ) -> List[SentimentResult]:
        """
        Analyze sentiment for a batch of texts.
        
        Args:
            texts: List of texts to analyze
            detect_language: Whether to detect the language of each text
            include_emotions: Whether to include emotion analysis
            include_tokens: Whether to include token information
            
        Returns:
            List of SentimentResult objects
        """
        results = []
        
        # Process in batches
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            batch_results = await asyncio.gather(*[
                self.analyze(
                    text,
                    detect_language=detect_language,
                    include_emotions=include_emotions,
                    include_tokens=include_tokens
                )
                for text in batch
            ])
            results.extend(batch_results)
        
        return results
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            # Run the pipeline
            result = await asyncio.to_thread(
                self._pipeline,
                text,
                truncation=True,
                max_length=self.config.max_length
            )
            
            # Process the result
            if not result or not isinstance(result, list) or not result[0]:
                return {
                    "label": SentimentLabel.NEUTRAL,
                    "score": 0.0,
                    "confidence": 0.0
                }
            
            # Get the highest confidence label
            scores = {item["label"]: item["score"] for item in result[0]}
            
            # Map labels to our standard format
            label_mapping = {
                "POSITIVE": SentimentLabel.POSITIVE,
                "NEGATIVE": SentimentLabel.NEGATIVE,
                "NEUTRAL": SentimentLabel.NEUTRAL,
                "LABEL_0": SentimentLabel.NEGATIVE,  # Some models use this
                "LABEL_1": SentimentLabel.POSITIVE
            }
            
            # Find the best label
            best_label = None
            best_score = -1.0
            
            for label, score in scores.items():
                if score > best_score:
                    best_score = score
                    best_label = label
            
            # Map to our standard label
            sentiment_label = label_mapping.get(best_label, SentimentLabel.NEUTRAL)
            
            # Calculate sentiment score (-1.0 to 1.0)
            sentiment_score = 0.0
            if sentiment_label == SentimentLabel.POSITIVE:
                sentiment_score = best_score
            elif sentiment_label == SentimentLabel.NEGATIVE:
                sentiment_score = -best_score
            
            return {
                "label": sentiment_label,
                "score": sentiment_score,
                "confidence": best_score
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}", exc_info=True)
            return {
                "label": SentimentLabel.NEUTRAL,
                "score": 0.0,
                "confidence": 0.0
            }
    
    async def _analyze_emotions(self, text: str) -> Dict[EmotionLabel, float]:
        """
        Analyze emotions in a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping emotion labels to confidence scores
        """
        if not self._emotion_model:
            return {}
            
        try:
            # Run the emotion model
            result = await asyncio.to_thread(
                self._emotion_model,
                text,
                truncation=True,
                max_length=self.config.max_length
            )
            
            if not result or not isinstance(result, list) or not result[0]:
                return {}
            
            # Map emotion labels to our standard format
            emotion_mapping = {
                "joy": EmotionLabel.JOY,
                "sadness": EmotionLabel.SADNESS,
                "anger": EmotionLabel.ANGER,
                "fear": EmotionLabel.FEAR,
                "disgust": EmotionLabel.DISGUST,
                "surprise": EmotionLabel.SURPRISE,
                "neutral": EmotionLabel.NEUTRAL
            }
            
            # Extract emotion scores
            emotions = {}
            for item in result[0]:
                label = item["label"].lower()
                score = item["score"]
                
                # Map to our standard label
                emotion_label = emotion_mapping.get(label)
                if emotion_label:
                    emotions[emotion_label] = score
            
            return emotions
            
        except Exception as e:
            logger.error(f"Emotion analysis failed: {str(e)}", exc_info=True)
            return {}
    
    async def _detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'es') or None if detection fails
        """
        try:
            # Lazy load language detector
            if self._language_detector is None:
                from langdetect import detect, LangDetectException
                self._language_detector = detect
            
            # Simple detection for very short texts
            if len(text.strip()) < 10:
                return self.config.language
                
            # Detect language
            lang = await asyncio.to_thread(self._language_detector, text)
            return lang
            
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return self.config.language
    
    def _preprocess_text(self, text: str, language: str) -> str:
        """
        Preprocess text before analysis.
        
        Args:
            text: Text to preprocess
            language: Language code
            
        Returns:
            Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Basic cleaning
        text = text.strip()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _generate_cache_key(
        self,
        text: str,
        detect_language: bool,
        include_emotions: bool,
        include_tokens: bool
    ) -> str:
        """Generate a cache key for the given parameters."""
        key_parts = [
            f"text:{text[:100]}",
            f"lang:{str(detect_language).lower()}",
            f"emo:{str(include_emotions).lower()}",
            f"tokens:{str(include_tokens).lower()}"
        ]
        return "|".join(key_parts)
    
    def _update_cache(self, key: str, result: SentimentResult) -> None:
        """Update the cache with a new result."""
        if len(self._cache) >= self.config.cache_size:
            # Remove the least recently used item
            if self._cache_order:
                oldest_key = self._cache_order.pop(0)
                if oldest_key in self._cache:
                    del self._cache[oldest_key]
        
        # Add to cache
        self._cache[key] = result
        self._cache_order.append(key)

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_sentiment_analyzer():
        # Create a sentiment analyzer
        analyzer = SentimentAnalyzer({
            "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
            "use_gpu": False,
            "cache_size": 100
        })
        
        # Test texts
        texts = [
            "I love this product! It's amazing!",
            "I'm so frustrated with this service. It's terrible!",
            "The weather is nice today.",
            "This is the worst experience I've ever had.",
            "I'm feeling happy and excited about the future!"
        ]
        
        # Analyze each text
        for text in texts:
            print(f"\nAnalyzing: {text}")
            result = await analyzer.analyze(
                text,
                detect_language=True,
                include_emotions=True
            )
            
            print(f"Sentiment: {result.sentiment.value} (score: {result.sentiment_score:.2f})")
            print(f"Confidence: {result.confidence:.2f}")
            
            if result.emotions:
                print("Emotions:")
                for emotion, score in result.emotions.items():
                    print(f"  - {emotion.value}: {score:.2f}")
    
    asyncio.run(test_sentiment_analyzer())
