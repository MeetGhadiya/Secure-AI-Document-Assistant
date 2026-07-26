"""
Central configuration for the Secure Document RAG backend.
Loads settings from environment variables (see .env.example).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    # --- Gemini / LLM ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # --- Storage paths ---
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", str(BASE_DIR / "chroma_db"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "app.db"))

    # --- Upload constraints ---
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}

    # --- Chunking ---
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # --- Retrieval ---
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))

    # --- Embeddings ---
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # --- CORS ---
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # --- Session ---
    SESSION_HEADER: str = "X-Session-Id"


settings = Settings()

# Ensure required directories exist at import time.
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
