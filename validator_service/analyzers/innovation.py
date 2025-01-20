from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer
from .practice_classifier import PracticeClassifier, PracticeType

class InnovationAnalyzer(BaseAnalyzer):
    """Анализатор инновационности (I)"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_md")
        self.classifier = PracticeClassifier()
        
    def analyze_sync(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        practice_type, is_concept = self.classifier.classify(practice_data)
        base_score = self._get_base_innovation_score(practice_data)
        
        # Используем .value для доступа к строковому значению enum
        type_multipliers = {
            PracticeType.SCIENTIFIC.value: 1.4,    # Научные практики обычно более инновационны
            PracticeType.ENGINEERING.value: 1.3,   # Инженерные практики тоже часто инновационны
            PracticeType.PROCESS.value: 1.1,       # Процессные практики могут быть инновационными
            PracticeType.MANAGEMENT.value: 1.0     # Управленческие практики реже инновационны
        }
        
        final_score = base_score * type_multipliers[practice_type.value]
        return {
            "score": round(min(final_score, 10.0), 2),
            "details": {
                "base_score": base_score, 
                "multiplier": type_multipliers[practice_type.value],
                "is_concept": is_concept
            }
        }
    
    def _get_base_innovation_score(self, data: Dict[str, Any]) -> float:
        """Базовая оценка инновационности"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        text = text.lower()
        
        # Добавляем больше специфичных технологических индикаторов
        tech_indicators = [
            ("artificial intelligence", 3.5),
            ("machine learning", 3.5),
            ("deep learning", 3.5),
            ("neural network", 3.0),
            ("natural language processing", 3.0),
            ("computer vision", 3.0),
            ("blockchain", 3.0),
            ("quantum computing", 3.0),
            ("robotics", 2.5),
            ("automation", 2.5),
            ("cloud native", 2.5),
            ("microservices", 2.0),
            ("containerization", 2.0),
            ("devops", 2.0),
            ("big data", 2.0)
        ]
        
        # Расширяем методологические инновации
        method_indicators = [
            ("novel methodology", 3.5),
            ("innovative framework", 3.0),
            ("new paradigm", 3.0),
            ("revolutionary approach", 3.0),
            ("unique solution", 2.5),
            ("advanced technique", 2.5),
            ("improved method", 2.0),
            ("enhanced workflow", 2.0)
        ]
        
        # Добавляем индикаторы для организационных инноваций
        org_indicators = [
            ("transformative change", 3.0),
            ("cultural revolution", 3.0),
            ("organizational innovation", 2.5),
            ("new management model", 2.5),
            ("innovative culture", 2.5),
            ("agile transformation", 2.0),
            ("digital transformation", 2.0)
        ]
        
        # Усиливаем общие индикаторы новизны
        general_indicators = [
            ("world first", 4.0),
            ("breakthrough innovation", 3.5),
            ("revolutionary", 3.0),
            ("pioneering", 3.0),
            ("cutting edge", 2.5),
            ("state of the art", 2.5),
            ("next generation", 2.5),
            ("innovative", 2.0),
            ("novel approach", 2.0)
        ]
        
        all_indicators = tech_indicators + method_indicators + org_indicators + general_indicators
        
        for term, points in all_indicators:
            if term in text:
                score += points
        
        # Увеличиваем бонусы
        if re.search(r'patent pending|patent application|granted patent', text):
            score += 4.0
        
        if re.search(r'doi:', text):
            score += 4.0
        
        if re.search(r'research paper|scientific publication|conference proceeding', text):
            score += 3.0
        
        if re.search(r'\d+%|\d+x|increased by \d+|reduced by \d+', text):
            score += 2.5
        
        if re.search(r'outperforms|better than|faster than|more efficient than', text):
            score += 2.0
        
        if re.search(r'award|recognition|prize', text):
            score += 2.0
        
        return self._normalize_score(score)
    
    def _generate_explanation(self, scores: Dict[str, float]) -> str:
        """Генерирует текстовое объяснение оценок"""
        explanations = []
        
        if scores["conceptual_innovation"] >= 8:
            explanations.append("Высокая степень концептуальной новизны")
        elif scores["conceptual_innovation"] >= 5:
            explanations.append("Присутствуют инновационные элементы в концепции")
        else:
            explanations.append("Требуется усилить концептуальную составляющую")
            
        if scores["methodological_innovation"] >= 8:
            explanations.append("Использует передовые методы")
        elif scores["methodological_innovation"] >= 5:
            explanations.append("Умеренная методологическая сложность")
        else:
            explanations.append("Можно усилить методологическую составляющую")
            
        if scores["technical_innovation"] >= 8:
            explanations.append("Большой технологический прогресс")
        else:
            explanations.append("Требуется лучше описать технологический прогресс")
            
        return ". ".join(explanations) 