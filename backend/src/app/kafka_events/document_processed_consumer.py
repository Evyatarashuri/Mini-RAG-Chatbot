from datetime import datetime, timezone
from app.kafka_events.base_consumer import KafkaEventConsumer
from app.db.mongo import documents_collection
from app.db.redis import redis_client # <--- NEW IMPORT
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
        Handle the document_processed event:
        1. Update MongoDB status (document is ready).
        2. Invalidate user's Redis query cache.
        """
        doc_id = event["doc_id"]
        filename = event["filename"]
        user_id = event["user_id"]
        chunks_count = event.get("chunks_count", 0)

        logger.info(
            f"[DocumentProcessedConsumer] Document {filename} (doc_id={doc_id}) "
            f"processed for user {user_id} with {chunks_count} chunks"
        )

        # 1. Update MongoDB: mark document as ready
        documents_collection.update_one(
            {"_id": doc_id},
            {"$set": {
                "ready": True,
                "chunks_count": chunks_count,
                "last_processed_at": datetime.now(timezone.utc)
            }}
        )
        
        # 2. Invalidate the user's cache
        self._invalidate_user_cache(user_id)
        
    def _invalidate_user_cache(self, user_id: str):
        """Deletes all cached RAG answers for a specific user."""
        try:
            # The cache key pattern is "answer:{user_id}:{question}"
            cache_pattern = f"answer:{user_id}:*"
            
            # Find all keys matching the pattern
            keys_to_delete = redis_client.keys(cache_pattern)
            
            if keys_to_delete:
                # Delete all matching keys
                deleted_count = redis_client.delete(*keys_to_delete)
                logger.info(f"[CacheInvalidator] Cleared {deleted_count} cache entries for user {user_id}")
            else:
                logger.debug(f"[CacheInvalidator] No cache entries found for user {user_id}")
                
        except Exception as e:
            logger.error(f"[CacheInvalidator] Failed to invalidate cache for user {user_id}: {e}", exc_info=True)
