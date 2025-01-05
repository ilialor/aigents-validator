from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer

class ReliabilityAnalyzer(BaseAnalyzer):
    """Анализатор надежности (Reliability)"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_md")
        
    def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "empirical_validation": self._analyze_empirical_validation(practice_data),
            "methodology": self._analyze_methodology(practice_data),
            "adaptability": self._analyze_adaptability(practice_data),
            "external_validation": self._analyze_external_validation(practice_data)
        }
        
        weights = {
            "empirical_validation": 0.35,
            "methodology": 0.25,
            "adaptability": 0.20,
            "external_validation": 0.20
        }
        
        # Применяем корректирующие факторы
        correction = self._calculate_correction_factors(practice_data)
        
        final_score = sum(scores[k] * weights[k] for k in scores) + correction
        
        return {
            "score": round(final_score, 2),
            "details": scores,
            "correction": correction,
            "explanation": self._generate_explanation(scores, correction)
        }
    
    def _analyze_empirical_validation(self, data: Dict[str, Any]) -> float:
        """Анализ эмпирической валидации"""
        score = 0.0
        
        # Расширяем список индикаторов исследований и доказательств
        research_indicators = {
            "strong": [
                "study", "research", "experiment", "evidence", "proven",
                "standard", "framework", "methodology", "practice", "established"  # Добавляем индикаторы для устоявшихся практик
            ],
            "medium": [
                "tested", "validated", "measured", "observed",
                "implemented", "applied", "used", "adopted"  # Добавляем индикаторы практического применения
            ],
            "metrics": [
                "accuracy", "precision", "efficiency", "performance",
                "improvement", "effectiveness", "quality", "success"  # Расширяем метрики
            ]
        }
        
        # Анализируем все релевантные поля
        text = f"{data.get('solution', '')} {data.get('benefits', '')} {data.get('summary', '')}"
        text = text.lower()
        
        # Увеличиваем веса для устоявшихся практик
        for word in research_indicators["strong"]:
            if word in text:
                score += 3.0  # Было 2.5
        for word in research_indicators["medium"]:
            if word in text:
                score += 2.0  # Было 1.5
        for word in research_indicators["metrics"]:
            if word in text:
                score += 1.5  # Было 1.0
                
        # Добавляем бонус за структурированность и полноту описания
        if isinstance(data.get("implementation_steps"), list) and len(data["implementation_steps"]) >= 4:
            score += 2.0
            
        return self._normalize_score(score, 10.0)
    
    def _analyze_methodology(self, data: Dict[str, Any]) -> float:
        """Анализ методологической прочности"""
        score = 0.0
        
        # Проверяем структуру и полноту описания
        if isinstance(data.get("implementation_steps"), list):
            steps = data["implementation_steps"]
            if len(steps) >= 5:
                score += 3.0
            elif len(steps) >= 3:
                score += 2.0
                
        # Проверяем наличие требований и ограничений
        if isinstance(data.get("implementation_requirements"), list):
            score += min(len(data["implementation_requirements"]) * 1.5, 3.0)
            
        if isinstance(data.get("limitations"), list):
            score += min(len(data["limitations"]) * 1.5, 3.0)
            
        # Анализируем логическую связность
        text = f"{data.get('problem', '')} {data.get('solution', '')}"
        doc = self.nlp(text)
        
        # Проверяем наличие логических связок
        logical_markers = ["therefore", "because", "consequently", "thus", "hence"]
        if any(marker in text.lower() for marker in logical_markers):
            score += 1.0
            
        return self._normalize_score(score, 10.0)
    
    def _analyze_adaptability(self, data: Dict[str, Any]) -> float:
        """Анализ адаптивности"""
        score = 0.0
        
        # Расширяем индикаторы адаптивности
        adapt_indicators = {
            "high": [
                "adapt", "flexible", "customize", "configure",
                "scalable", "modular", "extensible"  # Добавляем индикаторы масштабируемости
            ],
            "medium": [
                "adjust", "modify", "tune", "parameter",
                "update", "maintain", "improve"  # Добавляем индикаторы поддержки
            ],
            "context": [
                "environment", "condition", "scenario", "case",
                "organization", "domain", "context", "situation"  # Расширяем контекстные индикаторы
            ]
        }
        
        # Анализируем больше полей
        text = f"{data.get('solution', '')} {data.get('implementation_steps', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        for word in adapt_indicators["high"]:
            if word in text:
                score += 3.0  # Было 2.5
        for word in adapt_indicators["medium"]:
            if word in text:
                score += 2.0  # Было 1.5
        for word in adapt_indicators["context"]:
            if word in text:
                score += 1.5  # Было 1.0
                
        # Добавляем бонус за наличие вариаций применения
        if data.get("domain") and data.get("sub_domains"):
            score += 2.0
            
        return self._normalize_score(score, 10.0)
    
    def _analyze_external_validation(self, data: Dict[str, Any]) -> float:
        score = 0.0
        
        validation_indicators = {
            "strong": [
                "certified", "approved", "standardized", "recognized",
                "established", "proven", "industry-standard", "professional"
            ],
            "medium": [
                "recommended", "endorsed", "supported", "accepted",
                "trusted", "reliable", "effective", "successful"
            ],
            "usage": [
                "widely used", "adopted", "implemented", "common practice",
                "best practice", "standard practice", "established method"
            ]
        }
        
        text = f"{data.get('solution', '')} {data.get('benefits', '')} {data.get('summary', '')}"
        text = text.lower()
        
        for category in validation_indicators.values():
            for word in category:
                if word in text:
                    score += 2.5
                    
        # Добавляем бонус за наличие примеров применения
        if "examples" in text.lower():
            score += 2.0
            
        return self._normalize_score(score, 10.0)

    def _calculate_correction_factors(self, data: Dict[str, Any]) -> float:
        """Расчет корректирующих факторов"""
        correction = 0.0
        
        text = f"{data.get('solution', '')} {data.get('limitations', '')}"
        text = text.lower()
        
        # Новизна практики (-0.05)
        if any(word in text for word in ["new", "novel", "recent"]):
            correction -= 0.5
            
        # Ограниченность данных (-0.05)
        if "limited data" in text or "preliminary results" in text:
            correction -= 0.5
            
        # Противоречивые результаты (-0.10)
        if any(word in text for word in ["contradictory", "inconsistent", "varies"]):
            correction -= 1.0
            
        return correction
    
    def _generate_explanation(self, scores: Dict[str, float], correction: float) -> str:
        """Генерирует текстовое объяснение оценок"""
        explanations = []
        
        if scores["empirical_validation"] >= 8:
            explanations.append("Сильная эмпирическая база")
        elif scores["empirical_validation"] >= 5:
            explanations.append("Достаточная эмпирическая валидация")
        else:
            explanations.append("Требуется больше эмпирических данных")
            
        if scores["methodology"] >= 8:
            explanations.append("Методология хорошо проработана")
        elif scores["methodology"] >= 5:
            explanations.append("Методология адекватна")
        else:
            explanations.append("Требуется улучшить методологию")
            
        if correction < 0:
            explanations.append(f"Применены корректирующие факторы ({correction})")
            
        return ". ".join(explanations) 