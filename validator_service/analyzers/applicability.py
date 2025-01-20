from typing import Dict, Any, List
import spacy
from textblob import TextBlob
import re
from .base import BaseAnalyzer
from .practice_classifier import PracticeClassifier, PracticeType
from enum import Enum

class ApplicabilityAnalyzer(BaseAnalyzer):
    """Анализатор применимости (A)"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_md")
        self.classifier = PracticeClassifier()
        
    def analyze_sync(self, practice_data: Dict[str, Any]) -> Dict[str, float]:
        practice_type, is_concept = self.classifier.classify(practice_data)
        base_score = self._analyze_generalization(practice_data)
        
        # Увеличиваем множители
        type_multipliers = {
            PracticeType.SCIENTIFIC.value: 1.4,     # Было 1.2
            PracticeType.ENGINEERING.value: 1.3,    # Было 1.1
            PracticeType.PROCESS.value: 1.1,        # Было 0.9
            PracticeType.MANAGEMENT.value: 1.0      # Было 0.8
        }
        
        final_score = base_score * type_multipliers[practice_type.value]
        
        # Увеличиваем бонусы
        if re.search(r'documentation|user guide|manual|tutorial', practice_data.get('solution', '').lower()):
            final_score += 1.5  # Было 1.0
            
        if re.search(r'example|case study|use case|implementation', practice_data.get('solution', '').lower()):
            final_score += 1.5  # Было 1.0
            
        # Добавляем бонус за подтвержденное внедрение
        if re.search(r'successfully (implemented|deployed|used) in \d+', practice_data.get('solution', '').lower()):
            final_score += 2.0
            
        return {
            "score": round(min(final_score, 10.0), 2),
            "details": {
                "base_score": base_score, 
                "multiplier": type_multipliers[practice_type.value],
                "is_concept": is_concept
            }
        }
        
    def _analyze_scientific_applicability(self, data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "reproducibility": self._analyze_reproducibility(data),
            "generalization": self._analyze_generalization(data),
            "resource_requirements": self._analyze_resources(data)
        }
        weights = {"reproducibility": 0.4, "generalization": 0.4, "resource_requirements": 0.2}
        return self._calculate_final_score(scores, weights)
    
    def _analyze_reproducibility(self, data: Dict[str, Any]) -> float:
        """Оценка воспроизводимости"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        text = text.lower()
        
        # Проверяем воспроизводимость
        reproducibility_indicators = {
            "scope": ["universal", "general", "common", "standard", "fundamental"],
            "domain": ["any domain", "multiple fields", "various areas", "different contexts"],
            "flexibility": ["adaptable", "flexible", "customizable", "configurable"]
        }
        
        for category, terms in reproducibility_indicators.items():
            found = sum(1 for term in terms if term in text)
            if found > 0:
                score += min(found * 2.5, 5.0)
        
        # Проверяем домены применения
        if isinstance(data.get("sub_domains"), list):
            score += min(len(data["sub_domains"]) * 1.5, 4.0)
        
        # Проверяем контексты
        contexts = ["team", "organization", "industry", "research", "development", "production"]
        found_contexts = sum(1 for ctx in contexts if ctx in text)
        score += min(found_contexts * 1.0, 3.0)
        
        return self._normalize_score(score)

    def _analyze_generalization(self, data: Dict[str, Any]) -> float:
        """Оценка обобщаемости"""
        score = 6.0  # Увеличиваем базовую оценку с 5.0 до 6.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        text = text.lower()
        
        # Проверяем универсальность (увеличиваем веса)
        universality_indicators = [
            ("universal solution", 2.0),
            ("widely applicable", 1.5),
            ("general purpose", 1.5),
            ("cross-domain", 1.5),
            ("industry standard", 1.0),
            ("versatile", 1.0),
            ("flexible", 1.0),
            ("adaptable", 1.0),
            ("reusable", 1.0),
            ("scalable", 1.0)
        ]
        
        # Смягчаем штрафы за ограничения
        limitation_indicators = [
            ("only works with", -1.5),
            ("limited to", -1.0),
            ("specific to", -1.0),
            ("requires specific", -1.0),
            ("not suitable for", -1.0),
            ("cannot be used", -1.0),
            ("only applicable", -0.5),
            ("restricted to", -0.5)
        ]
        
        # Проверяем области применения
        domain_bonuses = {
            "scientific": ["research", "science", "academic", "study", "laboratory"],
            "engineering": ["development", "technical", "software", "system", "architecture"],
            "business": ["enterprise", "company", "organization", "industry", "commercial"],
            "education": ["learning", "teaching", "training", "education", "academic"],
            "production": ["manufacturing", "production", "industrial", "factory", "operations"]
        }
        
        # Подсчет основных индикаторов
        for term, points in universality_indicators:
            if term in text:
                score += points
                
        # Учет ограничений (с меньшими штрафами)
        for term, points in limitation_indicators:
            if term in text:
                score += points
        
        # Бонусы за области применения
        domain_count = 0
        for domain, terms in domain_bonuses.items():
            if any(term in text for term in terms):
                domain_count += 1
        score += domain_count * 0.5
        
        # Бонусы за готовность к внедрению
        if re.search(r'(ready to use|easy to implement|documented|guide|tutorial)', text):
            score += 1.0
        
        if re.search(r'(example|case study|success story)', text):
            score += 1.0
        
        if re.search(r'(customizable|configurable|adjustable)', text):
            score += 0.5
            
        return self._normalize_score(score)

    def _analyze_resources(self, data: Dict[str, Any]) -> float:
        """Оценка ресурсоемкости"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        text = text.lower()
        
        # Проверяем ресурсоемкость
        resource_indicators = {
            "scope": ["universal", "general", "common", "standard", "fundamental"],
            "domain": ["any domain", "multiple fields", "various areas", "different contexts"],
            "flexibility": ["adaptable", "flexible", "customizable", "configurable"]
        }
        
        for category, terms in resource_indicators.items():
            found = sum(1 for term in terms if term in text)
            if found > 0:
                score += min(found * 2.5, 5.0)
        
        # Проверяем домены применения
        if isinstance(data.get("sub_domains"), list):
            score += min(len(data["sub_domains"]) * 1.5, 4.0)
        
        # Проверяем контексты
        contexts = ["team", "organization", "industry", "research", "development", "production"]
        found_contexts = sum(1 for ctx in contexts if ctx in text)
        score += min(found_contexts * 1.0, 3.0)
        
        return self._normalize_score(score)
    
    def _generate_explanation(self, scores: Dict[str, float]) -> str:
        """Генерирует текстовое объяснение оценок"""
        explanations = []
        
        if scores["reproducibility"] >= 8:
            explanations.append("Практика широко воспроизводима")
        elif scores["reproducibility"] >= 5:
            explanations.append("Практика имеет достаточную воспроизводимость")
        else:
            explanations.append("Требуется улучшить воспроизводимость")
            
        if scores["generalization"] >= 8:
            explanations.append("Практика широко обобщаема")
        elif scores["generalization"] >= 5:
            explanations.append("Практика имеет достаточную обобщаемость")
        else:
            explanations.append("Требуется улучшить обобщаемость")
            
        if scores["resource_requirements"] >= 8:
            explanations.append("Практика имеет достаточную ресурсоемкость")
        else:
            explanations.append("Требуется улучшить ресурсоемкость")
            
        return ". ".join(explanations) 

    def _analyze_scope(self, data: Dict[str, Any]) -> float:
        score = 0.0
        
        # Универсальные научные методы получают бонус
        scientific_terms = [
            "statistical analysis", "methodology",
            "systematic approach", "framework",
            "general method", "universal"
        ]
        
        text = f"{data.get('solution', '')} {data.get('summary', '')}"
        if any(term in text.lower() for term in scientific_terms):
            score += 4.0  # Бонус за универсальность
        
        # Остальная логика...
        return self._normalize_score(score) 

    def _analyze_engineering_applicability(self, data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "technical_feasibility": self._analyze_technical_feasibility(data),
            "implementation_ease": self._analyze_implementation_ease(data),
            "resource_efficiency": self._analyze_resource_efficiency(data)
        }
        weights = {"technical_feasibility": 0.4, "implementation_ease": 0.3, "resource_efficiency": 0.3}
        return self._calculate_final_score(scores, weights)

    def _analyze_process_applicability(self, data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "process_integration": self._analyze_process_integration(data),
            "team_adoption": self._analyze_team_adoption(data),
            "organizational_fit": self._analyze_organizational_fit(data)
        }
        weights = {"process_integration": 0.4, "team_adoption": 0.3, "organizational_fit": 0.3}
        return self._calculate_final_score(scores, weights)

    def _analyze_management_applicability(self, data: Dict[str, Any]) -> Dict[str, float]:
        scores = {
            "organizational_impact": self._analyze_organizational_impact(data),
            "resource_requirements": self._analyze_resource_requirements(data),
            "implementation_complexity": self._analyze_implementation_complexity(data)
        }
        weights = {"organizational_impact": 0.4, "resource_requirements": 0.3, "implementation_complexity": 0.3}
        return self._calculate_final_score(scores, weights)

    def _analyze_organizational_impact(self, data: Dict[str, Any]) -> float:
        """Оценка организационного влияния"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        impact_indicators = [
            ("organization wide", 3.0),
            ("culture change", 2.5),
            ("strategic", 2.0),
            ("transformation", 2.0),
            ("alignment", 1.5),
            ("integration", 1.5)
        ]
        
        for term, points in impact_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)

    def _analyze_implementation_complexity(self, data: Dict[str, Any]) -> float:
        """Оценка сложности внедрения"""
        score = 10.0  # Начинаем с максимума и вычитаем за сложность
        text = f"{data.get('solution', '')} {data.get('implementation_steps', '')}"
        text = text.lower()
        
        complexity_indicators = [
            ("complex", -2.0),
            ("difficult", -2.0),
            ("challenging", -1.5),
            ("requires training", -1.5),
            ("time consuming", -1.5),
            ("prerequisite", -1.0)
        ]
        
        for term, points in complexity_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)

    def _analyze_resource_requirements(self, data: Dict[str, Any]) -> float:
        """Оценка требований к ресурсам"""
        score = 10.0  # Начинаем с максимума и вычитаем за требования
        text = f"{data.get('solution', '')} {data.get('requirements', '')}"
        text = text.lower()
        
        requirement_indicators = [
            ("expensive", -2.0),
            ("high cost", -2.0),
            ("significant resources", -2.0),
            ("specialized tools", -1.5),
            ("dedicated team", -1.5),
            ("infrastructure", -1.0)
        ]
        
        for term, points in requirement_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score) 

    def _calculate_final_score(self, scores: Dict[str, float], weights: Dict[str, float]) -> Dict[str, float]:
        """Вычисляет финальную оценку"""
        final_score = sum(scores[k] * weights[k] for k in scores)
        return {
            "score": round(min(final_score, 10.0), 2),
            "details": scores
        }

    def _analyze_technical_feasibility(self, data: Dict[str, Any]) -> float:
        """Оценка технической осуществимости"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('implementation_steps', '')}"
        text = text.lower()
        
        feasibility_indicators = [
            ("proven technology", 3.0),
            ("tested solution", 2.5),
            ("working prototype", 2.5),
            ("implementation guide", 2.0),
            ("technical details", 2.0),
            ("documentation", 1.5)
        ]
        
        for term, points in feasibility_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)

    def _analyze_implementation_ease(self, data: Dict[str, Any]) -> float:
        """Оценка простоты внедрения"""
        score = 10.0  # Начинаем с максимума и вычитаем за сложность
        text = f"{data.get('solution', '')} {data.get('implementation_steps', '')}"
        text = text.lower()
        
        complexity_indicators = [
            ("complex setup", -2.0),
            ("difficult integration", -2.0),
            ("extensive configuration", -1.5),
            ("specialized knowledge", -1.5),
            ("technical expertise", -1.5),
            ("training required", -1.0)
        ]
        
        for term, points in complexity_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)

    def _analyze_resource_efficiency(self, data: Dict[str, Any]) -> float:
        """Оценка эффективности использования ресурсов"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        efficiency_indicators = [
            ("resource efficient", 3.0),
            ("cost effective", 2.5),
            ("optimized", 2.0),
            ("lightweight", 2.0),
            ("minimal overhead", 1.5),
            ("low maintenance", 1.5)
        ]
        
        for term, points in efficiency_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)

    def _analyze_process_integration(self, data: Dict[str, Any]) -> float:
        """Оценка интеграции с процессами"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('implementation_steps', '')}"
        text = text.lower()
        
        integration_indicators = [
            ("seamless integration", 3.0),
            ("workflow compatible", 2.5),
            ("process aligned", 2.0),
            ("easy adoption", 2.0),
            ("minimal disruption", 1.5),
            ("gradual rollout", 1.5)
        ]
        
        for term, points in integration_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)

    def _analyze_team_adoption(self, data: Dict[str, Any]) -> float:
        """Оценка принятия командой"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        adoption_indicators = [
            ("user friendly", 3.0),
            ("intuitive", 2.5),
            ("easy to learn", 2.5),
            ("clear benefits", 2.0),
            ("team oriented", 1.5),
            ("collaborative", 1.5)
        ]
        
        for term, points in adoption_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score)

    def _analyze_organizational_fit(self, data: Dict[str, Any]) -> float:
        """Оценка соответствия организации"""
        score = 0.0
        text = f"{data.get('solution', '')} {data.get('benefits', '')}"
        text = text.lower()
        
        fit_indicators = [
            ("organizational alignment", 3.0),
            ("culture fit", 2.5),
            ("strategic value", 2.5),
            ("business goals", 2.0),
            ("scalable solution", 1.5),
            ("long term value", 1.5)
        ]
        
        for term, points in fit_indicators:
            if term in text:
                score += points
                
        return self._normalize_score(score) 