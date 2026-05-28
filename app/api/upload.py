import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user
from app.models import Document, DocumentStatus, User
from app.schemas.document_schemas import DocumentResponse, DocumentUploadResponse
from app.tasks import process_document_embeddings

router = APIRouter()
settings = get_settings()
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF or .txt files are allowed",
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex}{suffix}"
    file_path = upload_dir / safe_name
    content = await file.read()
    file_path.write_bytes(content)

    document = Document(
        user_id=current_user.id,
        filename=file.filename or safe_name,
        file_path=str(file_path),
        status=DocumentStatus.PENDING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    process_document_embeddings.delay(document.id)

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        message="Document queued for embedding. Poll GET /documents/{id} for status.",
    )


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return docs


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
