import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    topic_tag: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("Document", back_populates="flashcards")
    progress_records = relationship("UserCardProgress", back_populates="flashcard", cascade="all, delete-orphan")
