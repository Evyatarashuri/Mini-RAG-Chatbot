from app.core.celery_app import celery_app
from app.services.storage_service import save_file_to_gridfs
from app.db.mongo import documents_collection
from datetime import datetime, timezone

@celery_app.task(acks_late=True)
def save_file_to_gridfs_task(file_path: str, doc_id: str):
    """
    Background archiving task: move a local file into Mongo GridFS and mark document.
    """
    try:
        documents_collection.update_one(
            {"_id": doc_id},
            {"$set": {"archive_status": "running", "archive_started_at": datetime.now(timezone.utc)}}
        )
        file_id = save_file_to_gridfs(file_path, doc_id)
        documents_collection.update_one(
            {"_id": doc_id},
            {"$set": {
                "archive_status": "succeeded",
                "archive_finished_at": datetime.now(timezone.utc),
                "file_id": file_id,
                "file_stored": True
            }}
        )
        return {"doc_id": doc_id, "file_id": file_id, "status": "ok"}
    except Exception as e:
        documents_collection.update_one(
            {"_id": doc_id},
            {"$set": {"archive_status": "failed", "archive_error": str(e)}}
        )
        raise
