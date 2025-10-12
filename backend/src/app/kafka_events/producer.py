from app.core.kafka_app import get_kafka_producer
from app.core.config import settings
from datetime import datetime, timezone
import json


def publish_document_uploaded(doc_id, filename, user_id, file_path):
    """Send an event when a document is uploaded."""
    producer = get_kafka_producer()
    event = {
        "event_type": "document_uploaded",
        "doc_id": doc_id,
        "filename": filename,
        "user_id": user_id,
        "file_path": file_path,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    producer.send(settings.KAFKA_TOPIC_DOCUMENT_UPLOADED, value=event)
    producer.flush()


def publish_document_processed(doc_id, filename, user_id, chunks_count):
    """Send an event when a document has been processed."""
    producer = get_kafka_producer()
    event = {
        "event_type": "document_processed",
        "doc_id": doc_id,
        "filename": filename,
        "user_id": user_id,
        "chunks_count": chunks_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    producer.send(settings.KAFKA_TOPIC_DOCUMENT_PROCESSED, value=event)
    producer.flush()
