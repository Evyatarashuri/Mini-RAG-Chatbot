from datetime import datetime, timezone
from app.kafka_events.base_consumer import KafkaEventConsumer
from app.db.mongo import documents_collection
from app.services.document_service import process_pdf
from app.kafka_events.producer import publish_document_processed
from app.core.logging import logger
from app.core.config import settings


class DocumentUploadedConsumer(KafkaEventConsumer):
    def __init__(self):
        super().__init__(
            topic=settings.KAFKA_TOPIC_DOCUMENT_UPLOADED,
            group_id="document-processor"
        )

    def handle_event(self, event: dict):
        """
        Handle the document_uploaded event.
        Expected event structure:
        {
            "doc_id": str,
            "filename": str,
            "user_id": str,
            "file_path": str
        }
        """
        doc_id = event["doc_id"]
        filename = event["filename"]
        user_id = event["user_id"]
        file_path = event["file_path"]

        logger.info(f"[DocumentUploadedConsumer] Received {filename} for user {user_id}")

        # Update MongoDB status → processing
        documents_collection.update_one(
            {"_id": doc_id},
            {"$set": {"status": "processing", "started_at": datetime.now(timezone.utc)}}
        )

        try:
            # Run PDF processing pipeline
            chunks_count = process_pdf(file_path, user_id, doc_id, filename)

            # Update MongoDB status → processed
            documents_collection.update_one(
                {"_id": doc_id},
                {"$set": {"status": "processed", "finished_at": datetime.now(timezone.utc)}}
            )

            # Publish new event: document_processed
            publish_document_processed(doc_id, filename, user_id, chunks_count)

            logger.info(f"[DocumentUploadedConsumer] Document {doc_id} processed successfully")

        except Exception as e:
            logger.error(f"[DocumentUploadedConsumer] Failed to process {doc_id}: {e}", exc_info=True)
            documents_collection.update_one(
                {"_id": doc_id},
                {"$set": {"status": "failed", "error": str(e)}}
            )

        # Future observability: send processing metrics to Elastic/Grafana
        # Example: processing duration, chunk count, errors
