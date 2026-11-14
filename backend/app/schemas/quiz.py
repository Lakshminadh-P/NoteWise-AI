from datetime import datetime
from pydantic import BaseModel


class QuizResponse(BaseModel):
    id: str
    title: str
    quiz_type: str
    question_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QuizQuestionResponse(BaseModel):
    id: str
    question_text: str
    question_type: str
    options: dict | None
    difficulty: int

    model_config = {"from_attributes": True}


class AnswerSubmission(BaseModel):
    question_id: str
    user_answer: str


class QuizSubmission(BaseModel):
    answers: list[AnswerSubmission]


class AttemptResult(BaseModel):
    question_id: str
    score: float
    ai_feedback: str | None
    correct_answer: str


class QuizResult(BaseModel):
    session_id: str
    total_score: float
    total_questions: int
    percentage: float
    results: list[AttemptResult]
