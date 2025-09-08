import tempfile
import PyPDF2
from app.services import embedding_service
from app.db.mongo import documents_collection
from app.db.faiss_store import faiss_store


async def process_pdf(file, user_id: str):
    # save file temporarily
    tmp = tempfile.NamedTemporaryFile(delete=False)
    contents = await file.read()
    tmp.write(contents)
    tmp.close()

    # extract text
    reader = PyPDF2.PdfReader(tmp.name)
    text = "\n".join([p.extract_text() or "" for p in reader.pages])

    # create chunks + embeddings
    chunks = embedding_service.chunk_text(text)
    embeddings = [embedding_service.create_embedding(c) for c in chunks]

    # store in FAISS
    metadata = [{"user_id": user_id, "chunk": c, "doc": file.filename} for c in chunks]
    faiss_store.add(embeddings, metadata)

    # save in Mongo
    result = documents_collection.insert_one({
        "user_id": user_id,
        "filename": file.filename,
        "chunks_count": len(chunks),
    })

    return str(result.inserted_id)
