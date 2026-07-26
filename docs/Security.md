# Security

This document describes the security measures implemented in the prototype
and the path to hardening them for production.

## Session isolation

Each browser is assigned a random UUID on first visit, stored in Local
Storage and sent as the `X-Session-Id` header on every request
(`app/security/session.py`). The header is validated as a well-formed UUID.

Every read and write to both the SQLite metadata store and the ChromaDB
vector store includes this session ID:

- `app/database/db.py` — every query includes `WHERE session_id = ?`.
- `app/rag/vector_store.py` — every ChromaDB `add`/`query`/`delete` call
  includes `session_id` in its metadata / `where` filter.

This means one browser session cannot retrieve, list, or delete another
session's documents, even if it somehow learned another session's document
ID — the SQL and vector-store filters require both the ID and a matching
session_id.

**Production note:** session IDs are a lightweight stand-in for real
authentication. They are not tamper-proof (a client could forge a header)
and provide no user-level audit trail. Production deployment should replace
this with authenticated users (JWT) and role-based access control (RBAC),
as listed in the Future Enhancements section of the README.

## Sensitive data masking

Before any retrieved chunk is included in a prompt sent to Gemini, it passes
through `app/security/pii_masking.py`, which uses pattern matching to detect
and redact:

- Email addresses
- Phone numbers
- Credit card numbers
- Social Security numbers
- Client / account / customer IDs
- Passwords and API keys/tokens appearing in text
- IP addresses
- Dates of birth

Matches are replaced with category-labelled placeholders (e.g.
`[MASKED_EMAIL]`) so the model can still reason about the presence of such a
value without ever seeing it. The number of redactions per chunk is surfaced
to the frontend as a source-citation badge.

**Production note:** regex-based masking has good precision but imperfect
recall (it will not catch, for example, a person's name mentioned in prose).
A production system should pair this with a dedicated PII-detection model
(e.g. Microsoft Presidio) for higher-recall entity detection.

## File upload security

- **Type validation:** only `.pdf`, `.docx`, `.txt` are accepted
  (`app/security/file_security.py`).
- **Size limits:** enforced via `MAX_FILE_SIZE_MB`.
- **Secure storage:** uploaded files are saved under a randomly generated
  UUID-based filename — the original filename is stored only as metadata and
  never used as a path.
- **Path traversal protection:** every resolved storage path is asserted to
  remain within the configured upload directory before any file read/write.

## Transport & secrets

- The Gemini API key is read from environment variables (`.env`, excluded
  from version control) and never exposed to the frontend.
- CORS is restricted to configured frontend origins (`CORS_ORIGINS`).

## Known limitations of this prototype

- No authentication — anyone with a session ID (which lives in their own
  browser) can access that session's data; there's no login.
- No encryption at rest for the SQLite DB, ChromaDB store, or uploaded files
  on disk — add disk-level or field-level encryption before handling real
  sensitive data in production.
- No audit logging beyond the `query_log` table.
- No rate limiting on `/upload` or `/query`.
