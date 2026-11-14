import uuid
from datetime import datetime, date, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.quiz import Quiz, QuizQuestion, QuizSession, QuizAttempt
from app.models.flashcard import Flashcard
from app.models.sm2_progress import UserCardProgress
from app.schemas.quiz import QuizResponse, QuizQuestionResponse, QuizSubmission, QuizResult, AttemptResult
from app.services.ai_grader import grade_free_text
from app.services.sm2_engine import SM2State, sm2_update, score_to_quality

router = APIRouter()


@router.get("", response_model=list[QuizResponse])
async def list_quizzes(
    doc_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List quizzes, optionally filtered by document."""
    query = (
        select(Quiz)
        .join(Document, Quiz.document_id == Document.id)
        .where(Document.user_id == current_user.id)
    )
    if doc_id:
        query = query.where(Quiz.document_id == uuid.UUID(doc_id))

    result = await db.execute(query.order_by(Quiz.created_at.desc()))
    quizzes = result.scalars().all()

    return [
        QuizResponse(
            id=str(q.id), title=q.title, quiz_type=q.quiz_type,
            question_count=q.question_count, created_at=q.created_at,
        )
        for q in quizzes
    ]


@router.post("/{quiz_id}/start")
async def start_quiz(
    quiz_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a quiz session. Returns session ID and questions."""
    quiz_uuid = uuid.UUID(quiz_id)

    # Verify quiz belongs to user
    result = await db.execute(
        select(Quiz)
        .join(Document, Quiz.document_id == Document.id)
        .where(Quiz.id == quiz_uuid, Document.user_id == current_user.id)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    # Create session
    session = QuizSession(user_id=current_user.id, quiz_id=quiz_uuid, total_questions=quiz.question_count)
    db.add(session)
    await db.flush()

    # Get questions
    q_result = await db.execute(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_uuid))
    questions = q_result.scalars().all()

    return {
        "session_id": str(session.id),
        "quiz_title": quiz.title,
        "questions": [
            QuizQuestionResponse(
                id=str(q.id), question_text=q.question_text,
                question_type=q.question_type, options=q.options, difficulty=q.difficulty,
            )
            for q in questions
        ],
    }


@router.post("/sessions/{session_id}/submit", response_model=QuizResult)
async def submit_quiz(
    session_id: str,
    submission: QuizSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit quiz answers for grading. Triggers AI grading + SM-2 updates."""
    session_uuid = uuid.UUID(session_id)

    # Verify session
    result = await db.execute(
        select(QuizSession).where(QuizSession.id == session_uuid, QuizSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz session not found")
    if session.completed_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already completed")

    results = []
    total_score = 0.0

    for answer in submission.answers:
        q_result = await db.execute(
            select(QuizQuestion).where(QuizQuestion.id == uuid.UUID(answer.question_id))
        )
        question = q_result.scalar_one_or_none()
        if not question:
            continue

        # Grade the answer
        if question.question_type == "mcq":
            is_correct = answer.user_answer.strip().upper() == (question.correct_option or "").strip().upper()
            score = 5.0 if is_correct else 0.0
            feedback = "Correct!" if is_correct else f"Incorrect. The correct answer is {question.correct_option}."
        else:
            grading = await grade_free_text(question.question_text, question.reference_answer, answer.user_answer)
            score = grading["score"]
            feedback = grading["feedback"]

        # Save attempt
        attempt = QuizAttempt(
            session_id=session_uuid,
            question_id=question.id,
            user_answer=answer.user_answer,
            score=score,
            ai_feedback=feedback,
        )
        db.add(attempt)
        total_score += score

        results.append(AttemptResult(
            question_id=str(question.id),
            score=score,
            ai_feedback=feedback,
            correct_answer=question.reference_answer,
        ))

    # Finalize session
    session.total_score = total_score
    session.completed_at = datetime.now(timezone.utc)

    # ── SM-2 Update ──
    # Find flashcards linked to this quiz's document and update progress
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == session.quiz_id))
    quiz = quiz_result.scalar_one_or_none()
    if quiz:
        fc_result = await db.execute(
            select(Flashcard).where(Flashcard.document_id == quiz.document_id)
        )
        flashcards = fc_result.scalars().all()

        avg_quality = score_to_quality(total_score / max(len(submission.answers), 1))

        for card in flashcards:
            prog_result = await db.execute(
                select(UserCardProgress).where(
                    UserCardProgress.user_id == current_user.id,
                    UserCardProgress.flashcard_id == card.id,
                )
            )
            progress = prog_result.scalar_one_or_none()

            if progress:
                state = SM2State(
                    repetition_number=progress.repetition_number,
                    easiness_factor=progress.easiness_factor,
                    interval_days=progress.interval_days,
                )
            else:
                state = SM2State()
                progress = UserCardProgress(user_id=current_user.id, flashcard_id=card.id)
                db.add(progress)

            new_state = sm2_update(state, avg_quality)
            progress.repetition_number = new_state.repetition_number
            progress.easiness_factor = new_state.easiness_factor
            progress.interval_days = new_state.interval_days
            progress.next_review_date = new_state.next_review_date
            progress.last_review_date = date.today()
            progress.quality_last = avg_quality

    total_questions = len(submission.answers)
    percentage = (total_score / (total_questions * 5) * 100) if total_questions > 0 else 0

    return QuizResult(
        session_id=str(session.id),
        total_score=total_score,
        total_questions=total_questions,
        percentage=round(percentage, 1),
        results=results,
    )
