from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class SaveHistoryRequest(BaseModel):
    session_id: str


class HistorySummary(BaseModel):
    id: str
    skill_category: str
    topic: str
    difficulty: str
    accuracy_percent: float
    correct_count: int
    total_questions: int
    completed_at: str


class HistoryDetail(HistorySummary):
    experience_level: str
    assessment_type: str
    results: dict
    feedback: dict | None = None


class ReportsSummary(BaseModel):
    total_tests: int
    average_score: float
    best_score: float
    recent_tests: list[HistorySummary]
