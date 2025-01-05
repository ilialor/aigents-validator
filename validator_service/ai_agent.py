from typing import Dict, Any, Optional
from .analyzers.quality import QualityAnalyzer
from .analyzers.reproducibility import ReproducibilityAnalyzer
from .analyzers.utility import UtilityAnalyzer
from .analyzers.applicability import ApplicabilityAnalyzer
from .analyzers.innovation import InnovationAnalyzer
from .analyzers.reliability import ReliabilityAnalyzer

class PracticeAnalyzer:
    """Основной класс для анализа практик"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.analyzers = {
            "Q": QualityAnalyzer(self.config),
            "R": ReproducibilityAnalyzer(self.config),
            "U": UtilityAnalyzer(self.config),
            "A": ApplicabilityAnalyzer(self.config),
            "I": InnovationAnalyzer(self.config),
            "Rel": ReliabilityAnalyzer(self.config)
        }
        
        self.weights = {
            "Q": 0.25,
            "R": 0.20,
            "U": 0.20,
            "A": 0.20,
            "I": 0.15
        }
        
    def analyze(self, practice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ практики по всем критериям"""
        if not self._validate_practice_data(practice_data):
            raise ValueError("Invalid practice data format")
            
        results = {}
        
        # Анализируем по каждому критерию
        for criterion, analyzer in self.analyzers.items():
            results[criterion] = analyzer.analyze(practice_data)
            
        # Вычисляем sota_score
        sota_scores = {k: v["score"] for k, v in results.items() if k != "Rel"}
        sota_score = sum(sota_scores[k] * self.weights[k] for k in self.weights)
        
        return {
            "scores": results,
            "sota_score": round(sota_score, 2),
            "reliability_score": results["Rel"]["score"] if "Rel" in results else None
        }
    
    def _validate_practice_data(self, data: Dict[str, Any]) -> bool:
        """Проверка корректности входных данных"""
        required_fields = ['title', 'summary', 'problem', 'solution']
        return all(field in data and data[field] for field in required_fields)

def analyze_practice(practice_data: Dict[str, Any], custom_config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Анализирует практику и возвращает оценки по критериям Q.R.U.A.I. + Reliability
    """
    analyzer = PracticeAnalyzer(custom_config)
    return analyzer.analyze(practice_data) 