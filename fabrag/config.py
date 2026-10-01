"""Central configuration, read from environment variables (or a .env file).

A *profile* is one knowledge base: its document folder, its own Chroma collection,
and its UI text. Built-in profiles:
  fab      - semiconductor fab troubleshooting (fictional sample docs)
  it       - IT / network operations runbooks (fictional sample docs)
  private  - your own documents in data/private/ (git-ignored, never pushed)
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent

try:  # optional: load .env if python-dotenv is installed
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass


@dataclass(frozen=True)
class Profile:
    key: str
    name: str
    icon: str
    subtitle: str
    docs_dir: Path
    audience: str
    extra_rules: str
    examples: List[str] = field(default_factory=list)


IT_RULES = ("- If the fix changes a production device, mention the change-management and rollback steps "
            "found in the context.\n- Show CLI commands exactly as written in the context, in code formatting.")

IT_EXAMPLES = [
    "Switch log shows %PM-4-ERR_DISABLE on a user port. How do I fix it?",
    "Users on the third floor get a 169.254 address. What should I check?",
    "The nightly config backup failed with an authentication error",
    "What do I need in the implementation plan for a normal change?",
    "A site name won't resolve but the IP works. How do I troubleshoot DNS?",
]

PROFILES = {
    "fab": Profile(
        key="fab", name="FabAssist", icon="🔧",
        subtitle="RAG assistant over fab SOPs, troubleshooting guides, alarm codes, and lessons learned. "
                 "Sample knowledge base is fictional.",
        docs_dir=ROOT / "data" / "fab",
        audience="semiconductor fab engineers and technicians",
        extra_rules="- If the question involves safety (gas leaks, chemicals, lockout), put the safety action first.",
        examples=[
            "Tool shows ALM-4021. What should I do?",
            "What must pass before a PECVD tool is released after PM?",
            "Overlay is out of spec after a reticle change. What could cause it?",
            "How often do we change the SC1 bath?",
            "I smell an unusual odor near a gas cabinet.",
        ],
    ),
    "it": Profile(
        key="it", name="OpsAssist", icon="🖧",
        subtitle="RAG assistant over IT and network operations runbooks, error references, and postmortems. "
                 "Sample knowledge base is fictional.",
        docs_dir=ROOT / "data" / "it",
        audience="IT and network operations staff",
        extra_rules=IT_RULES,
        examples=IT_EXAMPLES,
    ),
    "private": Profile(
        key="private", name="My Runbooks", icon="🗂️",
        subtitle="RAG assistant over your own documents in data/private/ (never pushed to GitHub).",
        docs_dir=Path(os.getenv("PRIVATE_DOCS_DIR", ROOT / "data" / "private")),
        audience="IT and network operations staff",
        extra_rules=IT_RULES,
        examples=[],  # your documents, your questions: no demo examples here
    ),
}


@dataclass(frozen=True)
class Settings:
    profile: Profile
    docs_dir: Path
    persist_dir: Path
    collection: str

    # Embeddings: "minilm" (local ONNX all-MiniLM-L6-v2, free), "openai", or "hashing" (offline, for tests)
    embedding_provider: str = "minilm"
    openai_embedding_model: str = "text-embedding-3-small"

    # LLM: "anthropic", "openai" (also any OpenAI-compatible server such as Ollama), or "none"
    llm_provider: str = "anthropic"
    anthropic_model: str = "claude-sonnet-5-5"
    openai_model: str = "gpt-5.6-luna"

    chunk_size: int = 700
    chunk_overlap: int = 100
    top_k: int = 4
    # Retrieval: "hybrid" (vector + BM25 fused with RRF), "vector", or "bm25"
    retrieval_mode: str = "hybrid"


def get_settings(profile: str | None = None, **overrides) -> Settings:
    """Build settings from env vars (read at call time) plus explicit overrides."""
    key = profile or os.getenv("FABRAG_PROFILE", "fab")
    if key not in PROFILES:
        raise ValueError(f"Unknown profile '{key}'. Choose from: {', '.join(PROFILES)}")
    p = PROFILES[key]
    docs_env = os.getenv("FABRAG_DOCS_DIR") if key != "private" else None
    s = Settings(
        profile=p,
        docs_dir=Path(docs_env) if docs_env else p.docs_dir,
        persist_dir=Path(os.getenv("FABRAG_CHROMA_DIR", ROOT / "chroma_db")) / key,
        collection=f"{key}_knowledge",
        embedding_provider=os.getenv("EMBEDDING_PROVIDER", "minilm"),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        llm_provider=os.getenv("LLM_PROVIDER", "anthropic"),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "700")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "100")),
        top_k=int(os.getenv("TOP_K", "4")),
        retrieval_mode=os.getenv("RETRIEVAL_MODE", "hybrid"),
    )
    return replace(s, **overrides) if overrides else s
