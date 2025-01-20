from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer
import logging

logger = logging.getLogger(__name__)

class QualityAnalyzer(BaseAnalyzer):
    """Анализатор качества (Q)"""
    
    def __init__(self, config: Dict = None):
        logger.info("Initializing QualityAnalyzer")
        super().__init__(config)
        # Загружаем модель spaCy для анализа структуры текста
        self.nlp = spacy.load("en_core_web_md")
        
    def analyze_sync(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        logger.info("Starting quality analysis")
        
        scores = {
            "fullness": self._analyze_fullness(practice_data),
            "structure": self._analyze_structure(practice_data),
            "examples": self._analyze_examples(practice_data),
            "limitations": self._analyze_limitations(practice_data)
        }
        
        logger.debug(f"Individual scores: {scores}")
        
        # Добавляем научный бонус
        scientific_bonus = self._calculate_scientific_bonus(practice_data)
        logger.debug(f"Scientific bonus: {scientific_bonus}")
        
        weights = {
            "fullness": 0.35,
            "structure": 0.35,
            "examples": 0.15,
            "limitations": 0.15
        }
        
        final_score = sum(scores[k] * weights[k] for k in scores) + scientific_bonus
        logger.info(f"Final quality score: {final_score}")
        
        result = {
            "score": round(min(final_score, 10.0), 2),
            "details": scores,
            "scientific_bonus": scientific_bonus,
            "explanation": self._generate_explanation(scores)
        }
        logger.debug(f"Analysis result: {result}")
        return result
    
    def _analyze_fullness(self, data: Dict[str, Any]) -> float:
        """Анализ полноты описания"""
        logger.debug("Analyzing fullness")
        required_fields = ["title", "summary", "problem", "solution"]
        score = 0.0
        
        for field in required_fields:
            if field in data and data[field]:
                text = str(data[field])
                logger.debug(f"Analyzing field '{field}' (length: {len(text)})")
                
                # Анализируем сложность и качество текста
                blob = TextBlob(text)
                
                # Учитываем длину
                if len(text) >= 200:
                    score += 2.5
                    logger.debug(f"Field '{field}' got full length score")
                elif len(text) >= 50:
                    score += 1.5
                    logger.debug(f"Field '{field}' got partial length score")
                
                # Учитываем сложность предложений
                subjectivity_score = min(blob.sentiment.subjectivity * 2, 1.0)
                score += subjectivity_score
                logger.debug(f"Subjectivity score for '{field}': {subjectivity_score}")
                
        # Научные индикаторы в описании
        scientific_indicators = [
            "methodology", "statistical", "empirical",
            "hypothesis", "analysis", "validation",
            "experiment", "research", "study"
        ]
        
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        scientific_score = sum(2.0 for ind in scientific_indicators if ind in text.lower())
        logger.debug(f"Scientific indicators found: {scientific_score/2.0}")
        score += min(scientific_score, 5.0)
        
        final_score = self._normalize_score(score, 10.0)
        logger.info(f"Fullness analysis score: {final_score}")
        return final_score
    
    def _analyze_structure(self, data: Dict[str, Any]) -> float:
        """Анализ структурированности"""
        logger.debug("Analyzing structure")
        score = 0.0
        
        # Проверяем наличие всех ключевых секций
        required_sections = ["problem", "solution", "implementation_steps", 
                            "benefits", "limitations"]
        present_sections = [section for section in required_sections if data.get(section)]
        logger.debug(f"Present sections: {present_sections}")
        score += len(present_sections)
        
        # Анализируем детальность шагов реализации
        if isinstance(data.get("implementation_steps"), list):
            steps = data["implementation_steps"]
            logger.debug(f"Found {len(steps)} implementation steps")
            
            if len(steps) >= 5:
                score += 2.0
                logger.debug("Added bonus for 5+ steps")
            elif len(steps) >= 3:
                score += 1.0
                logger.debug("Added bonus for 3+ steps")
                
            # Проверяем качество описания шагов
            detailed_steps = sum(1 for step in steps 
                               if len(str(step.get("description", ""))) > 100)
            logger.debug(f"Detailed steps count: {detailed_steps}")
            score += min(detailed_steps * 0.5, 2.0)
        
        # Проверяем научную структуру
        scientific_elements = [
            "hypothesis", "methodology", "data collection",
            "analysis", "validation", "results"
        ]
        text = f"{data.get('solution', '')} {' '.join(str(step.get('description', '')) for step in data.get('implementation_steps', []))}"
        text = text.lower()
        
        scientific_score = sum(1 for element in scientific_elements if element in text)
        logger.debug(f"Scientific elements found: {scientific_score}")
        score += min(scientific_score * 0.5, 3.0)
        
        final_score = self._normalize_score(score)
        logger.info(f"Structure analysis score: {final_score}")
        return final_score
    
    def _analyze_examples(self, data: Dict[str, Any]) -> float:
        """Анализ примеров"""
        logger.debug("Analyzing examples")
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        
        example_patterns = [
            r"example[s]?:?\s*\d+\..*?(?=\n\n|\Z)",
            r"for example:?.*?(?=\n\n|\Z)",
            r"such as:?.*?(?=\n\n|\Z)",
            r"e\.g\..*?(?=\n\n|\Z)",
            r"\d+\.\s+[A-Z].*?:.*?(?=\n|$)"
        ]
        
        total_examples = 0
        for pattern in example_patterns:
            examples = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            total_examples += len(examples)
            logger.debug(f"Found {len(examples)} examples with pattern '{pattern}'")
            score += len(examples) * 2.5
            
        final_score = self._normalize_score(score, 10.0)
        logger.info(f"Examples analysis score: {final_score} (total examples: {total_examples})")
        return final_score
        
    def _analyze_limitations(self, data: Dict[str, Any]) -> float:
        """Анализ документации ограничений"""
        logger.debug("Analyzing limitations")
        score = 0.0
        
        if "limitations" in data and isinstance(data["limitations"], list):
            limitations = data["limitations"]
            logger.debug(f"Found {len(limitations)} limitations")
            
            for i, limit in enumerate(limitations, 1):
                text = str(limit)
                if self._validate_text(text, 30):
                    score += 2.5
                    logger.debug(f"Limitation {i} passed length validation")
                    
                    # Анализируем конкретность ограничения
                    doc = self.nlp(text)
                    specific_tokens = [token for token in doc if token.pos_ in ["NUM", "PROPN"]]
                    if specific_tokens:
                        score += 1.0
                        logger.debug(f"Limitation {i} contains specific details: {[token.text for token in specific_tokens]}")
                        
        final_score = self._normalize_score(score, 10.0)
        logger.info(f"Limitations analysis score: {final_score}")
        return final_score
    
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
            
        explanation = ". ".join(explanations)
        logger.debug(f"Generated explanation: {explanation}")
        return explanation
    
    def _calculate_scientific_bonus(self, data: Dict[str, Any]) -> float:
        """Бонус за научный подход"""
        logger.debug("Calculating scientific bonus")
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
                    logger.debug(f"Found scientific indicator '{pattern}': +{points} points")
            else:
                if re.search(pattern, text):
                    score += points
                    logger.debug(f"Found scientific pattern '{pattern}': +{points} points")
                
        final_score = min(score, 3.0)
        logger.info(f"Scientific bonus score: {final_score}")
        return final_score 