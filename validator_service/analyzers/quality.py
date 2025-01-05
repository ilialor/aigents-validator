from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer

class QualityAnalyzer(BaseAnalyzer):
    """Анализатор качества (Q)"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        # Загружаем модель spaCy для анализа структуры текста
        self.nlp = spacy.load("en_core_web_md")
        
    def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "fullness": self._analyze_fullness(practice_data),
            "structure": self._analyze_structure(practice_data),
            "examples": self._analyze_examples(practice_data),
            "limitations": self._analyze_limitations(practice_data)
        }
        
        # Вычисляем итоговую оценку с весами
        weights = {
            "fullness": 0.4,
            "structure": 0.3,
            "examples": 0.15,
            "limitations": 0.15
        }
        
        final_score = sum(scores[k] * weights[k] for k in scores)
        
        return {
            "score": round(final_score, 2),
            "details": scores,
            "explanation": self._generate_explanation(scores)
        }
    
    def _analyze_fullness(self, data: Dict[str, Any]) -> float:
        """Анализ полноты описания"""
        required_fields = ["title", "summary", "problem", "solution"]
        score = 0.0
        
        for field in required_fields:
            if field in data and data[field]:
                text = str(data[field])
                # Анализируем сложность и качество текста
                blob = TextBlob(text)
                
                # Учитываем длину
                if len(text) >= 200:
                    score += 2.5
                elif len(text) >= 50:
                    score += 1.5
                
                # Учитываем сложность предложений
                score += min(blob.sentiment.subjectivity * 2, 1.0)
                
        return self._normalize_score(score, 10.0)
    
    def _analyze_structure(self, data: Dict[str, Any]) -> float:
        """Анализ структурированности"""
        score = 0.0
        
        if "implementation_steps" in data:
            steps = data["implementation_steps"]
            if isinstance(steps, list):
                # Проверяем логическую последовательность шагов
                score += min(len(steps) * 2, 6)
                
                # Анализируем связность шагов
                if len(steps) > 1:
                    prev_doc = None
                    for step in steps:
                        if isinstance(step, dict) and "description" in step:
                            doc = self.nlp(step["description"])
                            if prev_doc:
                                # Проверяем связность с предыдущим шагом
                                similarity = doc.similarity(prev_doc)
                                score += similarity
                            prev_doc = doc
                
        return self._normalize_score(score, 10.0)
    
    def _analyze_examples(self, data: Dict[str, Any]) -> float:
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        
        # Добавляем поиск примеров в тексте через регулярные выражения
        example_patterns = [
            r"example[s]?:?\s*\d+\..*?(?=\n\n|\Z)",
            r"for example:?.*?(?=\n\n|\Z)",
            r"such as:?.*?(?=\n\n|\Z)",
            r"e\.g\..*?(?=\n\n|\Z)",
            r"\d+\.\s+[A-Z].*?:.*?(?=\n|$)" # Для нумерованных примеров с заглавной буквы
        ]
        
        for pattern in example_patterns:
            examples = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            score += len(examples) * 2.5
            
        return self._normalize_score(score, 10.0)
        
    def _analyze_limitations(self, data: Dict[str, Any]) -> float:
        """Анализ документации ограничений"""
        score = 0.0
        
        if "limitations" in data and isinstance(data["limitations"], list):
            limitations = data["limitations"]
            
            for limit in limitations:
                text = str(limit)
                if self._validate_text(text, 30):
                    score += 2.5
                    # Анализируем конкретность ограничения
                    doc = self.nlp(text)
                    if any(token.pos_ in ["NUM", "PROPN"] for token in doc):
                        score += 1.0
                        
        return self._normalize_score(score, 10.0)
    
    def _generate_explanation(self, scores: Dict[str, float]) -> str:
        """Генерирует текстовое объяснение оценок"""
        explanations = []
        
        if scores["fullness"] >= 8:
            explanations.append("Очень подробное описание")
        elif scores["fullness"] >= 5:
            explanations.append("Достаточное описание")
        else:
            explanations.append("Требуется более детальное описание")
            
        if scores["structure"] >= 8:
            explanations.append("Отличная структура")
        elif scores["structure"] >= 5:
            explanations.append("Приемлемая структура")
        else:
            explanations.append("Структура требует улучшения")
            
        return ". ".join(explanations) 