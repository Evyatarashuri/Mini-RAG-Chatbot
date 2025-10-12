from fastapi import APIRouter, Request
from app.services import embedding_service
from app.db.faiss_store import faiss_store
from app.db.redis import redis_client
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/api/query", tags=["api-query"])

@router.post("/")
async def query_api(request: Request, payload: dict):

    logger.info(f"Received query payload: {payload}")

    user = getattr(request.state, "user", None)
    if not user:
        logger.warning("Unauthorized query attempt") # FAILED HERE TO REMEMBER
        return {"error": "Unauthorized"}, 401

    question = payload.get("question")
    if not question:
        return {"error": "Missing question"}, 400

    cache_key = f"answer:{str(user['_id'])}:{question}"
    cached = redis_client.get(cache_key)
    if cached:
        return {"question": question, "answer": cached, "cached": True}

    query_emb = embedding_service.create_embedding(question)
    results = faiss_store.search(query_emb, top_k=5)
    if not results:
        return {"error": "No relevant context found"}, 404

    context = "\n".join([r[0]["chunk"] for r in results])

    prompt = f"""
    Answer the question based only on the context below.
    If the answer is not contained within the context, say 'I don't know.'

    Context:
    {context}

    Question:
    {question}
    """

    answer = embedding_service.ask_openai(prompt)
    redis_client.setex(cache_key, settings.REDIS_CACHE_TTL, answer)

    return {"question": question, "answer": answer, "cached": False}
