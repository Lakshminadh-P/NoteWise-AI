"""
Background task: Parse PDF, generate flashcards and quizzes using AI.
"""

import asyncio
import uuid
import traceback

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz, QuizQuestion
from app.services.pdf_parser import extract_text_from_pdf, chunk_text
from app.services.ai_generator import generate_flashcards, generate_quiz_questions


def process_document_task(document_id: str):
    """Entry point for the background task (sync wrapper for async logic)."""
    asyncio.run(_process_document(document_id))


async def _process_document(document_id: str):
    """Parse the PDF and generate study materials."""
    async with async_session() as db:
        try:
            # Load document
            result = await db.execute(select(Document).where(Document.id == uuid.UUID(document_id)))
            doc = result.scalar_one_or_none()
            if not doc:
                return

            # Mark as processing
            doc.status = "processing"
            await db.commit()

            # Step 1: Extract text from PDF
            raw_text, page_count = extract_text_from_pdf(doc.file_path)
            doc.raw_text = raw_text
            doc.page_count = page_count
            await db.commit()

            # Step 2: Chunk text for LLM processing
            chunks = chunk_text(raw_text)

            # Step 3: Generate flashcards from each chunk
            for i, chunk in enumerate(chunks):
                cards = await generate_flashcards(chunk, topic_hint=doc.title)
                for card_data in cards:
                    flashcard = Flashcard(
                        document_id=doc.id,
                        front=card_data.get("front", ""),
                        back=card_data.get("back", ""),
                        topic_tag=card_data.get("topic_tag"),
                        source_page=i + 1,
                    )
                    db.add(flashcard)

            # Step 4: Generate quiz questions from each chunk
            quiz = Quiz(
                document_id=doc.id,
                title=f"Quiz: {doc.title}",
                quiz_type="mixed",
                question_count=0,
            )
            db.add(quiz)
            await db.flush()

            question_count = 0
            for chunk in chunks:
                questions = await generate_quiz_questions(chunk, num_questions=5)
                for q_data in questions:
                    question = QuizQuestion(
                        quiz_id=quiz.id,
                        question_text=q_data.get("question_text", ""),
                        reference_answer=q_data.get("reference_answer", ""),
                        options=q_data.get("options"),
                        correct_option=q_data.get("correct_option"),
                        question_type=q_data.get("question_type", "free_text"),
                        difficulty=q_data.get("difficulty", 3),
                    )
                    db.add(question)
                    question_count += 1

            quiz.question_count = question_count

            # Mark as ready
            doc.status = "ready"
            await db.commit()

        except Exception as e:
            doc.status = "error"
            doc.error_message = str(e)
            await db.commit()
            traceback.print_exc()
