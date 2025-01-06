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
        
    def analyze_sync(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "fullness": self._analyze_fullness(practice_data),
            "structure": self._analyze_structure(practice_data),
            "examples": self._analyze_examples(practice_data),
            "limitations": self._analyze_limitations(practice_data)
        }
        
        # Добавляем научный бонус
        scientific_bonus = self._calculate_scientific_bonus(practice_data)
        
        weights = {
            "fullness": 0.35,
            "structure": 0.35,
            "examples": 0.15,
            "limitations": 0.15
        }
        
        final_score = sum(scores[k] * weights[k] for k in scores) + scientific_bonus
        return {
            "score": round(min(final_score, 10.0), 2),
            "details": scores,
            "scientific_bonus": scientific_bonus,
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
                
        # Научные индикаторы в описании
        scientific_indicators = [
            "methodology", "statistical", "empirical",
            "hypothesis", "analysis", "validation",
            "experiment", "research", "study"
        ]
        
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        scientific_score = sum(2.0 for ind in scientific_indicators if ind in text.lower())
        score += min(scientific_score, 5.0)
        
        return self._normalize_score(score, 10.0)
    
    def _analyze_structure(self, data: Dict[str, Any]) -> float:
        """Анализ структурированности"""
        score = 0.0
        
        # Проверяем наличие всех ключевых секций
        required_sections = ["problem", "solution", "implementation_steps", 
                            "benefits", "limitations"]
        for section in required_sections:
            if data.get(section):
                score += 1.0
        
        # Анализируем детальность шагов реализации
        if isinstance(data.get("implementation_steps"), list):
            steps = data["implementation_steps"]
            if len(steps) >= 5:  # Бонус за подробное описание
                score += 2.0
            elif len(steps) >= 3:
                score += 1.0
                
            # Проверяем качество описания шагов
            detailed_steps = sum(1 for step in steps 
                               if len(str(step.get("description", ""))) > 100)
            score += min(detailed_steps * 0.5, 2.0)
        
        # Проверяем научную структуру
        scientific_elements = [
            "hypothesis", "methodology", "data collection",
            "analysis", "validation", "results"
        ]
        text = f"{data.get('solution', '')} {' '.join(str(step.get('description', '')) for step in data.get('implementation_steps', []))}"
        text = text.lower()
        
        scientific_score = sum(1 for element in scientific_elements if element in text)
        score += min(scientific_score * 0.5, 3.0)
        
        return self._normalize_score(score)
    
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
    
    def _calculate_scientific_bonus(self, data: Dict[str, Any]) -> float:
        """Бонус за научный подход"""
        score = 0.0
        text = f"{data.get('solution', '')} {' '.join(str(step.get('description', '')) for step in data.get('implementation_steps', []))}"
        text = text.lower()
        
        scientific_indicators = [
            (r'doi:\s*10\.\d+/[\w\.-]+', 3.0),         # DOI
            (r'p\s*[<>=]\s*0\.\d+', 2.0),              # p-value
            (r'\d+%\s*confidence', 2.0),                # confidence interval
            ("statistical significance", 2.0),
            ("hypothesis testing", 2.0),
            ("empirical validation", 2.0),
            ("peer-reviewed", 2.0),
            ("reproducible results", 1.5),
            ("systematic approach", 1.5),
            ("quantitative analysis", 1.5)
        ]
        
        for pattern, points in scientific_indicators:
            if isinstance(pattern, str):
                if pattern in text:
                    score += points
            else:
                if re.search(pattern, text):
                    score += points
                
        return min(score, 3.0)  # Максимальный бонус 3.0 