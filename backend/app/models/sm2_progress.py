import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Float, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.guid import GUID


class UserCardProgress(Base):
    __tablename__ = "user_card_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "flashcard_id", name="uq_user_flashcard"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    flashcard_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("flashcards.id"), nullable=False, index=True)

    # SM-2 state
    repetition_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    easiness_factor: Mapped[float] = mapped_column(Float, nullable=False, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Schedule
    next_review_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    last_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quality_last: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-5

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="card_progress")
    flashcard = relationship("Flashcard", back_populates="progress_records")
