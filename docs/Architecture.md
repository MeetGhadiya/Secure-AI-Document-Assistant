# Architecture

## Overview

```text
                 User
                   │
                   ▼
         React + Vite Frontend
                   │
                   ▼
            FastAPI Backend
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
 Session ID   Document Upload  Query API
                   │
                   ▼
          Document Processing
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
 Text Extraction Chunking Embeddings
                   │
                   ▼
             ChromaDB Storage
                   │
                   ▼
               Vector Retriever
                   │
                   ▼
             PII Masking Layer
                   │
                   ▼
           Google Gemini API
                   │
                   ▼
            Contextual Answer
```

## Components

### Frontend (React + Vite + Tailwind)

- Generates and persists a random UUID per browser in Local Storage
  (`useSession` hook). This is sent as the `X-Session-Id` header on every
  request.
- `Sidebar` handles document upload and lists the current session's documents.
- `ChatInterface` sends questions to `/api/query` and renders answers with
  clickable source-chunk citations.
- `SecurityPanel` surfaces the active protections to the end user.

### Backend (FastAPI)

- `app/api/routes.py` exposes `/upload`, `/query`, `/documents`,
  `/documents/{id}`, all requiring a valid `X-Session-Id` header
  (`app/security/session.py`).
- `app/services/document_service.py` orchestrates the upload pipeline:
  validate → store securely → extract text → clean → chunk → embed → persist.
- `app/rag/` contains the embedding model wrapper (Sentence Transformers,
  `all-MiniLM-L6-v2`), the ChromaDB vector store wrapper, and the retriever
  that ties embedding + search + masking together.
- `app/security/pii_masking.py` runs on every retrieved chunk before it is
  passed to Gemini.
- `app/services/gemini_service.py` builds the final prompt (system
  instructions + masked context + question) and calls the Gemini API.

### Storage

- **SQLite** (`app/database/db.py`) — document metadata only: filenames,
  owning session, status, chunk counts, timestamps. Never stores chunk text.
- **ChromaDB** (persistent, on disk) — chunk text, embeddings, and metadata
  (`session_id`, `document_id`, `chunk_index`). Every write and every query
  includes `session_id` in its `where` filter.
- **Local filesystem** (`backend/uploads/`) — original file bytes, saved
  under a randomly generated filename (never the user-supplied name).

## Document processing pipeline

1. Validate the uploaded file (extension allow-list + size limit).
2. Extract text (PyPDF2 for PDF, python-docx for DOCX, plain read for TXT).
3. Clean and normalize whitespace.
4. Split into overlapping chunks (`CHUNK_SIZE` / `CHUNK_OVERLAP`).
5. Generate an embedding vector for each chunk.
6. Store embeddings + text in ChromaDB, tagged with the session ID.
7. Update the SQLite row's status to `ready` (or `failed`).

## Query pipeline

1. Embed the incoming question.
2. Query ChromaDB, filtered by `session_id` (and optionally a single
   `document_id`), for the top-K nearest chunks.
3. Mask sensitive data in each retrieved chunk.
4. Build a prompt from the masked context + question and send it to Gemini.
5. Return the generated answer plus a list of source citations
   (`document_id`, `chunk_index`, redaction count).
