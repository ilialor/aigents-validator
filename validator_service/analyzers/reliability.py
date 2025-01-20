from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer
from .practice_classifier import PracticeClassifier, PracticeType

class ReliabilityAnalyzer(BaseAnalyzer):
    """Анализатор надежности (Reliability) с усиленным анализом научного подхода"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_md")
        self.classifier = PracticeClassifier()
        
    def analyze_sync(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "empirical_validation": self._analyze_empirical_validation(practice_data),
            "methodology": self._analyze_methodology(practice_data),
            "adaptability": self._analyze_adaptability(practice_data),
            "external_validation": self._analyze_external_validation(practice_data),
            "validation_quality": self._analyze_validation_quality(practice_data)
        }
        
        # Увеличиваем веса для ключевых показателей
        weights = {
            "empirical_validation": 0.35,  # Было 0.3
            "methodology": 0.3,            # Было 0.25
            "adaptability": 0.15,
            "external_validation": 0.1,    # Было 0.15
            "validation_quality": 0.1      # Было 0.15
        }
        
        final_score = sum(scores[k] * weights[k] for k in scores)
        
        # Увеличиваем множители для научных практик
        practice_type, is_concept = self.classifier.classify(practice_data)
        type_multipliers = {
            PracticeType.SCIENTIFIC.value: 1.5,      # Было 1.3
            PracticeType.ENGINEERING.value: 1.3,     # Было 1.2
            PracticeType.PROCESS.value: 1.1,
            PracticeType.MANAGEMENT.value: 1.0
        }
        
        final_score *= type_multipliers[practice_type.value]
        
        # Увеличиваем минимальный порог для научных практик
        if self._is_scientific_practice(practice_data):
            final_score = max(final_score, 7.0)  # Было 6.0
            
            # Дополнительные бонусы для научных практик
            text = practice_data.get('solution', '').lower()
            if re.search(r'statistical (analysis|significance|test)', text):
                final_score += 1.5
                
            if re.search(r'peer[- ]review|journal|conference', text):
                final_score += 1.0
                
            if re.search(r'empirical|experimental', text):
                final_score += 1.0
        
        # Общие бонусы
        text = practice_data.get('solution', '').lower()
        if re.search(r'documentation|guide|manual', text):
            final_score += 0.5  # Уменьшили с 1.0
        
        if re.search(r'example|case study|proof', text):
            final_score += 0.5  # Уменьшили с 1.0
        
        return {
            "score": round(min(final_score, 10.0), 2),
            "details": {
                **scores,
                "type_multiplier": type_multipliers[practice_type.value],
                "is_concept": is_concept
            }
        }
    
    def _analyze_empirical_validation(self, data: Dict[str, Any]) -> float:
        """Анализ эмпирической валидации с учетом научного подхода"""
        score = 0.0
        
        research_indicators = {
            "critical": [
                "peer-reviewed", "replicated", "statistical significance",
                "confidence interval", "p-value", "hypothesis testing",
                "DOI:", "arxiv.org", "empirical evidence", "experimental validation"
            ],
            "strong": [
                "dataset", "protocol", "randomized", "double-blind",
                "control group", "statistical analysis", "github.com",
                "quantitative results", "measured outcomes", "verified results"
            ],
            "medium": [
                "empirical study", "experimental results", "quantitative analysis",
                "methodology", "validation", "systematic approach",
                "documented process", "reproducible steps"
            ]
        }
        
        text = f"{data.get('solution', '')} {' '.join(str(step.get('description', '')) for step in data.get('implementation_steps', []))}"
        text = text.lower()
        
        # Увеличиваем бонусы за критические индикаторы
        critical_count = sum(1 for ind in research_indicators["critical"] if ind in text)
        if critical_count >= 2:
            score += 6.0  # Было 5.0
        
        strong_count = sum(1 for ind in research_indicators["strong"] if ind in text)
        score += min(strong_count * 2.0, 4.0)  # Было 1.5, 3.0
        
        medium_count = sum(1 for ind in research_indicators["medium"] if ind in text)
        score += min(medium_count * 1.0, 3.0)  # Было 0.5, 2.0
        
        return self._normalize_score(score)
    
    def _analyze_methodology(self, data: Dict[str, Any]) -> float:
        """Анализ методологической прочности с учетом воспроизводимости"""
        score = 0.0
        
        # Индикаторы воспроизводимости
        reproducibility_indicators = {
            "strong": [
                "reproducible", "replicable", "repeatable",
                "open source", "public dataset", "documented protocol",
                "step-by-step guide", "detailed methodology"
            ],
            "medium": [
                "implementation guide", "technical documentation",
                "code examples", "test cases", "validation steps"
            ]
        }
        
        text = f"{data.get('solution', '')} {data.get('implementation_steps', '')}"
        text = text.lower()
        
        # Проверяем индикаторы воспроизводимости
        for word in reproducibility_indicators["strong"]:
            if word in text:
                score += 2.5
        for word in reproducibility_indicators["medium"]:
            if word in text:
                score += 1.5
                
        # Проверяем структуру и полноту описания
        if isinstance(data.get("implementation_steps"), list):
            steps = data["implementation_steps"]
            if len(steps) >= 5:
                score += 2.0
                
        # Проверяем наличие требований и ограничений
        if isinstance(data.get("implementation_requirements"), list):
            score += min(len(data["implementation_requirements"]) * 1.0, 3.0)
            
        return self._normalize_score(score, 10.0)
    
    def _analyze_adaptability(self, data: Dict[str, Any]) -> float:
        """Анализ адаптивности"""
        score = 0.0
        
        # Расширяем индикаторы адаптивности
        adapt_indicators = {
            "high": [
                "adapt", "flexible", "customize", "configure",
                "scalable", "modular", "extensible"  # Добавляем индикаторы масштабируемости
            ],
            "medium": [
                "adjust", "modify", "tune", "parameter",
                "update", "maintain", "improve"  # Добавляем индикаторы поддержки
            ],
            "context": [
                "environment", "condition", "scenario", "case",
                "organization", "domain", "context", "situation"  # Расширяем контекстные индикаторы
            ]
        }
        
        # Анализируем больше полей
        text = f"{data.get('solution', '')} {data.get('implementation_steps', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        for word in adapt_indicators["high"]:
            if word in text:
                score += 3.0  # Было 2.5
        for word in adapt_indicators["medium"]:
            if word in text:
                score += 2.0  # Было 1.5
        for word in adapt_indicators["context"]:
            if word in text:
                score += 1.5  # Было 1.0
                
        # Добавляем бонус за наличие вариаций применения
        if data.get("domain") and data.get("sub_domains"):
            score += 2.0
            
        return self._normalize_score(score, 10.0)
    
    def _analyze_external_validation(self, data: Dict[str, Any]) -> float:
        """Анализ внешней валидации с учетом научных публикаций"""
        score = 0.0
        
        validation_indicators = {
            "scientific": [
                "peer review", "journal publication", "conference paper",
                "citations", "nature", "science", "arxiv", "research paper",
                "scientific validation", "academic study"
            ],
            "industry": [
                "certified", "approved", "standardized", "recognized",
                "established", "proven", "industry-standard", "professional"
            ],
            "community": [
                "widely used", "community tested", "field-tested",
                "production deployment", "real-world application"
            ]
        }
        
        text = f"{data.get('solution', '')} {data.get('benefits', '')} {data.get('summary', '')}"
        text = text.lower()
        
        # Увеличиваем вес научных индикаторов
        for word in validation_indicators["scientific"]:
            if word in text:
                score += 3.0  # Было 2.5
        for word in validation_indicators["industry"]:
            if word in text:
                score += 2.0
        for word in validation_indicators["community"]:
            if word in text:
                score += 1.5
                
        return self._normalize_score(score, 10.0)

    def _calculate_correction_factors(self, data: Dict[str, Any]) -> float:
        """Расчет корректирующих факторов с учетом научной валидации"""
        correction = 0.0
        
        text = f"{data.get('solution', '')} {data.get('limitations', '')}"
        text = text.lower()
        
        # Проверяем сочетание новизны и научной валидации
        if any(word in text for word in ["new", "novel", "recent"]):
            if any(word in text for word in ["peer-reviewed", "replicated", "published", "validated"]):
                # Если есть научная валидация, не штрафуем
                correction += 0.0
            else:
                correction -= 0.5
                
        # Ограниченность данных
        if "limited data" in text:
            if "statistically significant" in text or "sufficient sample" in text:
                correction -= 0.2  # Уменьшаем штраф при наличии статистической значимости
            else:
                correction -= 0.5
                
        # Противоречивые результаты
        if any(word in text for word in ["contradictory", "inconsistent", "varies"]):
            if "explained variation" in text or "understood factors" in text:
                correction -= 0.5  # Уменьшаем штраф если вариации объяснены
            else:
                correction -= 1.0
                
        return correction
    
    def _generate_explanation(self, scores: Dict[str, float]) -> str:
        """Генерирует текстовое объяснение оценок с учетом научного подхода"""
        explanations = []
        
        if scores["empirical_validation"] >= 8:
            explanations.append("Сильная эмпирическая база с научной валидацией")
        elif scores["empirical_validation"] >= 5:
            explanations.append("Достаточная эмпирическая валидация")
        else:
            explanations.append("Требуется больше эмпирических данных и научной валидации")
            
        if scores["methodology"] >= 8:
            explanations.append("Методология хорошо проработана и воспроизводима")
        elif scores["methodology"] >= 5:
            explanations.append("Методология адекватна")
        else:
            explanations.append("Требуется улучшить методологию и воспроизводимость")
            
        if scores["external_validation"] >= 8:
            explanations.append("Сильная внешняя валидация через научные публикации")
        elif scores["external_validation"] >= 5:
            explanations.append("Есть внешняя валидация")
        else:
            explanations.append("Требуется усилить внешнюю валидацию")
            
        return ". ".join(explanations) 

    def _calculate_scientific_bonus(self, data: Dict[str, Any]) -> float:
        """Рассчитывает дополнительный бонус для научных практик"""
        bonus = 0.0
        text = f"{data.get('solution', '')} {' '.join(str(step.get('description', '')) for step in data.get('implementation_steps', []))}"
        text = text.lower()
        
        # Проверяем наличие строгих научных элементов
        scientific_elements = [
            (r'p\s*[<>=]\s*0\.\d+', 2.0),  # p-value
            (r'\d+%\s*confidence', 1.5),    # confidence interval
            (r'doi:.*?\s', 2.0),           # DOI reference
            (r'arxiv\.org/abs/\d{4}\.\d{4,5}', 1.5),  # arXiv reference
            (r'github\.com/[\w-]+/[\w-]+', 1.0),      # GitHub repository
            (r'statistical\s+significance', 1.5),
            (r'hypothesis\s+test', 1.5),
            (r'control\s+group', 1.0),
            (r'double-blind', 1.0),
            (r'peer-review', 2.0)
        ]
        
        for pattern, score in scientific_elements:
            if re.search(pattern, text):
                bonus += score
                
        # Проверяем наличие статистических метрик
        metrics = [
            'standard deviation',
            'variance',
            'correlation',
            'regression',
            'effect size',
            'sample size',
            'power analysis'
        ]
        
        metrics_found = sum(1 for m in metrics if m in text)
        bonus += metrics_found * 0.5
        
        return min(bonus, 4.0)  # Максимальный бонус 4.0 

    def _is_scientific_practice(self, data: Dict[str, Any]) -> bool:
        """Проверяет, является ли практика научной"""
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        text = text.lower()
        
        scientific_indicators = [
            r'doi:', r'p\s*[<>=]\s*0\.\d+', 
            "statistical significance", "empirical evidence",
            "peer-reviewed", "scientific method"
        ]
        
        return any(ind in text if isinstance(ind, str) else re.search(ind, text) 
                  for ind in scientific_indicators) 

    def _analyze_validation_quality(self, data: Dict[str, Any]) -> float:
        """Оценка качества валидации"""
        score = 5.0  # Начинаем с базовой оценки
        text = f"{data.get('solution', '')} {data.get('validation', '')} {data.get('summary', '')}"
        text = text.lower()
        
        # Проверяем методы валидации
        validation_indicators = [
            ("empirical validation", 2.0),
            ("statistical analysis", 2.0),
            ("experimental results", 2.0),
            ("case study", 1.5),
            ("user testing", 1.5),
            ("field testing", 1.5),
            ("pilot project", 1.5),
            ("proof of concept", 1.0),
            ("benchmark", 1.0),
            ("metrics", 1.0)
        ]
        
        # Проверяем количественные результаты
        quantitative_indicators = [
            (r'\d+%', 2.0),
            (r'\d+x', 2.0),
            (r'increased by \d+', 1.5),
            (r'reduced by \d+', 1.5),
            (r'measured improvement', 1.0),
            (r'performance gain', 1.0)
        ]
        
        # Проверяем качество документации
        documentation_indicators = [
            ("detailed documentation", 1.5),
            ("step by step guide", 1.5),
            ("implementation manual", 1.0),
            ("best practices", 1.0),
            ("known limitations", 1.0),
            ("troubleshooting", 1.0)
        ]
        
        # Подсчет баллов
        for term, points in validation_indicators:
            if term in text:
                score += points
            
        for pattern, points in quantitative_indicators:
            if re.search(pattern, text):
                score += points
            
        for term, points in documentation_indicators:
            if term in text:
                score += points
        
        # Дополнительные бонусы
        if re.search(r'verified by|validated by|tested by', text):
            score += 2.0
        
        if re.search(r'long[- ]term|over \d+ years|\d+ months', text):
            score += 1.5
        
        return self._normalize_score(score) 