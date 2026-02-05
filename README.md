# AI Knowledge API (RAG + FastAPI + Async)

Skeleton for a RAG-powered API: document ingestion, background embeddings (Celery + Redis), and cached query API.

## Tech stack

- **Python 3.11+**, **FastAPI**
- **PostgreSQL** (relational), **ChromaDB** (vectors)
- **Redis** + **Celery** (background embedding tasks + query cache)
- **LlamaIndex** (RAG pipeline)
- **Docker** + **docker-compose**

## What’s in the skeleton

- `app/main.py` – FastAPI app; wire in routers and CORS.
- `app/api/upload.py` – Upload PDF/text → DB record → enqueue Celery task.
- `app/api/query.py` – Query → cache check (Redis) → RAG (LlamaIndex + ChromaDB) → cache and return.
- `app/models.py` – Define User and Document models (DB).
- `app/tasks.py` – Celery task: load document, embed with LlamaIndex, write to ChromaDB, update document status.
- `app/utils.py` – RAG helpers and Redis get/set for cache.
- `requirements.txt`, `Dockerfile`, `docker-compose.yml` – Dependencies and run environment.

## What you need to implement

1. **Auth**: JWT login/register and `get_current_user` dependency; protect upload and query routes.
2. **Models & DB**: Implement User and Document in `models.py`, run migrations.
3. **Upload**: File validation, save file, insert Document, call `process_document_embeddings.delay(doc_id)`.
4. **Tasks**: In `tasks.py`, implement `process_document_embeddings`: read file, chunk, embed (LlamaIndex), index in ChromaDB, set status to `ready`.
5. **RAG & cache**: In `utils.py`, implement `run_rag_query` (LlamaIndex + ChromaDB) and Redis cache get/set; use them in `query.py`.

## Tests and CI

- **Run tests locally:** `pip install -r requirements.txt` then `pytest -v`
- **GitHub Actions:** `.github/workflows/ci.yml` runs tests on push/PR to `main` or `master`. Add the workflow to your repo to get checks on every push.

## Run locally

```bash
# With Docker
docker-compose up -d
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## GitHub / presentation

- Commit regularly (e.g. 3 commits/day).
- Add README screenshots of API responses and link to OpenAPI/Swagger.
- Optional: deploy on Railway/Heroku and add the live URL to the README.
