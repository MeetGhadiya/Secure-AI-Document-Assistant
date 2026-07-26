# API Reference

Base URL: `http://localhost:8000/api`

All endpoints (except `/health`, which lives at the app root) require an
`X-Session-Id` header containing a valid UUID. Requests missing or with a
malformed header are rejected with `401`/`400`.

## POST /upload

Upload a document for the current session.

**Request:** `multipart/form-data`, field `file` (PDF, DOCX, or TXT, ≤
`MAX_FILE_SIZE_MB`).

**Response `200`:**

```json
{
  "document_id": "b6b6b6b6-...",
  "status": "ready",
  "chunk_count": 42
}
```

On extraction failure, `status` is `"failed"` and a `reason` field is
included instead of `chunk_count`.

## POST /query

Ask a question about the current session's documents.

**Request body:**

```json
{
  "question": "What is the liability cap in the contract?",
  "document_id": null,
  "top_k": 5
}
```

`document_id` is optional — omit it (or pass `null`) to search across all of
the session's documents; pass a specific document ID to scope the search to
one file. `top_k` is optional (default from server config).

**Response `200`:**

```json
{
  "answer": "The liability is capped at $500,000 per occurrence...",
  "sources": [
    { "document_id": "b6b6b6b6-...", "chunk_index": 3, "redactions": 0 },
    { "document_id": "b6b6b6b6-...", "chunk_index": 4, "redactions": 2 }
  ]
}
```

`redactions` indicates how many sensitive values were masked out of that
chunk before it was sent to the model.

## GET /documents

List all documents belonging to the current session.

**Response `200`:**

```json
[
  {
    "id": "b6b6b6b6-...",
    "original_filename": "contract_v1.pdf",
    "file_type": ".pdf",
    "file_size_bytes": 245678,
    "chunk_count": 42,
    "status": "ready",
    "created_at": "2026-07-26T10:00:00"
  }
]
```

## DELETE /documents/{document_id}

Delete a document (metadata row, stored file, and all its vector chunks).
Scoped to the current session — deleting a document that belongs to a
different session (or doesn't exist) returns `404`.

**Response `200`:**

```json
{ "document_id": "b6b6b6b6-...", "deleted": true }
```

## GET /health

Simple liveness check (no session header required). Returns `{"status": "ok"}`.
