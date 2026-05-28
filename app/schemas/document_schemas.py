from datetime import datetime

from pydantic import BaseModel

from app.models import DocumentStatus


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    status: DocumentStatus
    message: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: DocumentStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    cached: bool = False
