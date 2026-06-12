import json
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from database import get_connection, row_to_dict
from models.auth import HistoryDetail, HistorySummary, ReportsSummary
from services.assessment_service import AssessmentService


class HistoryService:
    def __init__(self, assessment_service: AssessmentService) -> None:
        self._assessment = assessment_service

    def save_from_session(self, user_id: str, session_id: str) -> HistorySummary:
        results = self._assessment.get_results(session_id)
        try:
            feedback = self._assessment.generate_feedback(session_id)
            feedback_data = feedback.model_dump()
        except Exception:
            feedback_data = None

        history_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO test_history (
                    id, user_id, session_id, skill_category, topic, difficulty,
                    experience_level, assessment_type, accuracy_percent, correct_count,
                    total_questions, results_json, feedback_json, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    history_id,
                    user_id,
                    session_id,
                    results.skill_category,
                    results.topic,
                    results.difficulty,
                    results.experience_level,
                    results.assessment_type,
                    results.accuracy_percent,
                    results.correct_count,
                    results.total_questions,
                    json.dumps(results.model_dump()),
                    json.dumps(feedback_data) if feedback_data else None,
                    now,
                ),
            )

        return HistorySummary(
            id=history_id,
            skill_category=results.skill_category,
            topic=results.topic,
            difficulty=results.difficulty,
            accuracy_percent=results.accuracy_percent,
            correct_count=results.correct_count,
            total_questions=results.total_questions,
            completed_at=now,
        )

    def list_for_user(self, user_id: str) -> list[HistorySummary]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, skill_category, topic, difficulty, accuracy_percent,
                       correct_count, total_questions, completed_at
                FROM test_history WHERE user_id = ? ORDER BY completed_at DESC
                """,
                (user_id,),
            ).fetchall()

        return [HistorySummary(**row_to_dict(r)) for r in rows]

    def get_detail(self, user_id: str, history_id: str) -> HistoryDetail:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM test_history WHERE id = ? AND user_id = ?",
                (history_id, user_id),
            ).fetchone()

        data = row_to_dict(row)
        if not data:
            raise HTTPException(status_code=404, detail="Test not found")

        return HistoryDetail(
            id=data["id"],
            skill_category=data["skill_category"],
            topic=data["topic"],
            difficulty=data["difficulty"],
            experience_level=data["experience_level"],
            assessment_type=data["assessment_type"],
            accuracy_percent=data["accuracy_percent"],
            correct_count=data["correct_count"],
            total_questions=data["total_questions"],
            completed_at=data["completed_at"],
            results=json.loads(data["results_json"]),
            feedback=json.loads(data["feedback_json"]) if data["feedback_json"] else None,
        )

    def get_reports(self, user_id: str) -> ReportsSummary:
        tests = self.list_for_user(user_id)
        if not tests:
            return ReportsSummary(total_tests=0, average_score=0.0, best_score=0.0, recent_tests=[])

        scores = [t.accuracy_percent for t in tests]
        return ReportsSummary(
            total_tests=len(tests),
            average_score=round(sum(scores) / len(scores), 1),
            best_score=max(scores),
            recent_tests=tests[:5],
        )
