import hashlib
import json
import time
from typing import Any, Optional

from models.assessment import AssessmentConfig
from models.questions.mcq import MCQQuestion


class CacheService:
    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, list[MCQQuestion]]] = {}

    def compute_cache_key(self, config: AssessmentConfig, count: int) -> str:
        normalized = {
            "skill_category": config.skill_category.strip().lower(),
            "topic": config.topic.strip().lower(),
            "difficulty": config.difficulty,
            "experience_level": config.experience_level.strip().lower(),
            "assessment_type": config.assessment_type.strip().lower(),
            "learning_objectives": config.learning_objectives.strip().lower(),
            "count": count,
        }
        payload = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def get(self, cache_key: str) -> Optional[list[MCQQuestion]]:
        entry = self._store.get(cache_key)
        if not entry:
            return None
        expires_at, questions = entry
        if time.time() > expires_at:
            del self._store[cache_key]
            return None
        return questions

    def set(self, cache_key: str, questions: list[MCQQuestion]) -> None:
        self._store[cache_key] = (time.time() + self._ttl, questions)

    def clear_expired(self) -> None:
        now = time.time()
        expired = [key for key, (expires_at, _) in self._store.items() if now > expires_at]
        for key in expired:
            del self._store[key]
