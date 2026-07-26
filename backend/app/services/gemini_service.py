"""
Google Gemini API integration.

Only masked, retrieved document context is ever sent here -- never raw
uploaded documents, and never full documents outside the current session.
"""
import importlib
from typing import Any

from app.config import settings

_configured = False
_genai: Any = None


def _get_genai():
    global _genai
    if _genai is None:
        _genai = importlib.import_module("google.generativeai")
    return _genai


def _ensure_configured():
    genai = _get_genai()

    global _configured
    if not _configured:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file (see .env.example)."
            )
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _configured = True


SYSTEM_PROMPT = """You are a secure document assistant. Answer the user's question
using ONLY the provided context extracted from their uploaded documents.

Rules:
- If the answer is not contained in the context, say you don't have enough
  information in the uploaded documents to answer.
- Never invent facts that are not present in the context.
- Some sensitive values in the context have been replaced with placeholders
  like [MASKED_EMAIL] or [MASKED_PASSWORD]. Do not attempt to guess or
  reconstruct the original values -- just reference them as masked.
- Be concise and cite which document chunk(s) you used.
"""


def generate_answer(question: str, context_chunks: list) -> str:
    _ensure_configured()

    if not context_chunks:
        return (
            "I couldn't find any relevant information in your uploaded documents "
            "to answer this question."
        )

    context_block = "\n\n".join(
        f"[Chunk {i+1} | document_id={c['document_id']} | chunk_index={c['chunk_index']}]\n{c['text']}"
        for i, c in enumerate(context_chunks)
    )

    prompt = f"{SYSTEM_PROMPT}\n\n--- DOCUMENT CONTEXT ---\n{context_block}\n\n--- QUESTION ---\n{question}"

    genai = _get_genai()
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text
