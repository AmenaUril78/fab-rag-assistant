"""Central configuration, read from environment variables (or a .env file)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:  # optional: load .env if python-dotenv is installed
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass


@dataclass(frozen=True)
class Settings:
    docs_dir: Path = Path(os.getenv("FABRAG_DOCS_DIR", ROOT / "data" / "docs"))
    persist_dir: Path = Path(os.getenv("FABRAG_CHROMA_DIR", ROOT / "chroma_db"))
    collection: str = os.getenv("FABRAG_COLLECTION", "fab_knowledge")

    # Embeddings: "minilm" (local ONNX all-MiniLM-L6-v2, free), "openai", or "hashing" (offline, for tests)
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "minilm")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # LLM: "anthropic", "openai", or "none" (extractive answer, no API key needed)
    llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    chunk_size: int = int(os.getenv("CHUNK_SIZE", "700"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    top_k: int = int(os.getenv("TOP_K", "4"))
    # Retrieval: "hybrid" (vector + BM25 fused with RRF) or "vector"
    retrieval_mode: str = os.getenv("RETRIEVAL_MODE", "hybrid")


def get_settings(**overrides) -> Settings:
    s = Settings()
    if overrides:
        from dataclasses import replace

        s = replace(s, **overrides)
    return s
