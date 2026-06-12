from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from models.questions.mcq import MCQQuestion, MCQQuestionPublic


class AssessmentConfig(BaseModel):
    skill_category: str
    topic: str
    difficulty: str = Field(..., pattern="^(Easy|Medium|Hard)$")
    experience_level: str
    assessment_type: str
    learning_objectives: str = ""
    question_count: Optional[int] = None


class GenerateAssessmentRequest(AssessmentConfig):
    cache_key: Optional[str] = None
    skip_cache: bool = False


class GenerateAssessmentResponse(BaseModel):
    session_id: str
    cache_key: str
    questions: list[MCQQuestionPublic]
    total_questions: int
    from_cache: bool


class StartAssessmentRequest(BaseModel):
    config: AssessmentConfig
    cache_key: Optional[str] = None


class StartAssessmentResponse(BaseModel):
    session_id: str
    cache_key: str
    question: MCQQuestionPublic
    question_number: int
    total_questions: int


class SubmitAnswerRequest(BaseModel):
    selected_answer: str
    time_ms: int = 0


class SubmitAnswerResponse(BaseModel):
    correct: bool
    correct_answer: str
    explanation: str
    done: bool
    next_question: Optional[MCQQuestionPublic] = None
    question_number: int
    total_questions: int


class QuestionResult(BaseModel):
    question_id: str
    question: str
    options: list[str]
    selected_answer: str
    correct_answer: str
    correct: bool
    explanation: str
    topic: str
    difficulty: str
    time_ms: int


class AssessmentResultsResponse(BaseModel):
    skill_category: str
    topic: str
    difficulty: str
    experience_level: str
    assessment_type: str
    accuracy_percent: float
    correct_count: int
    total_questions: int
    total_time_ms: int
    avg_time_ms: float
    questions: list[QuestionResult]


class TopicBreakdown(BaseModel):
    topic: str
    accuracy: float
    correct: int
    total: int


class FeedbackResponse(BaseModel):
    summary: str
    strengths: list[str]
    improvements: list[str]
    topic_breakdown: list[TopicBreakdown]


class HealthResponse(BaseModel):
    status: str
    gemini_configured: bool


class AnswerRecord(BaseModel):
    question_id: str
    selected: str
    correct: bool
    time_ms: int


class SessionState(BaseModel):
    config: AssessmentConfig
    questions: list[MCQQuestion]
    answers: list[AnswerRecord] = []
    started_at: datetime
    current_index: int = 0
    feedback: Optional[FeedbackResponse] = None
