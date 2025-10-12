from fastapi import APIRouter, HTTPException, Form, Request, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from app.services import embedding_service
from .auth import get_current_user_from_cookie

router = APIRouter(prefix="/embedding", tags=["embedding"])

@router.post("/sources")
async def source(question: str = Form(...), user=Depends(get_current_user_from_cookie)):
    """Get the source document for a given question."""
    try:
        top_results = embedding_service.search_similar_chunks(question, top_k=1)
    except HTTPException as e:
        return JSONResponse(status_code=400, content={"error": e.detail})
    
    if not top_results:
        return JSONResponse(status_code=404, content={"source": "No source found"})
    
    return {"source": top_results[0][2]}  # Return the source of the top result
