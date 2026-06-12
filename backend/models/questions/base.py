from pydantic import BaseModel, Field


class BaseQuestion(BaseModel):
    type: str
    id: str
    topic: str
    difficulty: str = Field(..., pattern="^(Easy|Medium|Hard)$")
