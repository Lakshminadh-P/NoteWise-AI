import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.flashcard import Flashcard
from app.models.document import Document
from app.models.sm2_progress import UserCardProgress
from app.schemas.flashcard import FlashcardResponse, FlashcardReview, FlashcardDue
from app.services.sm2_engine import SM2State, sm2_update

router = APIRouter()


@router.get("", response_model=list[FlashcardResponse])
async def list_flashcards(
    doc_id: str | None = Query(None, description="Filter by document ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List flashcards, optionally filtered by document."""
    query = (
        select(Flashcard)
        .join(Document, Flashcard.document_id == Document.id)
        .where(Document.user_id == current_user.id)
    )
    if doc_id:
        query = query.where(Flashcard.document_id == uuid.UUID(doc_id))

    result = await db.execute(query.order_by(Flashcard.created_at.desc()))
    cards = result.scalars().all()

    return [
        FlashcardResponse(
            id=str(c.id), front=c.front, back=c.back,
            topic_tag=c.topic_tag, source_page=c.source_page,
        )
        for c in cards
    ]


@router.get("/due", response_model=list[FlashcardDue])
async def get_due_flashcards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all flashcards due for review today or earlier."""
    today = date.today()

    # Cards with existing progress that are due
    result = await db.execute(
        select(Flashcard, UserCardProgress)
        .join(UserCardProgress, UserCardProgress.flashcard_id == Flashcard.id)
        .join(Document, Flashcard.document_id == Document.id)
        .where(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.next_review_date <= today,
            Document.user_id == current_user.id,
        )
        .order_by(UserCardProgress.next_review_date)
    )
    due_with_progress = result.all()

    # Cards with no progress yet (never reviewed) — also due
    result2 = await db.execute(
        select(Flashcard)
        .join(Document, Flashcard.document_id == Document.id)
        .outerjoin(
            UserCardProgress,
            (UserCardProgress.flashcard_id == Flashcard.id) & (UserCardProgress.user_id == current_user.id),
        )
        .where(Document.user_id == current_user.id, UserCardProgress.id.is_(None))
    )
    new_cards = result2.scalars().all()

    items = []
    for card, progress in due_with_progress:
        items.append(FlashcardDue(
            id=str(card.id), front=card.front, back=card.back,
            topic_tag=card.topic_tag, next_review_date=progress.next_review_date,
            repetition_number=progress.repetition_number, easiness_factor=progress.easiness_factor,
        ))
    for card in new_cards:
        items.append(FlashcardDue(
            id=str(card.id), front=card.front, back=card.back,
            topic_tag=card.topic_tag, next_review_date=today,
            repetition_number=0, easiness_factor=2.5,
        ))

    return items


@router.post("/{flashcard_id}/review")
async def review_flashcard(
    flashcard_id: str,
    review: FlashcardReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a review quality score for a flashcard. Updates SM-2 state."""
    if not 0 <= review.quality <= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quality must be between 0 and 5")

    card_uuid = uuid.UUID(flashcard_id)

    # Verify card belongs to user
    card_result = await db.execute(
        select(Flashcard)
        .join(Document, Flashcard.document_id == Document.id)
        .where(Flashcard.id == card_uuid, Document.user_id == current_user.id)
    )
    if not card_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")

    # Get or create progress record
    result = await db.execute(
        select(UserCardProgress).where(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.flashcard_id == card_uuid,
        )
    )
    progress = result.scalar_one_or_none()

    if progress:
        current_state = SM2State(
            repetition_number=progress.repetition_number,
            easiness_factor=progress.easiness_factor,
            interval_days=progress.interval_days,
        )
    else:
        current_state = SM2State()
        progress = UserCardProgress(user_id=current_user.id, flashcard_id=card_uuid)
        db.add(progress)

    # Run SM-2 algorithm
    new_state = sm2_update(current_state, review.quality)

    # Persist
    progress.repetition_number = new_state.repetition_number
    progress.easiness_factor = new_state.easiness_factor
    progress.interval_days = new_state.interval_days
    progress.next_review_date = new_state.next_review_date
    progress.last_review_date = date.today()
    progress.quality_last = review.quality

    return {
        "message": "Review recorded",
        "next_review_date": str(new_state.next_review_date),
        "interval_days": new_state.interval_days,
        "easiness_factor": new_state.easiness_factor,
        "repetition_number": new_state.repetition_number,
    }
