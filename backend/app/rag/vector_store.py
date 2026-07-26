"""
ChromaDB-backed vector store.

CRITICAL SECURITY INVARIANT: every write includes a `session_id` in its
metadata, and every query filters `where={"session_id": session_id}`. This
is what prevents one browser session from ever retrieving another session's
document chunks. Never call the underlying collection without this filter.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

_COLLECTION_NAME = "document_chunks"

_client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_PATH,
    settings=ChromaSettings(anonymized_telemetry=False),
)


def _get_collection():
    return _client.get_or_create_collection(name=_COLLECTION_NAME)


def add_chunks(
    session_id: str,
    document_id: str,
    chunk_texts: list,
    embeddings: list,
) -> None:
    if not chunk_texts:
        return

    collection = _get_collection()
    ids = [f"{document_id}_{i}" for i in range(len(chunk_texts))]
    metadatas = [
        {"session_id": session_id, "document_id": document_id, "chunk_index": i}
        for i in range(len(chunk_texts))
    ]
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunk_texts,
        metadatas=metadatas,
    )


def query_chunks(session_id: str, query_embedding: list, top_k: int, document_id: str = None) -> list:
    """
    Retrieve the top_k most relevant chunks, STRICTLY scoped to session_id.
    Optionally further scoped to a single document_id.
    """
    collection = _get_collection()

    where_clause = {"session_id": session_id}
    if document_id:
        where_clause = {"$and": [{"session_id": session_id}, {"document_id": document_id}]}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause,
    )

    chunks = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0] if results.get("distances") else [None] * len(documents)

    for text, meta, distance in zip(documents, metadatas, distances):
        chunks.append(
            {
                "text": text,
                "document_id": meta.get("document_id"),
                "chunk_index": meta.get("chunk_index"),
                "distance": distance,
            }
        )
    return chunks


def delete_document_chunks(session_id: str, document_id: str) -> None:
    """Delete all chunks for a document, scoped to the owning session."""
    collection = _get_collection()
    collection.delete(where={"$and": [{"session_id": session_id}, {"document_id": document_id}]})
