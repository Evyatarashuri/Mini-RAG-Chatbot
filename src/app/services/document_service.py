import tempfile
import PyPDF2
from app.services import embedding_service
from app.db.mongo import documents_collection
from app.db.faiss_store import faiss_store
from app.core.logging import logger

def process_pdf(file_path: str, user_id: str, doc_id: str, filename: str) -> int:
    """
    Process a PDF: extract text, split into chunks, create embeddings,
    store in FAISS, and update Mongo.
    Returns: number of chunks processed.
    """

    logger.info(f"Processing PDF: {filename} for user: {user_id}")

    # extract text
    reader = PyPDF2.PdfReader(file_path)
    text = "\n".join([p.extract_text() or "" for p in reader.pages])

    logger.info(f"[process_pdf] Extracted {len(text.split())} words")

    # create chunks + embeddings
    chunks = chunk_text(text)
    logger.info(f"[process_pdf] Created {len(chunks)} chunks")

    embeddings = []
    for i, c in enumerate(chunks):
        try:
            emb = embedding_service.create_embedding(c)
            embeddings.append(emb)
        except Exception as e:
            logger.error(f"[process_pdf] Embedding failed on chunk {i}: {e}")

    metadata = [{"user_id": user_id, "chunk": c, "doc_id": doc_id, "filename": filename} for c in chunks]

    # store in FAISS
    if embeddings:
        faiss_store.add(embeddings, metadata)
        logger.info(f"[process_pdf] Added {len(embeddings)} vectors to FAISS")
    else:
        logger.warning(f"[process_pdf] No embeddings to add to FAISS")
    

    # update Mongo with chunk count
    documents_collection.update_one(
        {"_id": doc_id},
        {"$set": {"chunks_count": len(chunks)}}
    )

    return len(chunks)


def chunk_text(text: str, max_words=200) -> list[str]:
    """Split text into shorter chunks."""
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
