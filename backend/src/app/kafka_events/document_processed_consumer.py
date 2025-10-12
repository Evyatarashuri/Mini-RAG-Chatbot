from datetime import datetime, timezone
from app.kafka_events.base_consumer import KafkaEventConsumer
from app.db.mongo import documents_collection
from app.core.logging import logger
from app.core.config import settings

class DocumentProcessedConsumer(KafkaEventConsumer):
    def __init__(self):
        super().__init__(
            topic=settings.KAFKA_TOPIC_DOCUMENT_PROCESSED,
            group_id="document-processed"
        )

    def handle_event(self, event: dict):
        """
        Handle the document_processed event.
        Expected event structure:
        {
            "doc_id": str,
            "filename": str,
            "user_id": str,
            "chunks_count": int
        }
        """
        doc_id = event["doc_id"]
        filename = event["filename"]
        user_id = event["user_id"]
        chunks_count = event.get("chunks_count", 0)

        logger.info(
            f"[DocumentProcessedConsumer] Document {filename} (doc_id={doc_id}) "
            f"processed for user {user_id} with {chunks_count} chunks"
        )

        # Update MongoDB: mark document as ready
        documents_collection.update_one(
            {"_id": doc_id},
            {"$set": {
                "ready": True,
                "chunks_count": chunks_count,
                "last_processed_at": datetime.now(timezone.utc)
            }}
        )

        # Future observability: log processing metadata to Elastic/Grafana
        # Example: chunks_count distribution, user activity
