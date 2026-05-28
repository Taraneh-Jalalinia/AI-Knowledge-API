from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.models import User
from app.schemas.document_schemas import QueryRequest, QueryResponse
from app.utils import cache_key_for_query, get_cached_response, run_rag_query, set_cached_response

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query(
    body: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    key = cache_key_for_query(body.query, current_user.id)
    cached = get_cached_response(key)
    if cached:
        return QueryResponse(answer=cached["answer"], sources=cached["sources"], cached=True)

    result = run_rag_query(body.query, current_user.id)
    set_cached_response(key, result)
    return QueryResponse(answer=result["answer"], sources=result["sources"], cached=False)
