import json
import os
from pathlib import Path
from typing import Dict, Any, List
from tabulate import tabulate
from validator_service.analyzers import (
    QualityAnalyzer,
    ReproducibilityAnalyzer,
    UtilityAnalyzer,
    ApplicabilityAnalyzer,
    InnovationAnalyzer,
    ReliabilityAnalyzer
)

class AnalyzerTester:
    def __init__(self):
        self.analyzers = {
            "Quality": QualityAnalyzer(),
            "Reproducibility": ReproducibilityAnalyzer(),
            "Utility": UtilityAnalyzer(),
            "Applicability": ApplicabilityAnalyzer(),
            "Innovation": InnovationAnalyzer(),
            "Reliability": ReliabilityAnalyzer()
        }
        
    def load_test_data(self) -> List[Dict[str, Any]]:
        """Загружает тестовые данные из папки test-set"""
        test_data = []
        test_dir = Path(__file__).parent.parent / "docs" / "test-set"
        
        for file_path in test_dir.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                practice = json.load(f)
                practice['_file_name'] = file_path.name
                test_data.append(practice)
                
        return test_data
    
    def analyze_practice(self, practice: Dict) -> Dict[str, Any]:
        results = {}
        for name, analyzer in self.analyzers.items():
            try:
                # Используем синхронный метод
                result = analyzer.analyze_sync(practice)
                results[name] = result.get("score", 0.0)
            except Exception as e:
                print(f"Error analyzing {practice['_file_name']} with {name}: {str(e)}")
                results[name] = "ERROR"
        return results
    
    def run_tests(self) -> List[Dict[str, Any]]:
        """Запускает тестирование на всем наборе данных"""
        test_data = self.load_test_data()
        results = []
        
        for practice in test_data:
            analysis_results = self.analyze_practice(practice)
            results.append({
                "Practice": practice['_file_name'],
                "Title": practice['title'],
                **{k: v for k, v in analysis_results.items() if not k.endswith(('_details', '_explanation'))}
            })
            
            # Сохраняем детальные результаты
            details_file = Path(__file__).parent.parent / "results" / f"details_{practice['_file_name']}"
            with open(details_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "practice": practice,
                    "analysis": analysis_results
                }, f, indent=2, ensure_ascii=False)
                
        return results
    
    def print_results_table(self, results: List[Dict[str, Any]]):
        """Выводит результаты в виде таблицы"""
        headers = ["Practice", "Title", "Quality", "Reproducibility", "Utility", 
                   "Applicability", "Innovation", "Reliability"]
        
        table_data = []
        for result in results:
            row = [
                result["Practice"],
                result["Title"][:35] + "..." if len(result["Title"]) > 35 else result["Title"],
                str(result["Quality"]) if result["Quality"] is not None else "ERROR",
                str(result["Reproducibility"]) if result["Reproducibility"] is not None else "ERROR",
                str(result["Utility"]) if result["Utility"] is not None else "ERROR",
                str(result["Applicability"]) if result["Applicability"] is not None else "ERROR",
                str(result["Innovation"]) if result["Innovation"] is not None else "ERROR",
                str(result["Reliability"]) if result["Reliability"] is not None else "ERROR"
            ]
            table_data.append(row)
            
        print("\nAnalysis Results:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Вычисляем средние оценки для каждой практики
        print("\nAverage Scores:")
        for result in results:
            scores = []
            for key in ["Quality", "Reproducibility", "Utility", "Applicability", 
                       "Innovation", "Reliability"]:
                if isinstance(result[key], (int, float)):
                    scores.append(float(result[key]))
            if scores:
                avg_score = sum(scores) / len(scores)
                print(f"{result['Practice']}: {avg_score:.2f}")

def main():
    tester = AnalyzerTester()
    results = tester.run_tests()
    tester.print_results_table(results)

def test_utility():
    analyzer = UtilityAnalyzer()
    result = analyzer.analyze_sync(practice_data)  # Используем sync версию
    assert isinstance(result, dict)
    assert "score" in result
    assert "details" in result

if __name__ == "__main__":
    main() 