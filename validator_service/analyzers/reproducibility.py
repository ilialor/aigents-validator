from typing import Dict, Any, List
import spacy
from textblob import TextBlob
from .base import BaseAnalyzer

class ReproducibilityAnalyzer(BaseAnalyzer):
    """Анализатор воспроизводимости (R)"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_md")
        
    def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "steps_clarity": self._analyze_steps_clarity(practice_data),
            "requirements": self._analyze_requirements(practice_data),
            "resources": self._analyze_resources(practice_data)
        }
        
        weights = {
            "steps_clarity": 0.4,
            "requirements": 0.3,
            "resources": 0.3
        }
        
        final_score = sum(scores[k] * weights[k] for k in scores)
        
        return {
            "score": round(final_score, 2),
            "details": scores,
            "explanation": self._generate_explanation(scores)
        }
    
    def _analyze_steps_clarity(self, data: Dict[str, Any]) -> float:
        """Анализ четкости шагов реализации"""
        score = 0.0
        
        if "implementation_steps" in data and isinstance(data["implementation_steps"], list):
            steps = data["implementation_steps"]
            
            # Проверяем каждый шаг
            for step in steps:
                if isinstance(step, dict) and "description" in step:
                    text = str(step["description"])
                    doc = self.nlp(text)
                    
                    # Проверяем наличие глаголов действия
                    has_action_verb = any(token.pos_ == "VERB" for token in doc)
                    
                    # Проверяем конкретность описания
                    has_specifics = any(token.pos_ in ["NUM", "PROPN"] for token in doc)
                    
                    # Проверяем длину описания
                    if len(text) >= 50 and has_action_verb:
                        score += 2.0
                        if has_specifics:
                            score += 1.0
                            
            # Нормализуем с учетом количества шагов
            score = min(score, 10.0)
            
        return self._normalize_score(score, 10.0)
    
    def _analyze_requirements(self, data: Dict[str, Any]) -> float:
        score = 0.0
        
        if "implementation_requirements" in data:
            requirements = data["implementation_requirements"]
            if isinstance(requirements, list):
                # Оцениваем каждое требование
                for req in requirements:
                    text = str(req)
                    # Проверяем конкретность требования
                    if len(text.split()) >= 3:  # Более детальное описание
                        score += 2.0
                    else:
                        score += 1.0
                        
                    # Проверяем связь с доменом
                    if any(domain in text.lower() for domain in data.get("sub_domains", [])):
                        score += 0.5
                        
        # Добавляем бонус за структурированность
        if isinstance(data.get("implementation_steps"), list):
            score += 2.0
            
        return self._normalize_score(score, 10.0)    

    def _analyze_resources(self, data: Dict[str, Any]) -> float:
        """Анализ оценки ресурсов"""
        score = 0.0
        
        # Проверяем финансовые оценки
        if data.get("estimated_financial_cost_value"):
            score += 3.0
            
        # Проверяем временные оценки    
        if data.get("estimated_time_cost_minutes"):
            score += 3.0
            
        # Проверяем список ресурсов
        if "estimated_resources" in data and isinstance(data["estimated_resources"], list):
            resources = data["estimated_resources"]
            score += min(len(resources), 4) * 1.0
            
        return self._normalize_score(score, 10.0)
    
    def _generate_explanation(self, scores: Dict[str, float]) -> str:
        """Генерирует текстовое объяснение оценок"""
        explanations = []
        
        if scores["steps_clarity"] >= 8:
            explanations.append("Шаги реализации очень четкие и подробные")
        elif scores["steps_clarity"] >= 5:
            explanations.append("Шаги реализации достаточно понятны")
        else:
            explanations.append("Требуется улучшить описание шагов реализации")
            
        if scores["requirements"] >= 8:
            explanations.append("Требования четко определены")
        elif scores["requirements"] >= 5:
            explanations.append("Требования описаны адекватно")
        else:
            explanations.append("Требования нуждаются в уточнении")
            
        if scores["resources"] >= 8:
            explanations.append("Ресурсы оценены детально")
        else:
            explanations.append("Требуется более точная оценка ресурсов")
            
        return ". ".join(explanations) 