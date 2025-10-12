from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.kafka_events.producer import publish_document_uploaded
from app.db.mongo import documents_collection
import uuid
from pathlib import Path
from app.core.logging import logger

router = APIRouter(prefix="/api/documents", tags=["api-documents"])

UPLOAD_DIR = Path(settings.UPLOADS_DIR)

@router.post("/")
async def upload_document(request: Request, file: UploadFile = File(...)):
    user = getattr(request.state, "user", None)
    if not user:
        logger.warning("Unauthorized document upload attempt")
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    doc_record = {
        "user_id": str(user["_id"]),
        "filename": file.filename,
        "path": str(file_path),
        "status": "uploaded"
    }
    result = documents_collection.insert_one(doc_record)

    # Publish Kafka event
    publish_document_uploaded(str(result.inserted_id), file.filename, str(user["_id"]), str(file_path))

    return {"message": "File uploaded successfully", "filename": file.filename}
