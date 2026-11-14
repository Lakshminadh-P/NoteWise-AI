import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.guid import GUID


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending | processing | ready | error
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="documents")
    flashcards = relationship("Flashcard", back_populates="document", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="document", cascade="all, delete-orphan")
