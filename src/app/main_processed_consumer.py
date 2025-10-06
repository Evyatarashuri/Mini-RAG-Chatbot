from app.kafka_events.document_processed_consumer import DocumentProcessedConsumer

if __name__ == "__main__":
    consumer = DocumentProcessedConsumer()
    consumer.run()
