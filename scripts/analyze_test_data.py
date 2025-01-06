import json
from pathlib import Path
from typing import Dict, Any, List
from tabulate import tabulate

class TestDataAnalyzer:
    def __init__(self):
        self.required_fields = {
            "title": {"min_length": 10},
            "summary": {"min_length": 50},
            "problem": {"min_length": 50},
            "solution": {"min_length": 100},
            "domain": {"min_length": 3},
            "sub_domains": {"min_items": 2},
            "implementation_steps": {"min_items": 3, "min_description_length": 50},
            "implementation_requirements": {"min_items": 3},
            "benefits": {"min_items": 3},
            "limitations": {"min_items": 2},
            "estimated_resources": {"min_items": 2},
            "tags": {"min_items": 3}
        }
        
    def load_test_data(self) -> List[Dict[str, Any]]:
        """Загружает тестовые данные"""
        test_data = []
        test_dir = Path(__file__).parent.parent / "docs" / "test-set"
        
        for file_path in test_dir.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                practice = json.load(f)
                practice['_file_name'] = file_path.name
                test_data.append(practice)
                
        return test_data
    
    def analyze_field_quality(self, value: Any, requirements: Dict[str, int]) -> Dict[str, Any]:
        """Анализирует качество заполнения поля"""
        result = {"filled": False, "issues": []}
        
        if value is None:
            result["issues"].append("Field is empty")
            return result
            
        result["filled"] = True
        
        if "min_length" in requirements:
            if isinstance(value, str):
                length = len(value)
                if length < requirements["min_length"]:
                    result["issues"].append(f"Length {length} < {requirements['min_length']}")
                    
        if "min_items" in requirements:
            if isinstance(value, (list, dict)):
                items = len(value)
                if items < requirements["min_items"]:
                    result["issues"].append(f"Items {items} < {requirements['min_items']}")
                    
        if "min_description_length" in requirements and isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and "description" in item:
                    if len(str(item["description"])) < requirements["min_description_length"]:
                        result["issues"].append(
                            f"Step description length < {requirements['min_description_length']}"
                        )
                        
        return result
    
    def analyze_practice(self, practice: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует качество заполнения практики"""
        results = {
            "file": practice['_file_name'],
            "title": practice['title'],
            "fields_total": len(self.required_fields),
            "fields_filled": 0,
            "fields_with_issues": 0,
            "field_details": {}
        }
        
        for field, requirements in self.required_fields.items():
            analysis = self.analyze_field_quality(practice.get(field), requirements)
            results["field_details"][field] = analysis
            
            if analysis["filled"]:
                results["fields_filled"] += 1
            if analysis["issues"]:
                results["fields_with_issues"] += 1
                
        results["completeness"] = round(
            results["fields_filled"] / results["fields_total"] * 100, 1
        )
        
        return results
    
    def print_analysis(self, results: List[Dict[str, Any]]):
        """Выводит результаты анализа"""
        # Общая таблица
        headers = ["Practice", "Title", "Completeness %", "Fields Filled", "Fields with Issues"]
        table_data = []
        
        for result in results:
            table_data.append([
                result["file"],
                result["title"][:40] + "..." if len(result["title"]) > 40 else result["title"],
                f"{result['completeness']}%",
                f"{result['fields_filled']}/{result['fields_total']}",
                result["fields_with_issues"]
            ])
            
        print("\nTest Data Quality Analysis:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Детальный анализ для каждой практики
        for result in results:
            print(f"\nDetailed analysis for {result['file']}:")
            issues = []
            for field, details in result["field_details"].items():
                if details["issues"]:
                    issues.append(f"- {field}: {', '.join(details['issues'])}")
            if issues:
                print("Issues found:")
                print("\n".join(issues))
            else:
                print("No issues found")

def main():
    analyzer = TestDataAnalyzer()
    test_data = analyzer.load_test_data()
    results = [analyzer.analyze_practice(practice) for practice in test_data]
    analyzer.print_analysis(results)

if __name__ == "__main__":
    main() 