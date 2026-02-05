"""
Celery tasks for background embedding generation.
Uses Redis as broker. Triggered after document upload.
"""
from celery import Celery

# TODO: Configure Celery with Redis URL from env
# app = Celery("knowledge_api", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

# @app.task(bind=True)
# def process_document_embeddings(self, document_id: int):
#     """
#     1. Load document from DB and file path.
#     2. Use LlamaIndex to chunk and create embeddings.
#     3. Store vectors in ChromaDB.
#     4. Update document status to 'ready' in DB.
#     """
#     pass
