from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services import embedding_service
from app.db.faiss_store import faiss_store
from app.db.redis import redis_client
from app.core.config import settings
from pathlib import Path
from typing import Optional

# --- Configuration for LLM Cost Control ---
LLM_LIMIT_COUNT = 5     # Only allow 5 expensive LLM calls
LLM_LIMIT_WINDOW = 60   # Per 60 seconds

# --- Initialization ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter(prefix="/query", tags=["query"])

# --- Helper Functions ---

def get_current_user_id(request: Request) -> Optional[str]:
    """Extracts the authenticated user ID from the request state."""
    user = getattr(request.state, "user", None)
    if user and user.get("_id"):
        return str(user["_id"])
    return None

def check_llm_rate_limit(user_id: str):
    """
    Enforces a strict rate limit specifically for costly LLM operations (per user).
    Raises HTTPException 429 if the limit is exceeded.
    """
    key = f"llm_limit:user:{user_id}"
    
    count = redis_client.incr(key)
    
    if count == 1:
        redis_client.expire(key, LLM_LIMIT_WINDOW)

    if count > LLM_LIMIT_COUNT:
        raise HTTPException(
            status_code=429, 
            detail=f"LLM Generation rate limit exceeded. Max {LLM_LIMIT_COUNT} queries per minute."
        )

# --- Endpoints ---

@router.get("/", response_class=HTMLResponse)
async def query_form(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        return templates.TemplateResponse(
            "query.html", {"request": request, "user": "Not authenticated"}
        )
    
    return templates.TemplateResponse("query.html", {"request": request, "user": user})


@router.post("/", response_class=HTMLResponse)
async def query_post(request: Request, question: str = Form(...)):
    
    user_id = get_current_user_id(request)
    if not user_id:
        return templates.TemplateResponse(
            "query.html", {"request": request, "error": "Not authenticated"}
        )

    # --- 1. Caching Check (User-Specific) ---
    cache_key = f"answer:{user_id}:{question}"

    cached = redis_client.get(cache_key)
    if cached:
        # FIX: The cached object is already a string because the Redis client
        # is configured with decode_responses=True. Removed .decode('utf-8').
        answer = cached 
        return templates.TemplateResponse(
            "query.html",
            {
                "request": request,
                "question": question,
                "answer": answer,
                "cached": True,
            },
        )

    # --- 2. Cost Control Rate Limit ---
    # Apply the strict, cost-specific limit here, BEFORE retrieving data for the LLM
    try:
        check_llm_rate_limit(user_id)
    except HTTPException as e:
        # Catch and render the specific rate limit error
        return templates.TemplateResponse(
            "query.html",
            {"request": request, "error": e.detail, "question": question},
        )


    # --- 3. Retrieval (User-Isolated Search) ---
    # This step retrieves context but does not incur LLM cost.
    # Note: user_id is passed for mandatory filtering (security)
    query_emb = embedding_service.create_embedding(question)
    results = faiss_store.search(query_emb, user_id=user_id, top_k=5) 
    
    if not results:
        return templates.TemplateResponse(
            "query.html",
            {"request": request, "error": "No relevant context found in your documents."},
        )

    # --- 4. Context Construction & LLM Generation (The Costly Step) ---
    context = "\n".join([r[0]["chunk"] for r in results])

    prompt = f"""Answer the question based only on the context below.
If the answer is not contained within the context, say 'I don't know.'

Context:
{context}

Question:
{question}
"""
    try:
        answer = embedding_service.ask_openai(prompt)
    except Exception as e:
        return templates.TemplateResponse(
            "query.html",
            {"request": request, "error": f"LLM Generation failed: {str(e)}", "question": question},
        )


    # --- 5. Cache Result ---
    redis_client.setex(cache_key, settings.REDIS_CACHE_TTL, answer)

    return templates.TemplateResponse(
        "query.html",
        {
            "request": request,
            "question": question,
            "answer": answer,
            "cached": False,
        },
    )
