from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    title: str
    status: str
    page_count: int | None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetailResponse(DocumentResponse):
    flashcard_count: int = 0
    quiz_count: int = 0
