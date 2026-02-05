"""
RAG Query API.
- Check Redis cache for same query; return cached result if hit.
- Otherwise: LlamaIndex RAG pipeline → vector search (ChromaDB) → generate answer.
- Cache result in Redis, return to client.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# TODO: from app.api.auth import get_current_user
# TODO: from app.utils.rag import run_rag_query
# TODO: from app.utils.cache import get_cached_response, set_cached_response

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]  # or list of doc refs


@router.post("/", response_model=QueryResponse)
async def query(
    body: QueryRequest,
    # current_user = Depends(get_current_user),
):
    """
    1. cache_key = hash(body.query)
    2. cached = get_cached_response(cache_key)
    3. if cached: return cached
    4. result = run_rag_query(body.query)  # LlamaIndex + ChromaDB
    5. set_cached_response(cache_key, result)
    6. return result
    """
    return QueryResponse(
        answer="Implement: cache lookup, LlamaIndex RAG, then cache and return",
        sources=[],
    )
