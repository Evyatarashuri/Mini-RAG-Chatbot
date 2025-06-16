from openai import OpenAI, RateLimitError, OpenAIError
import numpy as np
import PyPDF2
import os
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")
client = OpenAI(api_key=openai_api_key)

stored_chunks = [] # List to store text chunks
stored_embeddings = [] # List to store embeddings of the text chunks
stored_sources = [] # List to store sources of the text chunks


def load_pdf_text(file_path: str) -> str:
    """Load text from a PDF file."""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {e}")

def load_all_pdfs_from_folder(folder_path: str):
    """Load all PDF files from a specified folder and return their texts and sources."""
    texts = []
    sources = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(folder_path, filename)
            text = load_pdf_text(path)
            texts.append(text)
            sources.append(filename)
    return texts, sources

def chunk_text(text: str, max_words=200):
    """Split text into chunks of a specified maximum number of words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i+max_words])
        chunks.append(chunk)
    return chunks

def create_embedding(text: str):
    """Create an embedding for the given text using OpenAI API."""
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except OpenAIError as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid or expired OpenAI API key.")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {error_msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def embed_and_store_chunks(chunks_with_sources):
    """Embed text chunks and store them along with their sources."""
    global stored_chunks, stored_embeddings, stored_sources
    stored_chunks = [cs[0] for cs in chunks_with_sources]
    stored_sources = [cs[1] for cs in chunks_with_sources]
    stored_embeddings = [create_embedding(chunk) for chunk in stored_chunks]

def prepare_chunks_and_sources(texts, sources, max_words=200):
    """Prepare text chunks and their sources from lists of texts and sources."""
    chunks_with_sources = []
    for text, source in zip(texts, sources):
        chunks = chunk_text(text, max_words)
        for chunk in chunks:
            chunks_with_sources.append((chunk, source))
    return chunks_with_sources

def search_similar_chunks(query: str, top_k=3):
    """Search for the most similar text chunks to the query."""
    if not stored_chunks or not stored_embeddings:
        raise HTTPException(status_code=400, detail="No embeddings stored yet.")
    query_emb = create_embedding(query)
    scores = [cosine_similarity(query_emb, emb) for emb in stored_embeddings]
    top_indices = np.argsort(scores)[-top_k:][::-1]
    results = []
    for i in top_indices:
        results.append((stored_chunks[i], scores[i], stored_sources[i]))
    return results
