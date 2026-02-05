"""
AI Knowledge API - Main entry point.
FastAPI app with JWT auth, document ingestion, and RAG query endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# TODO: Import your API routers when ready
# from app.api import upload, query
# from app.api.auth import router as auth_router

app = FastAPI(
    title="AI Knowledge API",
    description="RAG-powered document search and summarization",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Include routers
# app.include_router(auth_router, prefix="/auth", tags=["auth"])
# app.include_router(upload.router, prefix="/documents", tags=["documents"])
# app.include_router(query.router, prefix="/query", tags=["query"])


@app.get("/health")
def health():
    return {"status": "ok"}
