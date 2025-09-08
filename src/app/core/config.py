from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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

    class Config:
        env_file = ".env"


settings = Settings()
