import uuid

from fastapi import HTTPException

from config import get_settings
from models.assessment import AssessmentConfig
from models.questions.mcq import MCQQuestion
from prompts.mcq_generation import build_mcq_fix_json_prompt, build_mcq_generation_prompt
from services.cache_service import CacheService
from services.gemini_service import GeminiService


class QuestionGenerator:
    def __init__(self, gemini: GeminiService, cache: CacheService) -> None:
        self._gemini = gemini
        self._cache = cache
        self._settings = get_settings()

    def generate(
        self,
        config: AssessmentConfig,
        skip_cache: bool = False,
        cache_key: str | None = None,
        previously_asked: list[str] | None = None,
    ) -> tuple[list[MCQQuestion], str, bool]:
        count = config.question_count or self._settings.question_count
        key = cache_key or self._cache.compute_cache_key(config, count)

        if not skip_cache:
            cached = self._cache.get(key)
            if cached:
                return cached, key, True

        questions = self._generate_from_gemini(config, count, previously_asked)
        self._cache.set(key, questions)
        return questions, key, False

    def _generate_from_gemini(
        self,
        config: AssessmentConfig,
        count: int,
        previously_asked: list[str] | None,
    ) -> list[MCQQuestion]:
        prompt = build_mcq_generation_prompt(config, count, previously_asked)
        raw_data = self._gemini.generate_json(prompt)

        try:
            return self._parse_questions(raw_data, config)
        except (ValueError, HTTPException):
            fix_prompt = build_mcq_fix_json_prompt(str(raw_data))
            fixed_data = self._gemini.generate_json(fix_prompt)
            return self._parse_questions(fixed_data, config)

    def _parse_questions(self, data: object, config: AssessmentConfig) -> list[MCQQuestion]:
        if not isinstance(data, list):
            raise HTTPException(status_code=502, detail="Gemini returned invalid question format")

        questions: list[MCQQuestion] = []
        seen_texts: set[str] = set()

        for item in data:
            if not isinstance(item, dict):
                continue
            text_key = item.get("question", "").strip().lower()
            if not text_key or text_key in seen_texts:
                continue
            seen_texts.add(text_key)

            question = MCQQuestion(
                id=str(uuid.uuid4()),
                topic=item.get("topic", config.topic),
                difficulty=item.get("difficulty", config.difficulty),
                question=item["question"],
                options=item["options"],
                correct_answer=item.get("correctAnswer") or item.get("correct_answer", ""),
                explanation=item["explanation"],
            )
            questions.append(question)

        expected = config.question_count or self._settings.question_count
        if len(questions) < expected:
            raise HTTPException(
                status_code=502,
                detail=f"Gemini returned {len(questions)} questions, expected {expected}",
            )

        return questions[:expected]
