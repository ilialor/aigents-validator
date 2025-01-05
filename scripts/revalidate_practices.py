import asyncio
import aiohttp
import json
from typing import List, Dict, Any
from pathlib import Path
from validator_service.validator import PracticeValidator
from datetime import datetime

class PracticeRevalidator:
    def __init__(self):
        self.validator = PracticeValidator()
        self.storage_api = "http://aigents-storage-api-1:8000/api/v1"
        
    async def get_all_practices(self) -> List[str]:
        """Получение списка всех ID практик"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.storage_api}/practices") as response:
                response.raise_for_status()
                data = await response.json()
                
                # API возвращает данные в формате {'items': [...]}
                if isinstance(data, dict) and 'items' in data:
                    practices = data['items']
                else:
                    raise ValueError(f"Unexpected response format: {data}")
                    
                # Извлекаем ID из каждой практики
                return [p.get("id") for p in practices if isinstance(p, dict)]

    async def get_practice(self, practice_id: str) -> Dict[str, Any]:
        """Получение данных практики по ID"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.storage_api}/practices/{practice_id}") as response:
                response.raise_for_status()
                data = await response.json()
                if isinstance(data, str):
                    data = json.loads(data)
                return data

    async def update_validation(self, practice_id: str, validation: Dict[str, Any]) -> None:
        """Обновление результатов валидации"""
        # Убеждаемся, что все данные сериализуемы
        validation_data = {
            "scores": validation["scores"],
            "valid_scores": validation["valid_scores"],
            "invalid_scores": validation["invalid_scores"],
            "final_score": validation["final_score"],
            "reliability_score": validation["reliability_score"],
            "recommendations": validation["recommendations"],
            "decision": validation["decision"]
        }
        
        async with aiohttp.ClientSession() as session:
            # Сначала проверяем существование валидации
            try:
                async with session.get(
                    f"{self.storage_api}/practices/{practice_id}/validation"
                ) as response:
                    if response.status == 404:
                        # Если валидации нет, создаем новую через POST
                        async with session.post(
                            f"{self.storage_api}/practices/{practice_id}/validation",
                            json=validation_data
                        ) as post_response:
                            post_response.raise_for_status()
                            return await post_response.json()
                    else:
                        # Если валидация существует, обновляем через PATCH
                        async with session.patch(
                            f"{self.storage_api}/practices/{practice_id}/validation",
                            json=validation_data
                        ) as patch_response:
                            patch_response.raise_for_status()
                            return await patch_response.json()
            except Exception as e:
                print(f"Error updating validation for practice {practice_id}: {str(e)}")
                print(f"Validation data: {json.dumps(validation_data, indent=2)}")
                raise

    def validate_practice(self, practice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация практики новым алгоритмом"""
        return self.validator.validate_practice(practice_data)

    async def revalidate_all(self) -> Dict[str, Any]:
        """Перевалидация всех практик"""
        results = {
            "total": 0,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "failures": [],
            "validations": []  # Сохраняем результаты валидации
        }

        try:
            practice_ids = await self.get_all_practices()
            results["total"] = len(practice_ids)
            
            for practice_id in practice_ids:
                try:
                    print(f"\nProcessing practice {practice_id}")
                    
                    practice_data = await self.get_practice(practice_id)
                    print(f"Retrieved practice data")
                    
                    validation_result = self.validate_practice(practice_data)
                    print(f"Validation completed with scores:")
                    print(f"Final score: {validation_result.get('final_score')}")
                    print(f"Valid scores: {json.dumps(validation_result.get('valid_scores'), indent=2)}")
                    
                    await self.update_validation(practice_id, validation_result)
                    print(f"Validation results updated")
                    
                    results["success"] += 1
                    results["validations"].append({
                        "id": practice_id,
                        "validation": validation_result
                    })
                    
                except Exception as e:
                    print(f"Error processing practice {practice_id}: {e}")
                    results["failed"] += 1
                    results["failures"].append({
                        "id": practice_id,
                        "error": str(e)
                    })
                    
                results["processed"] += 1
                print(f"Progress: {results['processed']}/{results['total']} practices")
                
        except Exception as e:
            print(f"Failed to get practice list: {e}")
            results["failures"].append({
                "error": str(e)
            })
            
        return results

    def save_results(self, results: Dict[str, Any], filename: str = "revalidation_results.json"):
        """Сохранение результатов перевалидации"""
        # Создаем директорию results если её нет
        results_dir = Path("/app/results")
        results_dir.mkdir(exist_ok=True)
        
        # Формируем имя файла с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = results_dir / f"revalidation_results_{timestamp}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to {filepath}")
        except Exception as e:
            print(f"\nError saving results to {filepath}: {e}")
            # Пробуем сохранить в текущую директорию
            backup_path = Path(f"revalidation_results_{timestamp}.json")
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to backup location: {backup_path}")


async def main():
    revalidator = PracticeRevalidator()
    
    print("Starting revalidation of all practices...")
    results = await revalidator.revalidate_all()
    
    print("\nRevalidation completed!")
    print(f"Total practices: {results['total']}")
    print(f"Successfully processed: {results['success']}")
    print(f"Failed: {results['failed']}")
    
    if results['validations']:
        print("\nSuccessful validations:")
        for validation in results['validations']:
            print(f"\nPractice {validation['id']}:")
            print(f"Final score: {validation['validation']['final_score']}")
            print(f"Decision: {validation['validation']['decision']}")
    
    if results['failures']:
        print("\nFailures:")
        for failure in results['failures']:
            if 'id' in failure:
                print(f"Practice {failure['id']}: {failure['error']}")
            else:
                print(f"General error: {failure['error']}")
    
    # Сохраняем результаты
    revalidator.save_results(results)
    print(f"\nResults saved to revalidation_results.json")


if __name__ == "__main__":
    asyncio.run(main()) 