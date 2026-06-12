import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from models.assessment import (
    AnswerRecord,
    AssessmentConfig,
    AssessmentResultsResponse,
    FeedbackResponse,
    GenerateAssessmentResponse,
    QuestionResult,
    SessionState,
    StartAssessmentResponse,
    SubmitAnswerResponse,
    TopicBreakdown,
)
from models.questions.mcq import MCQQuestionPublic
from prompts.mcq_generation import build_feedback_prompt
from services.gemini_service import GeminiService
from services.mcq_evaluator import MCQEvaluator
from services.question_generator import QuestionGenerator


class AssessmentService:
    def __init__(
        self,
        generator: QuestionGenerator,
        evaluator: MCQEvaluator,
        gemini: GeminiService,
    ) -> None:
        self._generator = generator
        self._evaluator = evaluator
        self._gemini = gemini
        self._sessions: dict[str, SessionState] = {}

    def generate_assessment(
        self,
        config: AssessmentConfig,
        skip_cache: bool = False,
        cache_key: str | None = None,
    ) -> GenerateAssessmentResponse:
        questions, key, from_cache = self._generator.generate(
            config, skip_cache=skip_cache, cache_key=cache_key
        )
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = SessionState(
            config=config,
            questions=questions,
            started_at=datetime.now(timezone.utc),
        )
        return GenerateAssessmentResponse(
            session_id=session_id,
            cache_key=key,
            questions=[q.to_public() for q in questions],
            total_questions=len(questions),
            from_cache=from_cache,
        )

    def start_from_cache(self, config: AssessmentConfig, cache_key: str) -> StartAssessmentResponse:
        result = self.generate_assessment(config, cache_key=cache_key)
        first = result.questions[0]
        return StartAssessmentResponse(
            session_id=result.session_id,
            cache_key=result.cache_key,
            question=first,
            question_number=1,
            total_questions=result.total_questions,
        )

    def submit_answer(
        self, session_id: str, selected_answer: str, time_ms: int = 0
    ) -> SubmitAnswerResponse:
        session = self._get_session(session_id)
        index = session.current_index
        total = len(session.questions)

        if index >= total:
            raise HTTPException(status_code=400, detail="Assessment is already completed")

        question = session.questions[index]
        evaluation = self._evaluator.evaluate(question, selected_answer)

        session.answers.append(
            AnswerRecord(
                question_id=question.id,
                selected=selected_answer,
                correct=evaluation["correct"],
                time_ms=time_ms,
            )
        )
        session.current_index += 1
        done = session.current_index >= total

        next_question = None
        if not done:
            next_question = session.questions[session.current_index].to_public()

        return SubmitAnswerResponse(
            correct=evaluation["correct"],
            correct_answer=evaluation["correct_answer"],
            explanation=evaluation["explanation"],
            done=done,
            next_question=next_question,
            question_number=session.current_index + 1 if not done else total,
            total_questions=total,
        )

    def get_results(self, session_id: str) -> AssessmentResultsResponse:
        session = self._get_session(session_id)
        if len(session.answers) < len(session.questions):
            raise HTTPException(status_code=400, detail="Assessment not yet completed")

        question_results: list[QuestionResult] = []
        for question, answer in zip(session.questions, session.answers):
            question_results.append(
                QuestionResult(
                    question_id=question.id,
                    question=question.question,
                    options=question.options,
                    selected_answer=answer.selected,
                    correct_answer=question.correct_answer,
                    correct=answer.correct,
                    explanation=question.explanation,
                    topic=question.topic,
                    difficulty=question.difficulty,
                    time_ms=answer.time_ms,
                )
            )

        correct_count = sum(1 for a in session.answers if a.correct)
        total = len(session.questions)
        total_time = sum(a.time_ms for a in session.answers)

        return AssessmentResultsResponse(
            skill_category=session.config.skill_category,
            topic=session.config.topic,
            difficulty=session.config.difficulty,
            experience_level=session.config.experience_level,
            assessment_type=session.config.assessment_type,
            accuracy_percent=round((correct_count / total) * 100, 1) if total else 0.0,
            correct_count=correct_count,
            total_questions=total,
            total_time_ms=total_time,
            avg_time_ms=round(total_time / total, 0) if total else 0.0,
            questions=question_results,
        )

    def generate_feedback(self, session_id: str) -> FeedbackResponse:
        session = self._get_session(session_id)
        if session.feedback:
            return session.feedback

        results = self.get_results(session_id)
        results_summary = [
            {
                "question": q.question,
                "topic": q.topic,
                "selected": q.selected_answer,
                "correct": q.correct,
                "correct_answer": q.correct_answer,
                "time_ms": q.time_ms,
            }
            for q in results.questions
        ]

        prompt = build_feedback_prompt(
            session.config, results_summary, results.accuracy_percent
        )
        data = self._gemini.generate_json(prompt)

        topic_breakdown = [
            TopicBreakdown(
                topic=item.get("topic", session.config.topic),
                accuracy=float(item.get("accuracy", 0)),
                correct=int(item.get("correct", 0)),
                total=int(item.get("total", 0)),
            )
            for item in data.get("topic_breakdown", [])
        ]

        if not topic_breakdown:
            topic_stats: dict[str, dict] = {}
            for q in results.questions:
                if q.topic not in topic_stats:
                    topic_stats[q.topic] = {"correct": 0, "total": 0}
                topic_stats[q.topic]["total"] += 1
                if q.correct:
                    topic_stats[q.topic]["correct"] += 1
            topic_breakdown = [
                TopicBreakdown(
                    topic=topic,
                    correct=stats["correct"],
                    total=stats["total"],
                    accuracy=round((stats["correct"] / stats["total"]) * 100, 1),
                )
                for topic, stats in topic_stats.items()
            ]

        feedback = FeedbackResponse(
            summary=data.get("summary", "Assessment completed."),
            strengths=data.get("strengths", []),
            improvements=data.get("improvements", []),
            topic_breakdown=topic_breakdown,
        )
        session.feedback = feedback
        return feedback

    def _get_session(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        return self._sessions[session_id]
