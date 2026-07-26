from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.database import db
from app.models.schemas import (
    DeleteResponse,
    DocumentResponse,
    QueryRequest,
    QueryResponse,
    SourceCitation,
    UploadResponse,
)
from app.rag.retriever import retrieve_context
from app.security.file_security import validate_file
from app.security.session import get_session_id
from app.services import document_service
from app.services.gemini_service import generate_answer

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Depends(get_session_id),
):
    file_bytes = await file.read()
    ext = validate_file(file, content_length=len(file_bytes))

    result = document_service.process_upload(
        session_id=session_id,
        original_filename=file.filename,
        file_ext=ext,
        file_bytes=file_bytes,
    )
    return UploadResponse(**result)


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    payload: QueryRequest,
    session_id: str = Depends(get_session_id),
):
    db.log_query(session_id, payload.question)

    context_chunks = retrieve_context(
        session_id=session_id,
        question=payload.question,
        document_id=payload.document_id,
        top_k=payload.top_k,
    )

    try:
        answer = generate_answer(payload.question, context_chunks)
    except RuntimeError as e:
        # Provide a clearer error to the frontend when the Gemini client
        # isn't configured (missing API key or model misconfiguration).
        raise HTTPException(status_code=500, detail=str(e))

    sources = [
        SourceCitation(
            document_id=c["document_id"],
            chunk_index=c["chunk_index"],
            redactions=c.get("redactions", 0),
        )
        for c in context_chunks
    ]
    return QueryResponse(answer=answer, sources=sources)


@router.get("/documents", response_model=list[DocumentResponse])
async def get_documents(session_id: str = Depends(get_session_id)):
    return db.list_documents(session_id)


@router.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str, session_id: str = Depends(get_session_id)):
    deleted = document_service.remove_document(session_id, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found in this session.")
    return DeleteResponse(document_id=document_id, deleted=True)
