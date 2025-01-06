from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import spacy

class BaseAnalyzer:
    """Базовый класс для всех анализаторов критериев"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        if hasattr(self, 'nlp'):
            self.nlp = spacy.load("en_core_web_md")
    
    async def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        """Асинхронный анализ практики"""
        return self.analyze_sync(practice_data)
        
    def analyze_sync(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        """Синхронный анализ практики"""
        raise NotImplementedError
    
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