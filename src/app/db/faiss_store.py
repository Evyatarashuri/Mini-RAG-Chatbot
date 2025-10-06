import faiss
import numpy as np
import os
from app.core.logging import logger

FAISS_PATH = "/data/faiss.index"
META_PATH = "/data/metadata.npy"

class FaissStore:
    def __init__(self, dim=1536):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.vectors = []
        self._load()

    def add(self, vectors, metadata):
        if not vectors:
            return
        self.index.add(np.array(vectors).astype("float32"))
        self.vectors.extend(metadata)
        self._save()
        logger.info(f"[faiss_store] Added {len(vectors)} vectors, total={self.index.ntotal}")

    def search(self, query_vector, top_k=5):
        # Always reload before searching
        self.reload()
        if self.index.ntotal == 0:
            logger.warning("[faiss_store] No vectors available for search")
            return []
        D, I = self.index.search(np.array([query_vector]).astype("float32"), top_k)
        results = []
        for i, idx in enumerate(I[0]):
            if idx == -1 or idx >= len(self.vectors):
                continue
            results.append((self.vectors[idx], float(D[0][i])))
        return results

    def _save(self):
        os.makedirs("/data", exist_ok=True)
        faiss.write_index(self.index, FAISS_PATH)
        np.save(META_PATH, self.vectors, allow_pickle=True)
        logger.info(f"[faiss_store] Saved index to {FAISS_PATH} and metadata to {META_PATH}")

    def _load(self):
        if os.path.exists(FAISS_PATH) and os.path.exists(META_PATH):
            self.index = faiss.read_index(FAISS_PATH)
            self.vectors = np.load(META_PATH, allow_pickle=True).tolist()
            logger.info(f"[faiss_store] Loaded {self.index.ntotal} vectors from {FAISS_PATH}")
        else:
            logger.info("[faiss_store] No previous FAISS index found")

    def reload(self):
        """Force reload FAISS index from disk (used by FastAPI query endpoint)."""
        if os.path.exists(FAISS_PATH):
            self._load()
            logger.info(f"[faiss_store] Reloaded FAISS index (now {self.index.ntotal} vectors)")
        else:
            logger.warning("[faiss_store] No FAISS index found on disk to reload")

faiss_store = FaissStore()
