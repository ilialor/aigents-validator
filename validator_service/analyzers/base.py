from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import spacy
from ..llm.semantic_analyzer import SemanticAnalyzer
import logging

logger = logging.getLogger(__name__)

class BaseAnalyzer:
    """Базовый класс для всех анализаторов критериев"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        logger.info(f"Initializing {self.__class__.__name__} with config: {self.config}")
        if hasattr(self, 'nlp'):
            logger.info("Loading spaCy model 'en_core_web_md'")
            try:
                self.nlp = spacy.load("en_core_web_md")
                logger.info("Successfully loaded spaCy model")
            except Exception as e:
                logger.error(f"Failed to load spaCy model: {e}")
                raise
        self.semantic_analyzer = SemanticAnalyzer()
    
    async def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Асинхронный анализ практики"""
        logger.info(f"Starting analysis in {self.__class__.__name__}")
        try:
            logger.debug(f"Analyzing practice data: {practice_data.get('title', 'No title')}")
            result = self.analyze_sync(practice_data)
            
            if not result or not isinstance(result, dict):
                logger.error(f"Invalid analysis result format: {result}")
                raise ValueError(f"Invalid analysis result: {result}")
                
            if "score" not in result:
                logger.error(f"Missing 'score' in result: {result}")
                raise ValueError(f"Missing 'score' in result: {result}")
                
            logger.info(f"Analysis completed successfully. Score: {result.get('score')}")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__} analyzer: {str(e)}", exc_info=True)
            return {
                "score": 5.0,
                "explanation": f"Error during analysis: {str(e)}",
                "criteria": {},
                "details": {}
            }
        
    def analyze_sync(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        """Синхронный анализ практики"""
        raise NotImplementedError
    
    def _normalize_score(self, score: float, max_score: float = 10.0) -> float:
        """Нормализует оценку к шкале 0-10"""
        if max_score <= 0:
            logger.warning(f"Invalid max_score: {max_score}, returning 0.0")
            return 0.0
        normalized = min((score / max_score) * 10, 10.0)
        logger.debug(f"Normalized score {score} to {normalized} (max_score={max_score})")
        return normalized
    
    def _validate_text(self, text: str, min_length: int = 50) -> bool:
        """Проверяет валидность текста"""
        if not text:
            logger.debug("Empty text provided for validation")
            return False
        is_valid = len(str(text).strip()) >= min_length
        logger.debug(f"Text validation result: {is_valid} (length={len(str(text).strip())}, required={min_length})")
        return is_valid
    
    def _prepare_text(self, practice_data: Dict[str, Any]) -> str:
        """Подготавливает текст практики для анализа"""
        logger.debug("Preparing text for analysis")
        text_parts = [
            practice_data.get('title', ''),
            practice_data.get('summary', ''),
            practice_data.get('problem', ''),
            practice_data.get('solution', ''),
            ' '.join(str(step.get('description', '')) for step in practice_data.get('implementation_steps', [])),
            ' '.join(practice_data.get('benefits', [])),
            ' '.join(practice_data.get('limitations', []))
        ]
        result = ' '.join(filter(None, text_parts))
        logger.debug(f"Prepared text length: {len(result)}")
        return result 