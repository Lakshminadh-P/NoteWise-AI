import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.tasks.process_document import process_document_task

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF document for processing."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted")

    settings = get_settings()
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file with unique name
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}.pdf"
    content = await file.read()
    file_path.write_bytes(content)

    # Create DB record
    document = Document(
        user_id=current_user.id,
        title=file.filename.rsplit(".", 1)[0],
        file_path=str(file_path),
        status="pending",
    )
    db.add(document)
    await db.flush()

    # Kick off background processing
    background_tasks.add_task(process_document_task, str(document.id))

    return DocumentResponse(
        id=str(document.id),
        title=document.title,
        status=document.status,
        page_count=None,
        uploaded_at=document.uploaded_at,
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all documents for the current user."""
    result = await db.execute(
        select(Document).where(Document.user_id == current_user.id).order_by(Document.uploaded_at.desc())
    )
    docs = result.scalars().all()
    return [
        DocumentResponse(
            id=str(d.id), title=d.title, status=d.status,
            page_count=d.page_count, uploaded_at=d.uploaded_at,
        )
        for d in docs
    ]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get document details with flashcard and quiz counts."""
    result = await db.execute(
        select(Document).where(Document.id == uuid.UUID(document_id), Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    fc_count = await db.scalar(select(func.count()).where(Flashcard.document_id == doc.id))
    qz_count = await db.scalar(select(func.count()).where(Quiz.document_id == doc.id))

    return DocumentDetailResponse(
        id=str(doc.id), title=doc.title, status=doc.status,
        page_count=doc.page_count, uploaded_at=doc.uploaded_at,
        flashcard_count=fc_count or 0, quiz_count=qz_count or 0,
    )


@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Poll processing status for a document."""
    result = await db.execute(
        select(Document).where(Document.id == uuid.UUID(document_id), Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return {"status": doc.status, "error_message": doc.error_message}
