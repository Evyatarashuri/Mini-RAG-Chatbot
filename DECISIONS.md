# 🤠 Technical Decisions & Scaling Plan

This document outlines key architectural decisions, trade-offs, and how the system could be scaled or productionized beyond this demo.

---

## 📌 Project Flow

1. **PDF Ingestion**:
   On startup, the app loads all PDFs from the `data/` directory, splits them into chunks, and embeds them using OpenAI Embeddings.

2. **Embedding Storage**:
   The chunks and metadata are stored in memory (using Python lists) for quick similarity search.

3. **User Interaction**:
   Authenticated users can ask questions via a web form. Their queries are matched against the embedded chunks using cosine similarity.

4. **Streaming Response**:
   The most relevant chunks are used as context to query the OpenAI API, and the answer is streamed back to the user.

---

## 🔍 Cosine Similarity

Cosine similarity is used to determine how semantically similar a user query is to each embedded chunk of PDF text.

It computes the cosine of the angle between two vectors in a multi-dimensional space:

```text
similarity = (A · B) / (||A|| * ||B||)
```

This is particularly useful for comparing sentence embeddings, as it captures semantic closeness rather than just surface-level word overlap.

---

## ⚖️ Key Trade-Offs

* ✅ **Simplicity**: All embeddings are stored in memory, which makes the app fast to start and easy to test.
* ❌ **Persistence**: No long-term storage — once the server restarts, all embeddings are lost.
* ❌ **Scalability**: In-memory vector search limits the number of chunks and concurrent users.

---

## 🚀 How I'd Scale it on "Day 2"

### 🧱 Infrastructure

* **Vector DB**: Integrate a persistent vector database (e.g., Pinecone, Weaviate, Qdrant, or ChromaDB) for scalable and persistent embedding storage.
* **Background Workers**: Offload embedding generation to background tasks (e.g., Celery + Redis or FastAPI BackgroundTasks).
* **Auth & Rate Limiting**: Add OAuth2 / JWT-based auth and a rate limiter to prevent abuse.
* **Storage**: Move PDF uploads and logs to S3 (or equivalent) for scale and durability.
* **Monitoring**: Add logging, tracing, and metrics collection (e.g., Prometheus + Grafana or Datadog).

### ⚖️ Scaling to More Users

* Host behind a load balancer (e.g., AWS ALB)
* Use a managed database and cache (e.g., PostgreSQL + Redis)
* Dockerize the app with proper CI/CD (already partially done)
* Deploy on scalable infra like AWS ECS, Fly.io, or Railway

---

## 🏗️ Architectural Improvements for High Scale

To prepare this application for real-world scale, several core improvements can be made across infrastructure, security, and system design principles:

### 1. **User & Auth Management**

* Use a relational SQL database (e.g., PostgreSQL) to persist user accounts and authentication data securely.
* Implement proper user sessions using JWT or OAuth2.
* Enforce role-based access control (RBAC) for admin/user-level actions.

### 2. **Persistent Vector Database**

* Replace in-memory storage with a production-grade vector DB like **Pinecone**, **Weaviate**, **Qdrant**, or **ChromaDB**.
* Store each chunk with metadata (user ID, source name, timestamp) for efficient multi-user document retrieval.
* Enable similarity indexing with performance optimizations like HNSW or IVF.

### 3. **Security Principles**

* Store all secrets using environment variables or cloud secrets managers.
* Enable HTTPS across all endpoints.
* Sanitize user input to avoid prompt injection or query manipulation.
* Implement rate limiting and login attempt throttling to prevent abuse.

### 4. **System Design Principles**

* **Reliability**: Add health checks and retries for external APIs (OpenAI).
* **Scalability**:

  * **Vertical**: Deploy with more CPU/RAM when needed (e.g., larger containers).
  * **Horizontal**: Add load balancing (e.g., AWS ALB) and scale containers using orchestration tools like ECS, Kubernetes, or Fly.io.
* **Availability**: Use container restarts, multi-zone deployments, and uptime monitoring tools.
* **Observability**: Add structured logging (e.g., `loguru`, `structlog`) and metrics dashboards (Prometheus + Grafana).

---

## ✨ Feature Enhancements

### 1. **User PDF Upload**

* Allow users to upload PDFs via the web interface.
* Store uploaded documents in cloud storage (e.g., Amazon S3).
* Automatically process and embed these documents asynchronously using background workers (e.g., Celery + Redis).

### 2. **User Dashboard**

* Display uploaded documents, metadata, and recent queries.
* Allow deletion or re-indexing of specific files.

### 3. **Multi-Language Support**

* Integrate multilingual embeddings or auto-detection via `langchain` or HuggingFace models.
* Add support for right-to-left languages (e.g., Hebrew, Arabic).

### 4. **Search History + Audit Logs**

* Persist user queries and timestamps.
* Provide search analytics for admins (e.g., most searched topics).

### 5. **Offline Mode / Local Embeddings**

* Add support for running the app with `Instructor` or `sentence-transformers` models locally for air-gapped environments.

---

## ⏱️ Time Spent

Due to the difficult situation in the country, I began the project a day after receiving the assignment and not under the most ideal conditions.
I estimate that the total focused time I spent was between 3 to 4 hours.

It’s also worth mentioning that, because of the war, I temporarily relocated to my parents’ home and worked on a relatively slow machine — which slightly affected performance and development flow.
