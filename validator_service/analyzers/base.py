from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import spacy
from validator_service.quality_wheel import QualityWheel

class BaseAnalyzer(ABC):
    """Базовый класс для всех анализаторов критериев"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.quality_wheel = QualityWheel()
        if hasattr(self, 'nlp'):
            self.nlp = spacy.load("en_core_web_md")
    
    @abstractmethod
    def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Анализирует практику и возвращает оценку с объяснениями
        
        Returns:
            Dict с оценкой и объяснением, например:
            {
                "score": 8.5,
                "explanation": "Подробное объяснение оценки..."
            }
        """
        pass
    
    def _normalize_score(self, score: float, max_score: float = 10.0) -> float:
        """Нормализует оценку к шкале 0-10"""
        if max_score <= 0:
            return 0.0
        return min((score / max_score) * 10, 10.0)
    
    def _validate_text(self, text: str, min_length: int = 50) -> bool:
        """Проверяет валидность текста"""
        if not text:
            return False
        return len(str(text).strip()) >= min_length 
    
    def validate_scores(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """Валидация оценок с использованием штурвала качества"""
        return self.quality_wheel.evaluate_practice(scores) 