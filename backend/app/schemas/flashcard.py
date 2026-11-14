from datetime import date
from pydantic import BaseModel


class FlashcardResponse(BaseModel):
    id: str
    front: str
    back: str
    topic_tag: str | None
    source_page: int | None

    model_config = {"from_attributes": True}


class FlashcardReview(BaseModel):
    quality: int  # 0-5


class FlashcardDue(BaseModel):
    id: str
    front: str
    back: str
    topic_tag: str | None
    next_review_date: date
    repetition_number: int
    easiness_factor: float
