# 🧱 Technical Decisions & Scaling Plan

This document outlines key architectural decisions, trade-offs, and how the system could be scaled or productionized beyond this demo.

---

## 📌 Project Flow

1. **PDF Ingestion**: On startup, the app loads all PDFs from the `data/` directory, splits them into chunks, and embeds them using OpenAI Embeddings.

2. **Embedding Storage**: The chunks and metadata are stored in memory (Python lists) for quick similarity search.

3. **User Interaction**: Authenticated users can ask questions via a web form. Their queries are matched against embedded chunks using cosine similarity.

4. **Streaming Response**: Relevant chunks are used as context to query OpenAI, and the answer is streamed to the user.

---

## 🔍 Core Logic: Cosine Similarity

Used to compare the semantic similarity between the embedded user query and each PDF chunk:

```text
similarity = (A · B) / (||A|| * ||B||)
```

This captures semantic meaning, not just keyword overlap.

---

## ⚖️ Key Trade-Offs

* ✅ **Speed & Simplicity**: In-memory storage makes the app fast and simple.
* ❌ **No Persistence**: All embeddings are lost on restart.
* ❌ **Limited Scalability**: Not suitable for large volumes of data or users.

---

## 🏗️ Architectural Improvements for Scale

### User & Auth Management

* Use PostgreSQL to persist users and credentials
* Use JWT/OAuth2 + RBAC for proper access control

### Persistent Embeddings

* Store embeddings in a vector DB (e.g., Qdrant, Chroma, Weaviate)
* Index with metadata (user, file, timestamp) for future queries

### Security

* Environment variables for all secrets
* HTTPS, input sanitization, rate limiting, login throttling

### System Design Principles

* **Reliability**: Add retries + health checks
* **Scalability**: Support both vertical & horizontal scaling
* **Availability**: Multi-zone deployments + monitoring
* **Observability**: Logs, metrics, tracing

---

## ✨ Future Feature Enhancements

* **User PDF Uploads**: Upload → store (e.g., S3) → async embed
* **Dashboard**: View uploaded files and queries
* **Search History**: Audit logs per user
* **Multi-language Support**
* **Offline Mode**: Local embeddings via sentence-transformers
