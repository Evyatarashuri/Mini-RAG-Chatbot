import json
import time
import pytest
from fastapi.testclient import TestClient
from src.app.main import app
from src.app.core.kafka_app import get_kafka_producer, get_kafka_consumer
from src.app.core.config import settings


client = TestClient(app)


@pytest.fixture(scope="module")
def kafka_producer():
    return get_kafka_producer()


@pytest.fixture(scope="module")
def kafka_consumer_uploaded():
    consumer = get_kafka_consumer(
        topic=settings.KAFKA_TOPIC,
        group_id="test_uploaded_consumer",
    )
    consumer.poll(timeout_ms=1000)  # Initial poll to join the group
    return consumer


@pytest.fixture(scope="module")
def kafka_consumer_processed():
    consumer = get_kafka_consumer(
        topic="document_processed",
        group_id="test_processed_consumer",
    )
    consumer.poll(timeout_ms=1000)  # Initial poll to join the group
    return consumer


def test_document_upload_event_flow(kafka_producer, kafka_consumer_uploaded, kafka_consumer_processed):
    """Integration test: document_uploaded → document_processed → notifier"""

    # 1. Send event directly (simulate upload)
    event = {"doc_id": "test123", "filename": "test.pdf", "user_id": "user1"}
    kafka_producer.send(settings.KAFKA_TOPIC, value=event)
    kafka_producer.flush()

    # 2. Wait and check uploaded-consumer got it
    msg_uploaded = None
    for _ in range(5):  # retry up to 5 sec
        records = kafka_consumer_uploaded.poll(timeout_ms=1000)
        for tp, msgs in records.items():
            for msg in msgs:
                msg_uploaded = json.loads(msg.value)
        if msg_uploaded:
            break
        time.sleep(1)

    assert msg_uploaded is not None, "Uploaded event was not consumed"
    assert msg_uploaded["doc_id"] == "test123"

    # 3. Simulate that uploaded-consumer produced document_processed
    processed_event = {
        "doc_id": "test123",
        "filename": "test.pdf",
        "user_id": "user1",
        "chunks_count": 5
    }
    kafka_producer.send("document_processed", value=processed_event)
    kafka_producer.flush()

    # 4. Wait and check processed-consumer got it
    msg_processed = None
    for _ in range(5):
        records = kafka_consumer_processed.poll(timeout_ms=1000)
        for tp, msgs in records.items():
            for msg in msgs:
                msg_processed = json.loads(msg.value)
        if msg_processed:
            break
        time.sleep(1)

    assert msg_processed is not None, "Processed event was not consumed"
    assert msg_processed["chunks_count"] == 5