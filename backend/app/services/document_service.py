"""
Orchestrates the document upload pipeline:
validate -> save securely -> extract text -> clean -> chunk -> embed -> store.
"""
import uuid

from app.config import settings
from app.database import db
from app.rag.embeddings import embed_texts
from app.rag.vector_store import add_chunks, delete_document_chunks
from app.security.file_security import (
    generate_secure_filename,
    safe_upload_path,
    delete_file_safely,
)
from app.services.text_extraction import extract_text, clean_text, chunk_text


def process_upload(session_id: str, original_filename: str, file_ext: str, file_bytes: bytes) -> dict:
    doc_id = str(uuid.uuid4())
    stored_filename = generate_secure_filename(file_ext)
    dest_path = safe_upload_path(stored_filename)

    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    db.insert_document(
        doc_id=doc_id,
        session_id=session_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_type=file_ext,
        file_size_bytes=len(file_bytes),
    )

    try:
        raw_text = extract_text(dest_path, file_ext)
        cleaned = clean_text(raw_text)

        if not cleaned:
            db.update_document_status(doc_id, status="failed", chunk_count=0)
            return {"document_id": doc_id, "status": "failed", "reason": "No extractable text found."}

        chunks = chunk_text(cleaned, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        embeddings = embed_texts(chunks)

        add_chunks(
            session_id=session_id,
            document_id=doc_id,
            chunk_texts=chunks,
            embeddings=embeddings,
        )

        db.update_document_status(doc_id, status="ready", chunk_count=len(chunks))
        return {"document_id": doc_id, "status": "ready", "chunk_count": len(chunks)}

    except Exception as exc:  # noqa: BLE001
        db.update_document_status(doc_id, status="failed", chunk_count=0)
        return {"document_id": doc_id, "status": "failed", "reason": str(exc)}


def remove_document(session_id: str, document_id: str) -> bool:
    doc = db.get_document(document_id, session_id)
    if not doc:
        return False

    delete_document_chunks(session_id=session_id, document_id=document_id)
    delete_file_safely(doc["stored_filename"])
    db.delete_document(document_id, session_id)
    return True
