from app.kafka_events.base_consumer import KafkaEventConsumer
from app.core.logging import logger


class NotifierConsumer(KafkaEventConsumer):
    def __init__(self):
        super().__init__(topic="document_processed", group_id="notifier")

    def handle_event(self, event: dict):
        """
        Handle notifications after document_processed event.
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
            f"[NotifierConsumer] Sending notification for document {filename} "
            f"(doc_id={doc_id}, user_id={user_id}, chunks={chunks_count})"
        )

        # Future extension: send email / WebSocket notification
        # Example: notify user "Your document has been processed"

        # Future observability: track notification delivery
        # Example: store success/failure rate of notifications
