from abc import ABC, abstractmethod
from app.core.kafka_app import get_kafka_consumer
from app.core.logging import logger


class KafkaEventConsumer(ABC):
    """
    Abstract base class for Kafka event consumers.
    Subclasses implement handle_event().
    """

    def __init__(self, topic: str, group_id: str):
        self.topic = topic
        self.group_id = group_id
        self.consumer = get_kafka_consumer(topic=topic, group_id=group_id)

    @abstractmethod
    def handle_event(self, event: dict):
        """Process a single Kafka event."""
        pass

    def run(self):
        logger.info(f"[KafkaConsumer] Listening on topic: {self.topic}, group: {self.group_id}")
        for message in self.consumer:
            try:
                event = message.value
                self.handle_event(event)
            except Exception as e:
                logger.error(f"[KafkaConsumer] Error handling event: {e}", exc_info=True)
