"""
Retriever: turns a natural-language question into masked, session-scoped
document context ready to be sent to the LLM.
"""
from app.config import settings
from app.rag.embeddings import embed_query
from app.rag.vector_store import query_chunks
from app.security.pii_masking import mask_chunks


def retrieve_context(session_id: str, question: str, document_id: str = None, top_k: int = None) -> list:
    top_k = top_k or settings.TOP_K_RESULTS

    query_embedding = embed_query(question)
    raw_chunks = query_chunks(
        session_id=session_id,
        query_embedding=query_embedding,
        top_k=top_k,
        document_id=document_id,
    )

    # Sensitive data is masked BEFORE it ever leaves the local system.
    masked_chunks = mask_chunks(raw_chunks)
    return masked_chunks
