from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer

class ApplicabilityAnalyzer(BaseAnalyzer):
    """Анализатор применимости (A)"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_md")
        
    def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "universality": self._analyze_universality(practice_data),
            "scalability": self._analyze_scalability(practice_data),
            "constraints": self._analyze_constraints(practice_data)
        }
        
        weights = {
            "universality": 0.35,
            "scalability": 0.35,
            "constraints": 0.30
        }
        
        final_score = sum(scores[k] * weights[k] for k in scores)
        
        return {
            "score": round(final_score, 2),
            "details": scores,
            "explanation": self._generate_explanation(scores)
        }
    
    def _analyze_universality(self, data: Dict[str, Any]) -> float:
        score = 0.0
        
        # Анализируем примеры применения
        examples_text = f"{data.get('solution', '')} {data.get('summary', '')}"
        example_indicators = ["can be used", "applicable", "suitable for", "works in"]
        score += sum(2.0 for indicator in example_indicators if indicator in examples_text.lower())
        
        # Проверяем разнообразие доменов
        domains = set()
        if data.get("domain"):
            domains.add(data["domain"])
        if data.get("sub_domains"):
            domains.update(data["sub_domains"])
        if data.get("tags"):
            domains.update(data["tags"])
        
        score += min(len(domains) * 2.0, 6.0)
        
        return self._normalize_score(score, 10.0)

    def _analyze_scalability(self, data: Dict[str, Any]) -> float:
        score = 0.0
        
        # Проверяем адаптивность к разным контекстам
        contexts = ["workplace", "community", "international", "personal", "team", "organization"]
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        score += sum(2.0 for context in contexts if context in text.lower())
        
        # Проверяем модульность шагов
        if isinstance(data.get("implementation_steps"), list):
            if len(data["implementation_steps"]) >= 4:
                score += 4.0
                
        return self._normalize_score(score, 10.0)

    def _analyze_constraints(self, data: Dict[str, Any]) -> float:
        """Анализ ясности ограничений"""
        score = 0.0
        
        if "limitations" in data and isinstance(data["limitations"], list):
            limitations = data["limitations"]
            
            for limit in limitations:
                text = str(limit)
                doc = self.nlp(text)
                
                # Проверяем конкретность ограничения
                has_specifics = any(token.pos_ in ["NUM", "PROPN"] for token in doc)
                has_conditions = any(token.dep_ in ["mark", "prep"] for token in doc)
                
                if has_specifics and has_conditions:
                    score += 3.0
                elif has_specifics or has_conditions:
                    score += 2.0
                elif len(text) >= 30:
                    score += 1.0
                    
            # Учитываем количество ограничений
            score = min(score, 10.0)
            
        return self._normalize_score(score, 10.0)
    
    def _generate_explanation(self, scores: Dict[str, float]) -> str:
        """Генерирует текстовое объяснение оценок"""
        explanations = []
        
        if scores["universality"] >= 8:
            explanations.append("Практика широко применима в разных доменах")
        elif scores["universality"] >= 5:
            explanations.append("Практика имеет достаточную универсальность")
        else:
            explanations.append("Требуется расширить область применения")
            
        if scores["scalability"] >= 8:
            explanations.append("Отличная масштабируемость")
        elif scores["scalability"] >= 5:
            explanations.append("Приемлемая масштабируемость")
        else:
            explanations.append("Нужно улучшить масштабируемость")
            
        if scores["constraints"] >= 8:
            explanations.append("Ограничения четко определены")
        else:
            explanations.append("Требуется уточнить ограничения")
            
        return ". ".join(explanations) 