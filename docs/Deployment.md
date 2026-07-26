# Deployment

This prototype is designed to run locally for evaluation/demo purposes.
Below is guidance for moving toward a hosted deployment.

## Local development

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Environment variables (backend/.env)

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (required) | — |
| `GEMINI_MODEL` | Gemini model name | `gemini-1.5-flash` |
| `CHROMA_DB_PATH` | ChromaDB persistence directory | `./chroma_db` |
| `UPLOAD_DIR` | Uploaded file storage directory | `./uploads` |
| `SQLITE_DB_PATH` | SQLite database file path | `./app.db` |
| `MAX_FILE_SIZE_MB` | Max upload size | `20` |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Text chunking parameters | `1000` / `200` |
| `TOP_K_RESULTS` | Number of chunks retrieved per query | `5` |
| `EMBEDDING_MODEL` | Sentence Transformers model | `all-MiniLM-L6-v2` |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `http://localhost:5173` |

## Production considerations

1. **Persistent storage:** mount `chroma_db/`, `uploads/`, and the SQLite
   file (or migrate to PostgreSQL) on durable, backed-up volumes.
2. **Process manager:** run the backend with `uvicorn` behind a process
   manager (e.g. `gunicorn -k uvicorn.workers.UvicornWorker`) or a container
   orchestrator.
3. **Reverse proxy / TLS:** put both frontend and backend behind a reverse
   proxy (nginx, Caddy, or a cloud load balancer) terminating HTTPS.
4. **Frontend build:** `npm run build` produces static assets in
   `frontend/dist/` — serve these from a CDN or static hosting, with the
   proxy routing `/api/*` to the backend service.
5. **Secrets:** store `GEMINI_API_KEY` in a secrets manager, not a committed
   `.env` file.
6. **Authentication:** replace session-ID isolation with real user
   authentication (JWT) and RBAC before handling real customer data — see
   `docs/Security.md`.
7. **Scaling the embedding step:** `sentence-transformers` runs on CPU by
   default; for higher throughput, batch embedding calls or move to a GPU
   instance / managed embeddings API.
8. **Observability:** add structured logging and an audit trail (the
   `query_log` table is a starting point) suitable for compliance review.

## Example container layout (optional)

```text
docker-compose.yml
├── backend   (Python 3.11, uvicorn, mounts chroma_db/ + uploads/ as volumes)
└── frontend  (Node build stage -> static files served by nginx)
```

A `Dockerfile` per service and a `docker-compose.yml` are natural next
additions once the deployment target (cloud provider, on-prem, etc.) is
decided.
