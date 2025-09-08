import faiss
import numpy as np


class FaissStore:
    def __init__(self, dim=1536):
        self.index = faiss.IndexFlatL2(dim)
        self.vectors = []  # metadata matching vectors

    def add(self, vectors, metadata):
        if not vectors:
            return
        self.index.add(np.array(vectors).astype("float32"))
        self.vectors.extend(metadata)

    def search(self, query_vector, top_k=5):
        if self.index.ntotal == 0:
            return []

        D, I = self.index.search(np.array([query_vector]).astype("float32"), top_k)
        results = []
        for i, idx in enumerate(I[0]):
            if idx == -1 or idx >= len(self.vectors):
                continue
            results.append((self.vectors[idx], float(D[0][i])))
        return results

faiss_store = FaissStore()
