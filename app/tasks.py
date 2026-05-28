import os

from celery import Celery
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import Document, DocumentStatus
from app.utils import extract_text_from_file, index_document_in_chroma

settings = get_settings()

celery_app = Celery(
    "knowledge_api",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

if os.getenv("CELERY_TASK_ALWAYS_EAGER", "").lower() in ("1", "true", "yes"):
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def process_document_embeddings(self, document_id: int) -> dict:
    db: Session = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {"status": "error", "detail": "Document not found"}

        document.status = DocumentStatus.PROCESSING
        db.commit()

        text = extract_text_from_file(document.file_path)
        chroma_id = index_document_in_chroma(document.id, document.filename, text)

        document.chroma_id = chroma_id
        document.status = DocumentStatus.READY
        document.error_message = None
        db.commit()
        return {"status": "ready", "document_id": document_id, "chroma_id": chroma_id}
    except Exception as exc:
        db.rollback()
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)[:500]
            db.commit()
        raise self.retry(exc=exc) from exc
    finally:
        db.close()
