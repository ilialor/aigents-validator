from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer
from ..llm.semantic_analyzer import SemanticAnalyzer
from .practice_classifier import PracticeClassifier, PracticeType

class UtilityAnalyzer(BaseAnalyzer):
    """Анализатор полезности (U)"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.classifier = PracticeClassifier()
        
    def analyze_sync(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        practice_type = self.classifier.classify(practice_data)
        
        if practice_type == PracticeType.SCIENTIFIC:
            return self._analyze_scientific_utility(practice_data)
        elif practice_type == PracticeType.ENGINEERING:
            return self._analyze_engineering_utility(practice_data)
        elif practice_type == PracticeType.PROCESS:
            return self._analyze_process_utility(practice_data)
        else:
            return self._analyze_management_utility(practice_data)
            
    def _analyze_scientific_utility(self, data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "research_value": self._analyze_research_value(data),
            "methodology_strength": self._analyze_methodology(data),
            "validation_quality": self._analyze_validation(data)
        }
        weights = {
            "research_value": 0.5,
            "methodology_strength": 0.3,
            "validation_quality": 0.2
        }
        return self._calculate_final_score(scores, weights, data)
        
    def _analyze_engineering_utility(self, data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "technical_value": self._analyze_technical_value(data),
            "implementation_quality": self._analyze_implementation(data),
            "performance_impact": self._analyze_performance(data)
        }
        weights = {"technical_value": 0.4, "implementation_quality": 0.3, "performance_impact": 0.3}
        return self._calculate_final_score(scores, weights, data)
    
    async def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        """Асинхронный анализ с использованием LLM"""
        text = self._prepare_text(practice_data)
        llm_scores = await self.semantic_analyzer.analyze_utility(text)
        basic_scores = self._analyze_basic_metrics(practice_data)
        final_scores = self._combine_scores(llm_scores, basic_scores)
        return final_scores
    
    def _analyze_fundamental_value(self, data: Dict[str, Any]) -> float:
        """Оценка фундаментальной ценности"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')} {' '.join(str(step.get('description', '')) for step in data.get('implementation_steps', []))}"
        text = text.lower()
        
        # Базовые научные индикаторы
        fundamental_patterns = {
            "scientific": ["scientific", "statistical", "empirical", "methodology"],
            "analysis": ["analysis", "testing", "verification", "validation"],
            "systematic": ["systematic", "structured", "formal", "rigorous"],
            "theoretical": ["theory", "model", "framework", "principle"]
        }
        
        # Проверяем каждую категорию
        for category, terms in fundamental_patterns.items():
            found = sum(1 for term in terms if term in text)
            if found > 0:
                score += min(found * 2.5, 5.0)
        
        # Проверяем конкретные фразы
        specific_phrases = [
            (r'p\s*[<>=]\s*0\.\d+', 3.0),
            (r'\d+%\s*confidence', 2.5),
            ("hypothesis", 2.0),
            ("evidence", 2.0),
            ("proof", 2.0)
        ]
        
        for pattern, points in specific_phrases:
            if isinstance(pattern, str):
                if pattern in text:
                    score += points
            else:
                if re.search(pattern, text):
                    score += points
                
        return self._normalize_score(score)
    
    def _analyze_practical_value(self, data: Dict[str, Any]) -> float:
        """Оценка практической ценности"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')} {data.get('summary', '')}"
        text = text.lower()
        
        # Проверяем практические результаты
        practical_indicators = {
            "results": ["improves", "enhances", "optimizes", "solves", "helps"],
            "metrics": ["performance", "efficiency", "quality", "accuracy", "speed"],
            "impact": ["impact", "effect", "benefit", "advantage", "value"]
        }
        
        for category, terms in practical_indicators.items():
            found = sum(1 for term in terms if term in text)
            if found > 0:
                score += min(found * 2.0, 4.0)
            
        return self._normalize_score(score)
    
    def _analyze_measurable_value(self, data: Dict[str, Any]) -> float:
        """Оценка измеримой ценности"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        
        measurable_indicators = [
            ("quantitative metrics", 5.0),
            ("reproducible results", 4.0),
            ("empirical evidence", 4.0),
            ("mathematical model", 3.5),
            ("formal verification", 3.5),
            ("systematic approach", 3.0),
            ("proven methodology", 3.0)
        ]
        
        for term, points in measurable_indicators:
            if term in text.lower():
                score += points
                
        return self._normalize_score(score)
    
    def _normalize_score(self, score: float, max_score: float = 10.0) -> float:
        """Нормализует оценку"""
        return min(max(score, 0.0), max_score) 
    
    def _calculate_scientific_bonus(self, data: Dict[str, Any]) -> float:
        """Бонус за научный подход"""
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        text = text.lower()
        
        bonus = 0.0
        scientific_indicators = [
            (r'doi:\s*10\.\d+/[\w\.-]+', 2.0),
            (r'p\s*[<>=]\s*0\.\d+', 2.0),
            (r'\d+%\s*confidence', 1.5),
            ("statistical significance", 1.5),
            ("empirical evidence", 1.5),
            ("peer-reviewed", 1.5),
            ("scientific method", 1.0),
            ("systematic approach", 1.0)
        ]
        
        for pattern, points in scientific_indicators:
            if isinstance(pattern, str):
                if pattern in text:
                    bonus += points
            else:
                if re.search(pattern, text):
                    bonus += points
                
        return min(bonus, 3.0) 
    
    def _analyze_research_value(self, data: Dict[str, Any]) -> float:
        """Оценка исследовательской ценности"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        text = text.lower()
        
        research_indicators = [
            ("empirical evidence", 3.0),
            ("statistical significance", 3.0),
            ("peer review", 2.5),
            ("methodology", 2.0),
            ("validation", 2.0),
            ("hypothesis", 1.5)
        ]
        
        for term, points in research_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)
    
    def _analyze_management_utility(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Анализ управленческой практики"""
        scores = {
            "business_value": self._analyze_business_value(data),
            "team_impact": self._analyze_team_impact(data),
            "process_improvement": self._analyze_process_improvement(data)
        }
        weights = {"business_value": 0.4, "team_impact": 0.3, "process_improvement": 0.3}
        return self._calculate_final_score(scores, weights, data)
    
    def _calculate_final_score(self, scores: Dict[str, float], weights: Dict[str, float], data: Dict[str, Any] = None) -> Dict[str, float]:
        """Вычисляет финальную оценку с бонусами"""
        base_score = sum(scores[k] * weights[k] for k in scores)
        
        # Добавляем бонусы за конкретные характеристики
        bonus = 0.0
        
        if data:  # Проверяем, что данные переданы
            text = f"{data.get('solution', '')} {data.get('benefits', '')}"
            text = text.lower()
            
            # Бонус за измеримые результаты
            if re.search(r'\d+%|\d+x|increased by|reduced by', text):
                bonus += 2.0
                
            # Бонус за доказанную эффективность
            if re.search(r'proven|validated|tested|measured', text):
                bonus += 1.5
                
            # Бонус за широкое применение
            if re.search(r'widely used|industry standard|best practice', text):
                bonus += 1.5
        
        final_score = base_score + bonus
        return {
            "score": round(min(final_score, 10.0), 2),
            "details": scores,
            "bonus": bonus
        } 
    
    def _analyze_methodology(self, data: Dict[str, Any]) -> float:
        """Анализ методологической составляющей"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        text = text.lower()
        
        methodology_indicators = [
            ("systematic approach", 3.0),
            ("methodology", 2.5),
            ("framework", 2.0),
            ("protocol", 2.0),
            ("procedure", 1.5),
            ("steps", 1.0)
        ]
        
        for term, points in methodology_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)
    
    def _analyze_validation(self, data: Dict[str, Any]) -> float:
        """Анализ валидации"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        text = text.lower()
        
        validation_indicators = [
            ("empirical validation", 3.0),
            ("statistical analysis", 2.5),
            ("experimental results", 2.5),
            ("verified", 2.0),
            ("tested", 1.5),
            ("proven", 1.5)
        ]
        
        for term, points in validation_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)
    
    def _analyze_process_utility(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Анализ процессной практики"""
        scores = {
            "process_efficiency": self._analyze_process_efficiency(data),
            "team_impact": self._analyze_team_impact(data),
            "scalability": self._analyze_scalability(data)
        }
        weights = {"process_efficiency": 0.4, "team_impact": 0.3, "scalability": 0.3}
        return self._calculate_final_score(scores, weights, data)
    
    def _analyze_process_efficiency(self, data: Dict[str, Any]) -> float:
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        efficiency_indicators = [
            ("improves", 2.0),
            ("optimizes", 2.0),
            ("streamlines", 2.0),
            ("faster", 1.5),
            ("better", 1.5),
            ("efficient", 1.5)
        ]
        
        for term, points in efficiency_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)
    
    def _analyze_team_impact(self, data: Dict[str, Any]) -> float:
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        impact_indicators = [
            ("collaboration", 2.0),
            ("communication", 2.0),
            ("productivity", 2.0),
            ("motivation", 1.5),
            ("engagement", 1.5),
            ("satisfaction", 1.5)
        ]
        
        for term, points in impact_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)
    
    def _analyze_scalability(self, data: Dict[str, Any]) -> float:
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        scalability_indicators = [
            ("scalable", 2.0),
            ("adaptable", 2.0),
            ("flexible", 2.0),
            ("extensible", 1.5),
            ("reusable", 1.5),
            ("modular", 1.5)
        ]
        
        for term, points in scalability_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score) 
    
    def _analyze_business_value(self, data: Dict[str, Any]) -> float:
        """Оценка бизнес-ценности"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        business_indicators = [
            ("roi", 3.0),
            ("cost reduction", 2.5),
            ("efficiency", 2.0),
            ("productivity", 2.0),
            ("revenue", 2.0),
            ("profit", 2.0),
            ("performance", 1.5),
            ("quality", 1.5)
        ]
        
        for term, points in business_indicators:
            if term in text:
                score += points
            
        return self._normalize_score(score)
    
    def _analyze_process_improvement(self, data: Dict[str, Any]) -> float:
        """Оценка улучшения процессов"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        improvement_indicators = [
            ("streamline", 2.0),
            ("optimize", 2.0),
            ("improve", 2.0),
            ("enhance", 1.5),
            ("automate", 1.5),
            ("standardize", 1.5)
        ]
        
        for term, points in improvement_indicators:
            if term in text:
                score += points
            
        return self._normalize_score(score) 