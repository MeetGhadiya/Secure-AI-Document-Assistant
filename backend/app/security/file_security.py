"""
File upload security: extension/type validation, size limits, secure
randomized storage filenames, and path traversal protection.
"""
import os
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config import settings


def validate_file(file: UploadFile, content_length: int) -> str:
    """Validate extension and size. Returns the normalized extension."""
    original_name = file.filename or ""
    ext = Path(original_name).suffix.lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(settings.ALLOWED_EXTENSIONS)}",
        )

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if content_length > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the {settings.MAX_FILE_SIZE_MB}MB size limit.",
        )

    return ext


def generate_secure_filename(ext: str) -> str:
    """Generate a random, non-guessable filename. Never trust user-supplied names."""
    return f"{uuid.uuid4().hex}{ext}"


def safe_upload_path(stored_filename: str) -> str:
    """
    Resolve the final path for a stored filename and assert it stays within
    the upload directory (defense in depth against path traversal, even
    though stored_filename is always server-generated).
    """
    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    candidate = (upload_dir / stored_filename).resolve()

    if upload_dir not in candidate.parents and candidate != upload_dir:
        raise HTTPException(status_code=400, detail="Invalid file path.")
    if not str(candidate).startswith(str(upload_dir)):
        raise HTTPException(status_code=400, detail="Invalid file path.")

    return str(candidate)


def delete_file_safely(stored_filename: str) -> None:
    path = safe_upload_path(stored_filename)
    if os.path.exists(path):
        os.remove(path)
