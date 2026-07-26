"""
Google Gemini API integration.

Only masked, retrieved document context is ever sent here -- never raw
uploaded documents, and never full documents outside the current session.
"""
import importlib
import time
from typing import Any

from app.config import settings
import logging

# Adapter that supports both the legacy `google.generativeai` package
# and the newer `google.genai` package. Prefer `google.genai` when
# available.
_configured = False
_genai: Any = None
_genai_client: Any = None
_use_new_genai = False


def _get_genai():
    global _genai, _use_new_genai
    if _genai is None:
        try:
            _genai = importlib.import_module("google.genai")
            _use_new_genai = True
        except ModuleNotFoundError:
            # fall back to older package name used in older examples
            _genai = importlib.import_module("google.generativeai")
            _use_new_genai = False
    return _genai


def _ensure_configured():
    global _configured, _genai_client
    genai = _get_genai()

    if _configured:
        return

    if not settings.GEMINI_API_KEY:
        raise RuntimeError("api key is not available")

    if _use_new_genai:
        # The new `google.genai` uses a client object. Create and keep one.
        try:
            _genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except TypeError:
            # Some versions expect the key in client() or environment; try both ways.
            _genai_client = genai.Client()
            # If the client requires env-based key, we rely on the underlying
            # library to pick it up from environment variables.
    else:
        # legacy configure call
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

    # Implement a model chain with fallbacks from config
    model_chain = getattr(settings, "GEMINI_MODEL_CHAIN", [settings.GEMINI_MODEL])

    # logging
    logger = logging.getLogger(__name__)

    # Configuration for per-model retries
    per_model_attempts = 3
    backoffs = [1, 2, 4]
    max_total_seconds = 30
    start_time = time.time()

    last_exception = None
    # helper to normalize responses
    def _resp_to_text(r):
        if r is None:
            return ""
        if hasattr(r, "text") and r.text:
            return r.text
        if hasattr(r, "output") and r.output:
            return r.output
        if hasattr(r, "outputs"):
            parts = []
            for out in r.outputs:
                cont = getattr(out, "content", None)
                if isinstance(cont, (list, tuple)):
                    for item in cont:
                        if isinstance(item, str):
                            parts.append(item)
                        elif hasattr(item, "text"):
                            parts.append(item.text)
                        else:
                            parts.append(str(item))
                elif isinstance(cont, str):
                    parts.append(cont)
                elif hasattr(out, "text"):
                    parts.append(out.text)
                else:
                    parts.append(str(out))
            return "".join(parts)
        return str(r)

    # Iterate over the configured model chain and attempt generation with per-model retries
    for model_candidate in model_chain:
        if time.time() - start_time > max_total_seconds:
            logger.warning("Time cap exceeded while trying model chain")
            break

        logger.debug("Trying model %s for generation", model_candidate)

        if _use_new_genai:
            global _genai_client
            if _genai_client is None:
                _genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
            client = _genai_client

            for attempt in range(1, per_model_attempts + 1):
                try:
                    if hasattr(client, "models") and hasattr(client.models, "generate_content"):
                        resp = client.models.generate_content(model=model_candidate, contents=[prompt])
                    elif hasattr(genai, "models") and hasattr(genai.models, "generate_content"):
                        resp = genai.models.generate_content(model=model_candidate, contents=[prompt])
                    else:
                        raise RuntimeError("Installed google.genai package doesn't expose a known generate API.")

                    text = _resp_to_text(resp)
                    logger.info("Gemini generation succeeded with model %s", model_candidate)
                    return text
                except Exception as e:
                    last_exception = e
                    # extract detail
                    try:
                        detail = repr(e.args[0]) if hasattr(e, "args") and e.args and isinstance(e.args[0], (dict, list)) else str(e)
                    except Exception:
                        detail = str(e)
                    low = detail.lower()

                    if "503" in low or "unavailable" in low or "high demand" in low or "429" in low:
                        logger.warning("Transient error from model %s attempt %s: %s", model_candidate, attempt, detail)
                        if attempt < per_model_attempts and (time.time() - start_time) < max_total_seconds:
                            wait = backoffs[min(attempt - 1, len(backoffs) - 1)]
                            time.sleep(wait)
                            continue
                        logger.info("Exhausted retries for model %s, falling back", model_candidate)
                        break

                    if "token" in low or "expired" in low or "unauth" in low or "401" in low:
                        raise RuntimeError(f"GenAI request failed: {detail}") from e

                    logger.error("Non-retryable error for model %s: %s", model_candidate, detail)
                    break
        else:
            # legacy generativeai path
            try:
                legacy_model = genai.GenerativeModel(model_candidate)
            except Exception as e:
                last_exception = e
                logger.exception("Failed to construct legacy model %s: %s", model_candidate, e)
                continue

            for attempt in range(1, per_model_attempts + 1):
                try:
                    response = legacy_model.generate_content(prompt)
                    logger.info("Gemini (legacy) generation succeeded with model %s", model_candidate)
                    return response.text
                except Exception as e:
                    last_exception = e
                    detail = str(e)
                    low = detail.lower()
                    if "503" in low or "unavailable" in low or "high demand" in low or "429" in low:
                        logger.warning("Transient error from legacy model %s attempt %s: %s", model_candidate, attempt, detail)
                        if attempt < per_model_attempts and (time.time() - start_time) < max_total_seconds:
                            wait = backoffs[min(attempt - 1, len(backoffs) - 1)]
                            time.sleep(wait)
                            continue
                        logger.info("Exhausted retries for legacy model %s, falling back", model_candidate)
                        break
                    if "token" in low or "expired" in low or "unauth" in low or "401" in low:
                        raise RuntimeError(f"GenAI request failed: {detail}") from e
                    logger.error("Non-retryable error for legacy model %s: %s", model_candidate, detail)
                    break

    # After exhausting chain
    if last_exception is not None:
        try:
            payload = last_exception.args[0] if hasattr(last_exception, "args") and last_exception.args else str(last_exception)
            raise RuntimeError(f"GenAI request failed: {payload}") from last_exception
        except Exception:
            raise RuntimeError(f"GenAI request failed: {last_exception}") from last_exception
    raise RuntimeError("GenAI request failed: unknown error")
