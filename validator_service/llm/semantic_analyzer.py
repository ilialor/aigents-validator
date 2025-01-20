from typing import Dict, Any, List
import json
from .ollama_service import OllamaService

class SemanticAnalyzer:
    """Семантический анализатор на основе Llama2"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.ollama = OllamaService(config)
        
    async def analyze_utility(self, text: str) -> Dict[str, float]:
        """Анализ полезности через Llama2"""
        prompt = """
        You are an expert in analyzing software development practices.
        
        Evaluate the utility of the described practice on these criteria (0-10):
        1. Fundamental Value - scientific and theoretical value
        2. Practical Value - real-world applicability
        3. Measurable Value - quantifiable results
        
        Practice description:
        {text}
        
        Provide scores in JSON format:
        {{"fundamental_value": float, "practical_value": float, "measurable_value": float}}
        
        Explain your reasoning after the JSON.
        """
        
        response = await self.ollama.get_completion(prompt.format(text=text))
        return self._extract_scores(response)
        
    async def analyze_applicability(self, text: str) -> Dict[str, float]:
        """Анализ применимости через Llama2"""
        prompt = """
        You are an expert in analyzing software development practices.
        
        Evaluate the applicability of the described practice on these criteria (0-10):
        1. Universality - how universal is the approach
        2. Adaptability - adaptability to different contexts
        3. Accessibility - ease of implementation
        
        Consider:
        - Scientific methods should score high on universality (8-10)
        - Formal approaches are more adaptable
        - Clear steps increase accessibility
        
        Practice description:
        {text}
        
        Provide scores in JSON format:
        {{"universality": float, "adaptability": float, "accessibility": float}}
        
        Explain your reasoning after the JSON.
        """
        
        response = await self.ollama.get_completion(prompt.format(text=text))
        return self._extract_scores(response)
    
    def _extract_scores(self, response: str) -> Dict[str, float]:
        """Извлекает JSON со скорами из ответа модели"""
        try:
            # Ищем первый JSON в ответе
            start = response.find("{")
            end = response.find("}") + 1
            if start >= 0 and end > start:
                scores_json = response[start:end]
                scores = json.loads(scores_json)
                if not scores:
                    raise ValueError("Empty scores dictionary")
                return scores
            raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Error extracting scores: {e}")
            print(f"Response: {response}")
            # Возвращаем дефолтные значения вместо пустого словаря
            return {
                "fundamental_value": 5.0,
                "practical_value": 5.0,
                "measurable_value": 5.0,
                "universality": 5.0,
                "adaptability": 5.0,
                "accessibility": 5.0
            } 