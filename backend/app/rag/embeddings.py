"""
Embedding generation using Sentence Transformers (all-MiniLM-L6-v2 by default).

The model is loaded lazily and cached as a module-level singleton so it is
only loaded into memory once per process.
"""
from functools import lru_cache

from app.config import settings


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_texts(texts: list) -> list:
    """Return a list of embedding vectors (list[float]) for the given texts."""
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vectors.tolist()


def embed_query(query: str) -> list:
    return embed_texts([query])[0]
