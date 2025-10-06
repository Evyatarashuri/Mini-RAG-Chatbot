from kafka import KafkaProducer, KafkaConsumer
from .config import settings
import json

_producer = None


def get_kafka_producer():
    """Singleton Kafka producer (shared instance)."""
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=[settings.KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
    return _producer


def get_kafka_consumer(topic: str, group_id: str = "default"):
    """Return a Kafka consumer subscribed to the given topic."""
    return KafkaConsumer(
        topic,
        bootstrap_servers=[settings.KAFKA_BROKER],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
