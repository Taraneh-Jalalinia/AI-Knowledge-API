"""
Document upload API.
- Accept PDF or text files.
- Enqueue background embedding task (Celery) after upload.
- Store document metadata in PostgreSQL/MySQL.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

# TODO: Add JWT dependency
# from app.api.auth import get_current_user

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    # current_user = Depends(get_current_user),
):
    """
    1. Validate file type (PDF or .txt).
    2. Save file temporarily or to object storage.
    3. Create document record in DB (status: pending).
    4. Enqueue Celery task: app.tasks.process_document_embeddings.delay(doc_id)
    5. Return doc_id and status.
    """
    # if not file.filename.endswith((".pdf", ".txt")):
    #     raise HTTPException(400, "Only PDF or text files allowed")
    # ... persist file, create DB record, enqueue task
    return {"message": "Upload endpoint - implement file validation, DB insert, Celery enqueue"}
