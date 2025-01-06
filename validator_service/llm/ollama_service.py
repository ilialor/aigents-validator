from typing import Dict, Any, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class OllamaService:
    """Сервис для работы с Ollama API"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.base_url = self.config.get("OLLAMA_API_URL", "http://ollama:11434")
        self.model = self.config.get("OLLAMA_MODEL", "llama2")
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_embeddings(self, text: str) -> List[float]:
        """Получение эмбеддингов текста"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                }
            )
            return response.json()["embedding"]
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_completion(self, prompt: str) -> str:
        """Получение completion от модели"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            return response.json()["response"] 