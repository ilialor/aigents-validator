from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class CriterionThreshold:
    min_value: float = 6.0
    weight: float = 1.0
    required: bool = True

@dataclass
class QualityMetric:
    score: float
    details: Dict[str, float]
    explanation: str
    is_valid: bool = True

class QualityWheel:
    """Штурвал качества для управления критериями оценки практик"""
    
    def __init__(self):
        # Настройки критериев по умолчанию
        self.thresholds = {
            "Q": {  # Quality
                "fullness": CriterionThreshold(6.0, 0.4, True),
                "structure": CriterionThreshold(6.0, 0.3, True),
                "examples": CriterionThreshold(6.0, 0.15, False),
                "limitations": CriterionThreshold(6.0, 0.15, False)
            },
            "R": {  # Reproducibility
                "steps_clarity": CriterionThreshold(6.0, 0.4, True),
                "requirements": CriterionThreshold(6.0, 0.3, True),
                "resources": CriterionThreshold(6.0, 0.3, True)
            },
            "U": {  # Utility
                "problem_clarity": CriterionThreshold(6.0, 0.35, True),
                "benefits": CriterionThreshold(6.0, 0.35, True),
                "efficiency": CriterionThreshold(6.0, 0.30, False)
            },
            "A": {  # Applicability
                "universality": CriterionThreshold(6.0, 0.35, True),
                "scalability": CriterionThreshold(6.0, 0.35, True),
                "constraints": CriterionThreshold(6.0, 0.30, False)
            },
            "I": {  # Innovation
                "novelty": CriterionThreshold(6.0, 0.4, False),
                "tech_complexity": CriterionThreshold(6.0, 0.3, False),
                "potential": CriterionThreshold(6.0, 0.3, True)
            },
            "Rel": {  # Reliability
                "empirical_validation": CriterionThreshold(6.0, 0.35, True),
                "methodology": CriterionThreshold(6.0, 0.25, True),
                "adaptability": CriterionThreshold(6.0, 0.20, False),
                "external_validation": CriterionThreshold(6.0, 0.20, False)
            }
        }
        
    def adjust_threshold(self, criterion: str, metric: str, 
                        min_value: Optional[float] = None,
                        weight: Optional[float] = None,
                        required: Optional[bool] = None) -> None:
        """Настройка порогов для критерия"""
        if criterion in self.thresholds and metric in self.thresholds[criterion]:
            threshold = self.thresholds[criterion][metric]
            if min_value is not None:
                threshold.min_value = min_value
            if weight is not None:
                threshold.weight = weight
            if required is not None:
                threshold.required = required

    def evaluate_practice(self, scores: Dict[str, Dict]) -> Dict[str, Any]:
        """Оценка практики с учетом настроенных порогов"""
        result = {
            "valid_scores": {},
            "invalid_scores": {},
            "missing_required": [],
            "final_score": None,
            "reliability_score": None,
            "recommendations": []
        }
        
        for criterion, metrics in scores.items():
            if criterion not in self.thresholds:
                continue
                
            criterion_result = self._evaluate_criterion(criterion, metrics)
            
            # Конвертируем QualityMetric в словарь
            criterion_dict = {
                "score": criterion_result.score,
                "details": criterion_result.details,
                "explanation": criterion_result.explanation,
                "is_valid": criterion_result.is_valid
            }
            
            if criterion_result.is_valid:
                result["valid_scores"][criterion] = criterion_dict
            else:
                result["invalid_scores"][criterion] = criterion_dict
                if any(self.thresholds[criterion][m].required for m in metrics["details"]):
                    result["missing_required"].append(criterion)
                    
            # Формируем рекомендации по улучшению
            if criterion_result.score < 6.0:
                result["recommendations"].append(
                    f"Criterion {criterion} needs improvement: {criterion_result.explanation}"
                )
        
        # Вычисляем итоговую оценку только если все обязательные критерии валидны
        if not result["missing_required"]:
            valid_scores = [s["score"] for s in result["valid_scores"].values()]
            if valid_scores:
                result["final_score"] = sum(valid_scores) / len(valid_scores)
                
        return result

    def _evaluate_criterion(self, criterion: str, metrics: Dict) -> QualityMetric:
        """Оценка отдельного критерия"""
        details = metrics["details"]
        valid_metrics = {}
        invalid_metrics = {}
        
        for metric, score in details.items():
            if metric not in self.thresholds[criterion]:
                continue
                
            threshold = self.thresholds[criterion][metric]
            if score >= threshold.min_value or not threshold.required:
                valid_metrics[metric] = score
            else:
                invalid_metrics[metric] = score
        
        # Проверяем валидность критерия
        is_valid = True
        if invalid_metrics:
            required_invalid = any(
                self.thresholds[criterion][m].required 
                for m in invalid_metrics
            )
            is_valid = not required_invalid
        
        # Вычисляем взвешенную оценку для валидных метрик
        if valid_metrics:
            weighted_score = sum(
                score * self.thresholds[criterion][metric].weight
                for metric, score in valid_metrics.items()
            )
        else:
            weighted_score = 0.0
            
        return QualityMetric(
            score=weighted_score,
            details={**valid_metrics, **invalid_metrics},
            explanation=metrics.get("explanation", ""),
            is_valid=is_valid
        ) 