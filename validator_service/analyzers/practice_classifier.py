from enum import Enum
from typing import Dict, Any, Tuple

class PracticeType(Enum):
    SCIENTIFIC = "scientific"      # Научные методы, исследования
    ENGINEERING = "engineering"    # Инженерные практики, технические решения
    PROCESS = "process"           # Процессные практики (agile, code review)
    MANAGEMENT = "management"      # Управленческие практики
    
class PracticeClassifier:
    """Классификатор типов практик"""
    
    def classify(self, practice_data: Dict[str, Any]) -> Tuple[PracticeType, bool]:
        text = f"{practice_data.get('solution', '')} {practice_data.get('summary', '')}"
        text = text.lower()
        
        # Определяем тип практики
        practice_type = self._determine_type(text)
        
        # Учитываем категорию (концепт/реализация)
        is_concept = practice_data.get('category') == 'concept'
        
        return practice_type, is_concept
        
    def _determine_type(self, text: str) -> PracticeType:
        # Научные индикаторы
        if any(ind in text for ind in [
            'doi:', 'p-value', 'statistical', 'empirical',
            'hypothesis', 'experiment', 'research'
        ]):
            return PracticeType.SCIENTIFIC
            
        # Инженерные индикаторы
        if any(ind in text for ind in [
            'algorithm', 'implementation', 'code', 'architecture',
            'system', 'technical', 'software', 'development'
        ]):
            return PracticeType.ENGINEERING
            
        # Процессные индикаторы
        if any(ind in text for ind in [
            'process', 'workflow', 'methodology', 'practice',
            'review', 'agile', 'scrum', 'devops'
        ]):
            return PracticeType.PROCESS
            
        # По умолчанию - управленческие
        return PracticeType.MANAGEMENT 