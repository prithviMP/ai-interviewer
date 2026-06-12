from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_db
from dependencies import get_current_user
from models.assessment import (
    AssessmentConfig,
    AssessmentResultsResponse,
    FeedbackResponse,
    GenerateAssessmentRequest,
    GenerateAssessmentResponse,
    HealthResponse,
    StartAssessmentRequest,
    StartAssessmentResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from models.auth import (
    AuthResponse,
    HistoryDetail,
    HistorySummary,
    LoginRequest,
    ReportsSummary,
    SaveHistoryRequest,
    SignUpRequest,
    UserResponse,
)
from services.assessment_service import AssessmentService
from services.auth_service import AuthService
from services.cache_service import CacheService
from services.gemini_service import GeminiService
from services.history_service import HistoryService
from services.mcq_evaluator import MCQEvaluator
from services.question_generator import QuestionGenerator

settings = get_settings()
cache_service = CacheService(ttl_seconds=settings.cache_ttl_seconds)
gemini_service = GeminiService()
question_generator = QuestionGenerator(gemini_service, cache_service)
assessment_service = AssessmentService(question_generator, MCQEvaluator(), gemini_service)
auth_service = AuthService()
history_service = HistoryService(assessment_service)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Assessment Platform API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", gemini_configured=gemini_service.is_configured)


# --- Auth ---

@app.post("/auth/signup", response_model=AuthResponse)
def signup(payload: SignUpRequest) -> AuthResponse:
    return auth_service.signup(payload)


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    return auth_service.login(payload)


@app.get("/auth/me", response_model=UserResponse)
def me(user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return user


# --- Assessments ---

@app.post("/assessments/generate", response_model=GenerateAssessmentResponse)
def generate_assessment(
    payload: GenerateAssessmentRequest,
    user: UserResponse = Depends(get_current_user),
) -> GenerateAssessmentResponse:
    del user
    config = AssessmentConfig(
        skill_category=payload.skill_category,
        topic=payload.topic,
        difficulty=payload.difficulty,
        experience_level=payload.experience_level,
        assessment_type=payload.assessment_type,
        learning_objectives=payload.learning_objectives,
        question_count=payload.question_count,
    )
    return assessment_service.generate_assessment(
        config, skip_cache=payload.skip_cache, cache_key=payload.cache_key
    )


@app.post("/assessments/start", response_model=StartAssessmentResponse)
def start_assessment(
    payload: StartAssessmentRequest,
    user: UserResponse = Depends(get_current_user),
) -> StartAssessmentResponse:
    del user
    if payload.cache_key:
        return assessment_service.start_from_cache(payload.config, payload.cache_key)
    result = assessment_service.generate_assessment(payload.config)
    return StartAssessmentResponse(
        session_id=result.session_id,
        cache_key=result.cache_key,
        question=result.questions[0],
        question_number=1,
        total_questions=result.total_questions,
    )


@app.post("/assessments/{session_id}/answer", response_model=SubmitAnswerResponse)
def submit_answer(
    session_id: str,
    payload: SubmitAnswerRequest,
    user: UserResponse = Depends(get_current_user),
) -> SubmitAnswerResponse:
    del user
    return assessment_service.submit_answer(session_id, payload.selected_answer, payload.time_ms)


@app.get("/assessments/{session_id}/results", response_model=AssessmentResultsResponse)
def get_results(
    session_id: str,
    user: UserResponse = Depends(get_current_user),
) -> AssessmentResultsResponse:
    del user
    return assessment_service.get_results(session_id)


@app.post("/assessments/{session_id}/feedback", response_model=FeedbackResponse)
def get_feedback(
    session_id: str,
    user: UserResponse = Depends(get_current_user),
) -> FeedbackResponse:
    del user
    return assessment_service.generate_feedback(session_id)


# --- History & Reports ---

@app.post("/history", response_model=HistorySummary)
def save_history(
    payload: SaveHistoryRequest,
    user: UserResponse = Depends(get_current_user),
) -> HistorySummary:
    return history_service.save_from_session(user.id, payload.session_id)


@app.get("/history", response_model=list[HistorySummary])
def list_history(user: UserResponse = Depends(get_current_user)) -> list[HistorySummary]:
    return history_service.list_for_user(user.id)


@app.get("/history/{history_id}", response_model=HistoryDetail)
def get_history_detail(
    history_id: str,
    user: UserResponse = Depends(get_current_user),
) -> HistoryDetail:
    return history_service.get_detail(user.id, history_id)


@app.get("/reports", response_model=ReportsSummary)
def get_reports(user: UserResponse = Depends(get_current_user)) -> ReportsSummary:
    return history_service.get_reports(user.id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
