import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any




from groq import Groq




import chromadb
import redis
from jose import jwt
from passlib.context import CryptContext
from pypdf import PdfReader




from app.config import get_settings




settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")








def hash_password(password: str) -> str:
    return pwd_context.hash(password)








def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)








def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.algorithm)








def create_refresh_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.refresh_token_expire_minutes)
    )
    payload = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(payload, settings.jwt_refresh_secret_key, algorithm=settings.algorithm)








def _redis_client() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)








def cache_key_for_query(query: str, user_id: int) -> str:
    digest = hashlib.sha256(f"{user_id}:{query.strip().lower()}".encode()).hexdigest()
    return f"rag:query:{digest}"








def get_cached_response(key: str) -> dict[str, Any] | None:
    try:
        client = _redis_client()
        raw = client.get(key)
        return json.loads(raw) if raw else None
    except redis.RedisError:
        return None








def set_cached_response(key: str, value: dict[str, Any], ttl: int | None = None) -> None:
    try:
        client = _redis_client()
        client.setex(key, ttl or settings.cache_ttl_seconds, json.dumps(value))
    except redis.RedisError:
        pass








def get_chroma_collection():
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return client.get_or_create_collection(name=settings.chroma_collection)








def extract_text_from_file(file_path: str) -> str:
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")








def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks








def index_document_in_chroma(document_id: int, filename: str, text: str) -> str:
    collection = get_chroma_collection()
    chroma_doc_id = f"doc-{document_id}"
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No text could be extracted from the document")




    collection.upsert(
        ids=[f"{chroma_doc_id}-{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[{"document_id": document_id, "filename": filename, "chunk": i} for i in range(len(chunks))],
    )
    return chroma_doc_id








def run_rag_query(query: str, user_id: int) -> dict[str, Any]:
    if settings.rag_mock or os.getenv("RAG_MOCK", "").lower() in ("1", "true", "yes"):
        return {
            "answer": (
                f"Based on your knowledge base, here is a concise summary related to "
                f"\"{query}\". (Enable full RAG by running with ChromaDB and uploaded documents.)"
            ),
            "sources": ["mock-document.pdf"],
        }
    else:












        try:
            collection = get_chroma_collection()
            results = collection.query(query_texts=[query], n_results=3)
        except Exception:
            return {
                "answer": "No indexed documents available yet. Upload a PDF or text file first.",
                "sources": [],
            }




        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]
        if not documents[0]:
            return {"answer": "No relevant passages found in your documents.", "sources": []}




        passages = documents[0]
        sources = list({m.get("filename", "unknown") for m in metadatas[0] if m})




        #Call LLM to summarize the passages and provide a concise answer
        from groq import Groq




        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )




        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Based on the knowledge base, respond to the query '{query}', knowledge base: {passages}",
                }
            ],
            model=os.getenv("GROQ_MODEL", ""),
        )




        return {
                "answer": (
                    chat_completion.choices[0].message.content
                ),
                "sources": sources,
            }
   





