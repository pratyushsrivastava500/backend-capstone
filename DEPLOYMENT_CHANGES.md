# Deployment Changes for Render (Free Tier - 512MB RAM)

## Overview

This document outlines the changes made to successfully deploy the **Domain Knowledge Co-Pilot API** on Render's free tier, which has a 512MB memory limit. **No changes were made to the core logic, architecture, or application flow.** All endpoints, RAG pipeline, authentication, and database operations remain functionally identical.

---

## 1. Memory Optimization (OOM Fix)

### Problem
The application was crashing on Render with:
```
Out of memory (used over 512Mi)
```

### Root Cause
The `sentence-transformers` library pulls in **PyTorch** as a dependency, which alone consumes ~300-400MB of RAM. Combined with the embedding model weights (~90MB) and the rest of the application, total memory usage exceeded 512MB before the app could even serve a request.

### Solution
Replaced `sentence-transformers` (PyTorch-based) with **ChromaDB's built-in DefaultEmbeddingFunction** which uses **ONNX Runtime** — a much lighter inference engine.

| Component | Before | After |
|-----------|--------|-------|
| Embedding engine | PyTorch (~400MB) | ONNX Runtime (~100-150MB) |
| Model | all-MiniLM-L6-v2 | all-MiniLM-L6-v2 (same model) |
| Embedding quality | Identical | Identical |
| Library | sentence-transformers | chromadb.utils.embedding_functions |

### Files Changed
- **`rag.py`** — Replaced `SentenceTransformer` import and usage with `chromadb.utils.embedding_functions.DefaultEmbeddingFunction()`. ChromaDB now handles embedding generation internally using the same model but through ONNX Runtime.
- **`requirements.txt`** — Removed `sentence-transformers==5.3.0`, added `onnxruntime>=1.24.1` and `tokenizers>=0.13.2`.

---

## 2. Missing Dependency Fix

### Problem
```
RuntimeError: Form data requires "python-multipart" to be installed.
```

### Root Cause
FastAPI requires `python-multipart` for file upload endpoints (`UploadFile`). This dependency was missing from `requirements.txt`.

### Solution
Added `python-multipart>=0.0.7` to `requirements.txt`.

---

## 3. Python Version Pinning

### Problem
Render was auto-selecting Python 3.14 (bleeding edge), which caused compatibility issues with several packages.

### Solution
Added `runtime.txt` with `python-3.11.12` to pin a stable, well-supported Python version.

---

## What Was NOT Changed

- **Endpoints** — All API routes (`/signup`, `/login`, `/upload-pdf`, `/chat`, `/`) remain the same.
- **RAG Pipeline** — Text chunking, document storage, query retrieval, and LLM prompting logic are untouched.
- **Embedding Model** — Still uses `all-MiniLM-L6-v2`. Only the inference engine changed (PyTorch → ONNX Runtime). Embedding vectors are identical.
- **Database** — SQLAlchemy models, schemas, and SQLite usage are unchanged.
- **Authentication** — JWT token creation, password hashing (bcrypt), login/signup flow are all the same.
- **PDF Processing** — `pypdf`-based text extraction remains unchanged.
- **Groq LLM Integration** — Still uses `llama-3.1-8b-instant` via Groq API with the same prompt structure.

---

## Deployment Notes

- After deploying, use **"Clear build cache & deploy"** on Render if you face stale dependency issues.
- If you had previously uploaded PDFs, re-upload them after the first deploy so ChromaDB recreates the collection with the ONNX-based embedding function.
- Ensure `GROQ_API_KEY` is set in Render's environment variables.
