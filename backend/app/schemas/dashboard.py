from datetime import date
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_documents: int
    total_flashcards: int
    cards_due_today: int
    cards_mastered: int  # repetition_number >= 5
    average_easiness: float
    total_quizzes_taken: int
    average_quiz_score: float


class ScheduleItem(BaseModel):
    flashcard_id: str
    front: str
    topic_tag: str | None
    next_review_date: date
    repetition_number: int
    easiness_factor: float


class MasteryByTopic(BaseModel):
    topic: str
    total_cards: int
    mastered: int
    learning: int
    new: int
    mastery_percent: float
