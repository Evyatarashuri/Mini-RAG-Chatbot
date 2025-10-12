from app.kafka_events.document_uploaded_consumer import DocumentUploadedConsumer

if __name__ == "__main__":
    consumer = DocumentUploadedConsumer()
    consumer.run()
