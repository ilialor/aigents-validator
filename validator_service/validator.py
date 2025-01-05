from typing import Dict, Any
from validator_service.analyzers import (
    QualityAnalyzer, 
    ReproducibilityAnalyzer, 
    UtilityAnalyzer, 
    ApplicabilityAnalyzer, 
    InnovationAnalyzer, 
    ReliabilityAnalyzer
)
from validator_service.quality_wheel import QualityWheel

class PracticeValidator:
    def __init__(self):
        self.analyzers = {
            "Q": QualityAnalyzer(),
            "R": ReproducibilityAnalyzer(),
            "U": UtilityAnalyzer(),
            "A": ApplicabilityAnalyzer(),
            "I": InnovationAnalyzer(),
            "Rel": ReliabilityAnalyzer()
        }
        self.quality_wheel = QualityWheel()

    def validate_practice(self, practice_data: Dict[str, Any]) -> Dict[str, Any]:
        # Получаем оценки от всех анализаторов
        scores = {
            key: analyzer.analyze(practice_data)
            for key, analyzer in self.analyzers.items()
        }
        
        # Применяем штурвал качества
        evaluation = self.quality_wheel.evaluate_practice(scores)
        
        result = {
            "scores": scores,
            "valid_scores": evaluation["valid_scores"],
            "invalid_scores": evaluation["invalid_scores"],
            "final_score": evaluation["final_score"],
            "reliability_score": evaluation["reliability_score"],
            "recommendations": evaluation["recommendations"],
            "decision": self._make_decision(evaluation)
        }
        
        return result

    def _make_decision(self, evaluation: Dict[str, Any]) -> str:
        """Принятие решения на основе валидации"""
        if evaluation["missing_required"]:
            return "needs_improvement"
        if evaluation["final_score"] is None:
            return "incomplete"
        if evaluation["final_score"] >= 7.0:
            return "approve"
        if evaluation["final_score"] >= 5.0:
            return "review"
        return "reject" 