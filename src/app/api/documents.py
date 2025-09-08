from fastapi import APIRouter, UploadFile, Depends, HTTPException
from app.services import document_service
from app.api.auth import get_current_user_from_cookie

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_pdf(file: UploadFile, user=Depends(get_current_user_from_cookie)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    doc_id = await document_service.process_pdf(file, user["_id"])
    return {"message": "PDF uploaded successfully", "doc_id": str(doc_id)}
