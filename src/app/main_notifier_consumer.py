from app.kafka_events.base_consumer import KafkaEventConsumer
from app.core.logging import logger

class NotifierConsumer(KafkaEventConsumer):
    def __init__(self):
        super().__init__(topic="notification_ready", group_id="notification-service")

    def handle_event(self, event: dict):
        logger.info(f"[NotifierConsumer] Received notification event: {event}")
        
if __name__ == "__main__":
    consumer = NotifierConsumer()
    consumer.run()
