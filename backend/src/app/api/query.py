from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services import embedding_service
from app.db.faiss_store import faiss_store
from app.db.redis import redis_client
from app.core.config import settings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/query", tags=["query"])


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

    user = getattr(request.state, "user", None)
    if not user:
        return templates.TemplateResponse(
            "query.html", {"request": request, "error": "Not authenticated"}
        )

    cache_key = f"answer:{str(user['_id'])}:{question}"

    cached = redis_client.get(cache_key)
    if cached:
        return templates.TemplateResponse(
            "query.html",
            {
                "request": request,
                "question": question,
                "answer": cached,
                "cached": True,
            },
        )

    query_emb = embedding_service.create_embedding(question)
    results = faiss_store.search(query_emb, top_k=5)
    if not results:
        return templates.TemplateResponse(
            "query.html",
            {"request": request, "error": "No relevant context found"},
        )

    context = "\n".join([r[0]["chunk"] for r in results])

    prompt = f"""Answer the question based only on the context below.
If the answer is not contained within the context, say 'I don't know.'

Context:
{context}

Question:
{question}
"""
    answer = embedding_service.ask_openai(prompt)

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
