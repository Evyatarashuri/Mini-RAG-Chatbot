from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # General
    PROJECT_NAME: str = "FAISS PDF RAG"
    DEBUG: bool = True

    # OpenAI
    OPENAI_API_KEY: str

    # Mongo
    MONGO_URI: str
    MONGO_DB: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Kafka - Broker
    KAFKA_BROKER: str

    # Kafka - Topics
    KAFKA_TOPIC_DOCUMENT_UPLOADED: str
    KAFKA_TOPIC_DOCUMENT_PROCESSED: str
    KAFKA_TOPIC_NOTIFICATION_READY: str

    # Uploads
    UPLOADS_DIR: str

    class Config:
        env_file = ".env"


settings = Settings()
