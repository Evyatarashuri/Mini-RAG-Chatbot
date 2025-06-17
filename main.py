import os
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI, RateLimitError, OpenAIError
from contextlib import asynccontextmanager
from auth import router as auth_router, get_current_user, sessions
import embedding

# Jinja2 templates setup
templates = Jinja2Templates(directory="templates")

# Debug mode (default: False)
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Load OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key: # missing API key check
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")
client = OpenAI(api_key=openai_api_key)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to load PDFs and create embeddings at startup."""
    print("Loading PDFs and creating embeddings...")
    texts, sources = embedding.load_all_pdfs_from_folder("data")
    chunks_with_sources = embedding.prepare_chunks_and_sources(texts, sources)
    embedding.embed_and_store_chunks(chunks_with_sources)
    print(f"Loaded {len(chunks_with_sources)} chunks and created embeddings.")
    yield

# Create FastAPI app instance with lifespan
app = FastAPI(
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
    lifespan=lifespan
)

# Include the authentication router
app.include_router(auth_router)

# Middleware for authentication
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    ''' Check if the request path requires authentication'''

    path = request.url.path
    if path in ["/", "/ask"]:
        token = request.cookies.get("session_token")
        if not token or token not in sessions:
            return RedirectResponse(url="/login")
    response = await call_next(request)
    return response


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Render the home page with a form to ask questions."""
    return templates.TemplateResponse("ask.html", {"request": request})

# Endpoint to get the source of a document based on a question
@app.post("/source")
async def source(question: str = Form(...), user=Depends(get_current_user)):
    """Get the source document for a given question."""
    try:
        top_results = embedding.search_similar_chunks(question, top_k=1)
    except HTTPException as e:
        return JSONResponse(status_code=400, content={"error": e.detail})

    if not top_results:
        return JSONResponse(status_code=404, content={"source": "No source found"})

    source_doc = top_results[0][2]
    return {"source": source_doc}


@app.post("/ask")
async def ask(request: Request, question: str = Form(...), user=Depends(get_current_user)):
    """Answer a question based on the context from stored PDF chunks."""
    if not question.strip():
        return {"error": "Question cannot be empty."}
    try:
        top_chunks = embedding.search_similar_chunks(question, top_k=3) # Get top 3 chunks
    except HTTPException as e:
        return {"error": e.detail}

    context_text = "\n\n".join([chunk[0] for chunk in top_chunks]) # Combine text from top chunks

    # Create the prompt for the OpenAI model
    prompt = f"""Answer the question based only on the context below. If the answer is not contained within the context, say 'I don't know.'

Context:
{context_text}

Question:
{question}
"""
    async def event_generator():
        """Generator to stream the response from OpenAI API."""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            # Stream the response content
            for chunk in response:
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content is not None:
                    yield content

        # Handle specific OpenAI errors
        except RateLimitError:
            yield "\n[Error] Rate limit exceeded. Please try again later."
        except OpenAIError as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                yield "\n[Error] Invalid or expired OpenAI API key."
            else:
                yield f"\n[Error] OpenAI API error: {error_msg}"
        except Exception as e:
            yield f"\n[Error] Unexpected error: {str(e)}"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
