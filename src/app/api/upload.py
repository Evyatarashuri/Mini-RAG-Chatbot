from pathlib import Path
from fastapi import APIRouter, UploadFile, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.auth import get_current_user_from_cookie
from app.db.mongo import documents_collection
from app.kafka_events.producer import publish_document_uploaded
from bson import ObjectId
from datetime import datetime, timezone
from app.core.logging import logger
from app.core.config import settings
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    """
    Display the upload form page.
    """
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def upload_pdf(
    request: Request,
    file: UploadFile,
    description: str = Form(""),
    user: dict = Depends(get_current_user_from_cookie)
):
    """
    Handle uploaded PDF file, save it to disk, log to MongoDB, and trigger Kafka event.
    """
    if not file.filename.lower().endswith(".pdf"):
        return templates.TemplateResponse(
            "upload.html",
            {"request": request, "error": "Only PDF files are supported."},
        )

    uploads_dir = settings.UPLOADS_DIR
    os.makedirs(uploads_dir, exist_ok=True)

    try:
        doc_id = str(ObjectId())
        saved_path = os.path.join(uploads_dir, f"{doc_id}_{file.filename}")

        contents = await file.read()
        with open(saved_path, "wb") as f:
            f.write(contents)

        documents_collection.insert_one({
            "_id": doc_id,
            "user_id": str(user["_id"]),
            "filename": file.filename,
            "description": description,
            "path": saved_path,
            "status": "queued",
            "created_at": datetime.now(timezone.utc),
        })

        publish_document_uploaded(
            doc_id=doc_id,
            filename=file.filename,
            user_id=str(user["_id"]),
            file_path=saved_path
        )

        logger.info(f"File {file.filename} uploaded successfully by user {user['_id']}")

        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "success": f"File '{file.filename}' uploaded successfully!",
                "filename": file.filename,
                "description": description
            },
        )

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return templates.TemplateResponse(
            "upload.html",
            {"request": request, "error": f"Upload failed: {str(e)}"},
        )
