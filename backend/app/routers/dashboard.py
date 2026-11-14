from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import QuizSession
from app.models.sm2_progress import UserCardProgress
from app.schemas.dashboard import DashboardStats, ScheduleItem, MasteryByTopic

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get aggregated learning statistics for the dashboard."""
    user_id = current_user.id
    today = date.today()

    total_docs = await db.scalar(
        select(func.count()).select_from(Document).where(Document.user_id == user_id)
    ) or 0

    total_cards = await db.scalar(
        select(func.count())
        .select_from(Flashcard)
        .join(Document, Flashcard.document_id == Document.id)
        .where(Document.user_id == user_id)
    ) or 0

    cards_due = await db.scalar(
        select(func.count())
        .select_from(UserCardProgress)
        .where(UserCardProgress.user_id == user_id, UserCardProgress.next_review_date <= today)
    ) or 0

    cards_mastered = await db.scalar(
        select(func.count())
        .select_from(UserCardProgress)
        .where(UserCardProgress.user_id == user_id, UserCardProgress.repetition_number >= 5)
    ) or 0

    avg_ef = await db.scalar(
        select(func.avg(UserCardProgress.easiness_factor))
        .where(UserCardProgress.user_id == user_id)
    ) or 2.5

    total_quizzes = await db.scalar(
        select(func.count())
        .select_from(QuizSession)
        .where(QuizSession.user_id == user_id, QuizSession.completed_at.isnot(None))
    ) or 0

    avg_score = await db.scalar(
        select(func.avg(QuizSession.total_score))
        .where(QuizSession.user_id == user_id, QuizSession.completed_at.isnot(None))
    ) or 0.0

    return DashboardStats(
        total_documents=total_docs,
        total_flashcards=total_cards,
        cards_due_today=cards_due,
        cards_mastered=cards_mastered,
        average_easiness=round(float(avg_ef), 2),
        total_quizzes_taken=total_quizzes,
        average_quiz_score=round(float(avg_score), 1),
    )


@router.get("/schedule", response_model=list[ScheduleItem])
async def get_review_schedule(
    days: int = 14,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get upcoming review schedule for the next N days."""
    end_date = date.today() + timedelta(days=days)

    result = await db.execute(
        select(Flashcard, UserCardProgress)
        .join(UserCardProgress, UserCardProgress.flashcard_id == Flashcard.id)
        .where(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.next_review_date <= end_date,
        )
        .order_by(UserCardProgress.next_review_date)
    )

    items = []
    for card, progress in result.all():
        items.append(ScheduleItem(
            flashcard_id=str(card.id),
            front=card.front,
            topic_tag=card.topic_tag,
            next_review_date=progress.next_review_date,
            repetition_number=progress.repetition_number,
            easiness_factor=progress.easiness_factor,
        ))

    return items


@router.get("/mastery", response_model=list[MasteryByTopic])
async def get_mastery_by_topic(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get mastery breakdown grouped by topic."""
    result = await db.execute(
        select(Flashcard, UserCardProgress)
        .join(Document, Flashcard.document_id == Document.id)
        .outerjoin(
            UserCardProgress,
            (UserCardProgress.flashcard_id == Flashcard.id) & (UserCardProgress.user_id == current_user.id),
        )
        .where(Document.user_id == current_user.id)
    )

    topic_data: dict[str, dict] = {}
    for card, progress in result.all():
        topic = card.topic_tag or "Uncategorized"
        if topic not in topic_data:
            topic_data[topic] = {"total": 0, "mastered": 0, "learning": 0, "new": 0}

        topic_data[topic]["total"] += 1
        if progress is None:
            topic_data[topic]["new"] += 1
        elif progress.repetition_number >= 5:
            topic_data[topic]["mastered"] += 1
        else:
            topic_data[topic]["learning"] += 1

    return [
        MasteryByTopic(
            topic=topic,
            total_cards=data["total"],
            mastered=data["mastered"],
            learning=data["learning"],
            new=data["new"],
            mastery_percent=round(data["mastered"] / data["total"] * 100, 1) if data["total"] > 0 else 0,
        )
        for topic, data in sorted(topic_data.items())
    ]
