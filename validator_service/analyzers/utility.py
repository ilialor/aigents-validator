from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer

class UtilityAnalyzer(BaseAnalyzer):
    """Анализатор полезности (U)"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_md")
        
    def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "problem_clarity": self._analyze_problem_clarity(practice_data),
            "benefits": self._analyze_benefits(practice_data),
            "efficiency": self._analyze_efficiency(practice_data)
        }
        
        weights = {
            "problem_clarity": 0.35,
            "benefits": 0.35,
            "efficiency": 0.30
        }
        
        final_score = sum(scores[k] * weights[k] for k in scores)
        
        return {
            "score": round(final_score, 2),
            "details": scores,
            "explanation": self._generate_explanation(scores)
        }
    
    def _analyze_problem_clarity(self, data: Dict[str, Any]) -> float:
        score = 0.0
        
        if "problem" in data:
            text = str(data["problem"])
            
            # Проверяем структуру проблемы
            if "how to" in text.lower():
                score += 3.0
                
            # Проверяем наличие целей/результатов
            goals = ["ensuring", "maintaining", "creating", "improving", "reducing"]
            score += sum(2.0 for goal in goals if goal in text.lower())
            
            # Проверяем связь с доменом
            if data.get("domain") and data["domain"].lower() in text.lower():
                score += 2.0
                
        return self._normalize_score(score, 10.0)

    def _analyze_benefits(self, data: Dict[str, Any]) -> float:
        score = 0.0
        
        if "benefits" in data and isinstance(data["benefits"], list):
            benefits = data["benefits"]
            
            for benefit in benefits:
                text = str(benefit)
                
                # Проверяем измеримость
                if any(word in text.lower() for word in ["improved", "increased", "reduced", "better", "enhanced"]):
                    score += 2.0
                    
                # Проверяем конкретность
                if len(text.split()) >= 4:
                    score += 1.0
                    
        return self._normalize_score(score, 10.0)    
    
    def _analyze_efficiency(self, data: Dict[str, Any]) -> float:
        """Анализ эффективности"""
        score = 0.0
        
        # Проверяем наличие оценок затрат
        if data.get("estimated_financial_cost_value"):
            score += 2.0
            
        if data.get("estimated_time_cost_minutes"):
            score += 2.0
            
        # Анализируем соотношение выгод и затрат
        if "benefits" in data and isinstance(data["benefits"], list):
            benefits_text = " ".join(str(b) for b in data["benefits"])
            doc = self.nlp(benefits_text)
            
            # Ищем указания на ROI или эффективность
            roi_indicators = ["roi", "return", "efficiency", "effective", "save"]
            if any(word in benefits_text.lower() for word in roi_indicators):
                score += 3.0
                
            # Проверяем наличие конкретных метрик
            if bool(re.search(r'\d+%?', benefits_text)):
                score += 3.0
                
        return self._normalize_score(score, 10.0)
    
    def _generate_explanation(self, scores: Dict[str, float]) -> str:
        """Генерирует текстовое объяснение оценок"""
        explanations = []
        
        if scores["problem_clarity"] >= 8:
            explanations.append("Проблема описана очень четко")
        elif scores["problem_clarity"] >= 5:
            explanations.append("Описание проблемы адекватное")
        else:
            explanations.append("Требуется улучшить описание проблемы")
            
        if scores["benefits"] >= 8:
            explanations.append("Выгоды конкретны и измеримы")
        elif scores["benefits"] >= 5:
            explanations.append("Выгоды описаны достаточно ясно")
        else:
            explanations.append("Необходимо конкретизировать выгоды")
            
        if scores["efficiency"] >= 8:
            explanations.append("Эффективность хорошо обоснована")
        else:
            explanations.append("Требуется лучшее обоснование эффективности")
            
        return ". ".join(explanations) 