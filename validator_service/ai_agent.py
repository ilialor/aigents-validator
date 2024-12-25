from typing import Dict, Any

def analyze_practice(practice_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Анализирует практику и возвращает оценки по критериям A.I.Q.R.U.
    
    Args:
        practice_data: Данные практики для анализа
        
    Returns:
        Dict с оценками по критериям и общим sota_score
    """
    # TODO: Реализовать реальную логику AI-анализа
    # Для MVP возвращаем тестовые значения
    return {
        "Q": 7.0,  # Quality (качество)
        "R": 7.0,  # Reproducibility (воспроизводимость)
        "U": 4.0,  # Utility (полезность)
        "A": 5.0,  # Applicability (применимость)
        "I": 6.0,  # Innovation (инновационность)
        "sota_score": 5.8  # Средняя оценка
    } 