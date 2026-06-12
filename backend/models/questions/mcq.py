from typing import Literal

from pydantic import Field, field_validator, model_validator

from models.questions.base import BaseQuestion


class MCQQuestion(BaseQuestion):
    type: Literal["mcq"] = "mcq"
    question: str
    options: list[str]
    correct_answer: str = Field(..., alias="correctAnswer")
    explanation: str

    model_config = {"populate_by_name": True}

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str]) -> list[str]:
        if len(value) != 4:
            raise ValueError("MCQ must have exactly 4 options")
        return value

    @model_validator(mode="after")
    def validate_correct_answer_in_options(self) -> "MCQQuestion":
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must be one of the options")
        return self

    def to_public(self) -> "MCQQuestionPublic":
        return MCQQuestionPublic(
            id=self.id,
            type=self.type,
            topic=self.topic,
            difficulty=self.difficulty,
            question=self.question,
            options=self.options,
        )


class MCQQuestionPublic(BaseQuestion):
    type: Literal["mcq"] = "mcq"
    question: str
    options: list[str]
