from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer

class InnovationAnalyzer(BaseAnalyzer):
    """Анализатор инновационности (I)"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_md")
        
    def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "novelty": self._analyze_novelty(practice_data),
            "tech_complexity": self._analyze_tech_complexity(practice_data),
            "potential": self._analyze_potential(practice_data)
        }
        
        weights = {
            "novelty": 0.4,
            "tech_complexity": 0.3,
            "potential": 0.3
        }
        
        final_score = sum(scores[k] * weights[k] for k in scores)
        
        return {
            "score": round(final_score, 2),
            "details": scores,
            "explanation": self._generate_explanation(scores)
        }
    
    def _analyze_novelty(self, data: Dict[str, Any]) -> float:
        """Анализ новизны подхода"""
        score = 0.0
        
        # Ключевые слова для новизны
        novelty_indicators = {
            "high": ["new", "novel", "innovative", "unique", "original", "pioneering"],
            "medium": ["improved", "enhanced", "advanced", "modern"],
            "low": ["traditional", "conventional", "standard", "typical"]
        }
        
        # Анализируем разные поля на признаки новизны
        text = f"{data.get('solution', '')} {data.get('summary', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        # Проверяем наличие индикаторов
        for word in novelty_indicators["high"]:
            if word in text:
                score += 2.5
        for word in novelty_indicators["medium"]:
            if word in text:
                score += 1.5
        for word in novelty_indicators["low"]:
            if word in text:
                score -= 1.0
                
        # Проверяем теги на инновационность
        if isinstance(data.get("tags"), list):
            innovation_tags = ["innovation", "ai", "ml", "blockchain", "emerging"]
            score += sum(2.0 for tag in data["tags"] if any(i_tag in tag.lower() for i_tag in innovation_tags))
            
        return self._normalize_score(score, 10.0)
    
    def _analyze_tech_complexity(self, data: Dict[str, Any]) -> float:
        """Анализ технологической сложности"""
        score = 0.0
        
        # Технологические индикаторы
        tech_indicators = {
            "advanced": ["ai", "ml", "blockchain", "quantum", "neural"],
            "modern": ["cloud", "microservices", "api", "distributed"],
            "tools": ["python", "tensorflow", "kubernetes", "docker"]
        }
        
        # Анализируем текст на технологии
        text = f"{data.get('solution', '')} {data.get('implementation_requirements', '')}"
        text = text.lower()
        
        # Подсчитываем технологические термины
        for word in tech_indicators["advanced"]:
            if word in text:
                score += 3.0
        for word in tech_indicators["modern"]:
            if word in text:
                score += 2.0
        for word in tech_indicators["tools"]:
            if word in text:
                score += 1.0
                
        # Проверяем сложность реализации
        if isinstance(data.get("implementation_steps"), list):
            steps = data["implementation_steps"]
            if len(steps) >= 5:
                score += 2.0
                
        return self._normalize_score(score, 10.0)
    
    def _analyze_potential(self, data: Dict[str, Any]) -> float:
        score = 0.0
        
        # Проверяем потенциал развития
        potential_indicators = {
            "future": ["future", "potential", "roadmap", "vision", "long-term"],
            "growth": ["expand", "extend", "grow", "scale", "develop"],
            "impact": ["transform", "improve", "enhance", "strengthen"]
        }
        
        text = f"{data.get('benefits', '')} {data.get('solution', '')}"
        text = text.lower()
        
        for category in potential_indicators.values():
            for word in category:
                if word in text:
                    score += 2.0
                    
        # Проверяем наличие вариаций применения
        if isinstance(data.get("implementation_steps"), list):
            score += 2.0
            
        return self._normalize_score(score, 10.0)

    def _generate_explanation(self, scores: Dict[str, float]) -> str:
        """Генерирует текстовое объяснение оценок"""
        explanations = []
        
        if scores["novelty"] >= 8:
            explanations.append("Высокая степень новизны")
        elif scores["novelty"] >= 5:
            explanations.append("Присутствуют инновационные элементы")
        else:
            explanations.append("Требуется усилить инновационность")
            
        if scores["tech_complexity"] >= 8:
            explanations.append("Использует передовые технологии")
        elif scores["tech_complexity"] >= 5:
            explanations.append("Умеренная технологическая сложность")
        else:
            explanations.append("Можно усилить технологическую составляющую")
            
        if scores["potential"] >= 8:
            explanations.append("Большой потенциал развития")
        else:
            explanations.append("Требуется лучше описать потенциал развития")
            
        return ". ".join(explanations) 