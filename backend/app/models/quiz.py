import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.guid import GUID


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("documents.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    quiz_type: Mapped[str] = mapped_column(String(20), nullable=False, default="mixed")  # mcq | free_text | mixed
    question_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("Document", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    sessions = relationship("QuizSession", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("quizzes.id"), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    reference_answer: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {"A": "...", "B": "...", ...} for MCQ
    correct_option: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "A", "B", etc.
    question_type: Mapped[str] = mapped_column(String(20), nullable=False, default="free_text")  # mcq | free_text
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False, default=3)  # 1-5

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    attempts = relationship("QuizAttempt", back_populates="question", cascade="all, delete-orphan")


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    quiz_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("quizzes.id"), nullable=False, index=True)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    quiz = relationship("Quiz", back_populates="sessions")
    attempts = relationship("QuizAttempt", back_populates="session", cascade="all, delete-orphan")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("quiz_sessions.id"), nullable=False, index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("quiz_questions.id"), nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # 0.0 - 5.0
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("QuizSession", back_populates="attempts")
    question = relationship("QuizQuestion", back_populates="attempts")
