from openai import OpenAI
from app.core.config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def create_embedding(text: str):
    """Create an embedding for the given text using OpenAI's API."""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


def ask_openai(prompt: str) -> str:
    """Send a request to OpenAI and receive a response."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
