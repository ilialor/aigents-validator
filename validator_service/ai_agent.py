from typing import Dict, Any, Optional, List
import re
from collections import Counter

# Конфигурация для анализа
CONFIG = {
    "weights": {
        "Q": 0.25,  # Quality
        "R": 0.20,  # Reproducibility
        "U": 0.20,  # Utility
        "A": 0.20,  # Applicability
        "I": 0.15   # Innovation
    },
    "keywords": {
        "innovation": ['new', 'novel', 'innovative', 'unique', 'original'],
        "scalability": ['scale', 'adapt', 'flexible', 'modular'],
        "technology": ['ai', 'ml', 'blockchain', 'cloud', 'distributed', 'microservices'],
        "future": ['future', 'potential', 'scalable', 'extensible']
    },
    "scoring": {
        "min_text_length": 50,
        "good_text_length": 100,
        "max_examples": 2,
        "max_limitations": 2,
        "max_steps": 4
    }
}

class PracticeAnalyzer:
    def __init__(self, custom_config: Optional[Dict] = None):
        """
        Инициализация анализатора с возможностью переопределения конфигурации
        """
        self.config = custom_config or CONFIG
        
    def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        """Анализ практики по всем критериям"""
        if not self._validate_practice_data(practice_data):
            raise ValueError("Invalid practice data format")
            
        scores = {
            "Q": self._analyze_quality(practice_data),
            "R": self._analyze_reproducibility(practice_data),
            "U": self._analyze_utility(practice_data),
            "A": self._analyze_applicability(practice_data),
            "I": self._analyze_innovation(practice_data)
        }
        
        sota_score = self._calculate_sota_score(scores)
        scores["sota_score"] = round(sota_score, 2)
        
        return scores

    def _validate_practice_data(self, data: Dict[str, Any]) -> bool:
        """Проверка корректности входных данных"""
        required_fields = ['title', 'summary', 'problem', 'solution']
        return all(field in data and data[field] for field in required_fields)

    def _normalize_score(self, score: float, max_points: float) -> float:
        """Нормализация оценки к шкале 0-10"""
        if max_points <= 0:
            return 0.0
        return min((score / max_points) * 10, 10.0)

    def _analyze_text_quality(self, text: str) -> float:
        """Оценка качества текстового описания"""
        if not text:
            return 0.0
        length = len(str(text))
        if length > self.config["scoring"]["good_text_length"]:
            return 1.0
        elif length > self.config["scoring"]["min_text_length"]:
            return 0.7
        return 0.3

    def _count_keyword_matches(self, text: str, keyword_type: str) -> int:
        """Подсчет совпадений ключевых слов"""
        if not text:
            return 0
        text = text.lower()
        keywords = self.config["keywords"].get(keyword_type, [])
        return sum(1 for kw in keywords if kw in text)

    def _analyze_quality(self, data: Dict[str, Any]) -> float:
        """Детальный анализ качества"""
        score = 0.0
        max_points = 0.0
        
        # Анализ основных полей
        for field in ['title', 'summary', 'problem', 'solution']:
            if field in data:
                quality = self._analyze_text_quality(data[field])
                score += quality * 3
                max_points += 3

        # Анализ структуры
        if self._validate_field(data, 'implementation_steps', list):
            steps_quality = sum(self._analyze_text_quality(str(step)) 
                              for step in data['implementation_steps'])
            score += min(steps_quality, self.config["scoring"]["max_steps"])
            max_points += self.config["scoring"]["max_steps"]

        return self._normalize_score(score, max_points)

    def _analyze_reproducibility(self, data: Dict[str, Any]) -> float:
        """Детальный анализ воспроизводимости"""
        score = 0.0
        max_points = 0.0

        # Анализ шагов реализации
        if self._validate_field(data, 'implementation_steps', list):
            steps = data['implementation_steps']
            for step in steps:
                if isinstance(step, dict) and 'description' in step:
                    quality = self._analyze_text_quality(step['description'])
                    score += quality
                    max_points += 1

        # Анализ требований
        if self._validate_field(data, 'implementation_requirements', list):
            reqs_quality = sum(self._analyze_text_quality(str(req)) 
                             for req in data['implementation_requirements'])
            score += min(reqs_quality, 3)
            max_points += 3

        return self._normalize_score(score, max_points)

    def _analyze_utility(self, data: Dict[str, Any]) -> float:
        """Детальный анализ полезности"""
        score = 0.0
        max_points = 0.0

        # Анализ проблемы и решения
        if 'problem' in data and 'solution' in data:
            problem_quality = self._analyze_text_quality(data['problem'])
            solution_quality = self._analyze_text_quality(data['solution'])
            score += (problem_quality + solution_quality) * 2
            max_points += 4

        # Анализ выгод
        if self._validate_field(data, 'benefits', list):
            benefits_quality = sum(self._analyze_text_quality(str(benefit)) 
                                 for benefit in data['benefits'])
            score += min(benefits_quality, 4)
            max_points += 4

        return self._normalize_score(score, max_points)

    def _analyze_applicability(self, data: Dict[str, Any]) -> float:
        """Детальный анализ применимости"""
        score = 0.0
        max_points = 0.0

        # Анализ масштабируемости
        if 'implementation_requirements' in data:
            scalability_score = self._count_keyword_matches(
                str(data['implementation_requirements']), 
                'scalability'
            )
            score += min(scalability_score * 2, 4)
            max_points += 4

        # Анализ ограничений
        if self._validate_field(data, 'limitations', list):
            limitations_quality = sum(self._analyze_text_quality(str(limit)) 
                                    for limit in data['limitations'])
            score += min(limitations_quality, 3)
            max_points += 3

        return self._normalize_score(score, max_points)

    def _analyze_innovation(self, data: Dict[str, Any]) -> float:
        """Детальный анализ инновационности"""
        score = 0.0
        max_points = 0.0

        # Анализ новизны решения
        if 'solution' in data:
            innovation_score = self._count_keyword_matches(str(data['solution']), 'innovation')
            tech_score = self._count_keyword_matches(str(data['solution']), 'technology')
            
            score += min(innovation_score * 2, 4)  # До 4 баллов за инновационность
            score += min(tech_score * 1.5, 3)      # До 3 баллов за технологичность
            
            max_points += 7

        # Анализ потенциала развития
        if self._validate_field(data, 'benefits', list):
            future_score = sum(self._count_keyword_matches(str(benefit), 'future') 
                             for benefit in data['benefits'])
            score += min(future_score, 3)
            max_points += 3

        return self._normalize_score(score, max_points)

    def _calculate_sota_score(self, scores: Dict[str, float]) -> float:
        """Расчет итогового sota_score с учетом весов"""
        weights = self.config["weights"]
        return sum(scores[k] * weights[k] for k in scores if k != "sota_score")

    def _validate_field(self, data: Dict[str, Any], field: str, expected_type: type) -> bool:
        """Проверка наличия и типа поля"""
        return field in data and isinstance(data[field], expected_type)

# Пример использования
def analyze_practice(practice_data: Dict[str, Any], custom_config: Optional[Dict] = None) -> Dict[str, float]:
    """
    Анализирует практику и возвращает оценки по критериям Q.R.U.A.I.
    
    Args:
        practice_data: Данные практики для анализа
        custom_config: Пользовательская конфигурация (опционально)
        
    Returns:
        Dict с оценками по критериям и общим sota_score
    """
    analyzer = PracticeAnalyzer(custom_config)
    return analyzer.analyze(practice_data) 