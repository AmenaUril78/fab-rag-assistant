"""Load markdown documents, split them into chunks, and index them in Chroma.

Usage:  python -m fabrag.ingest
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from .config import Settings, get_settings
from .embeddings import get_embeddings

DOC_ID_RE = re.compile(r"Document IDs?:\s*([A-Z0-9\-, ]+?)\s*\|")


def load_documents(docs_dir: Path) -> List[Document]:
    docs = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        m = DOC_ID_RE.search(text)
        docs.append(Document(page_content=text, metadata={
            "source": path.name,
            "title": title,
            "doc_id": m.group(1).strip() if m else "",
        }))
    return docs


def split_documents(docs: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
    """Split by markdown section first (keeps procedures together), then by size."""
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "section")], strip_headers=False
    )
    size_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks: List[Document] = []
    for doc in docs:
        for section in header_splitter.split_text(doc.page_content):
            sec_name = section.metadata.get("section", "Overview")
            for i, piece in enumerate(size_splitter.split_text(section.page_content)):
                # Prefix with doc title + section so each chunk carries its own context
                content = f"[{doc.metadata['title']} > {sec_name}]\n{piece}"
                meta = {**doc.metadata, "section": sec_name}
                meta["chunk_id"] = f"{doc.metadata['source']}::{sec_name}::{i}"
                chunks.append(Document(page_content=content, metadata=meta))
    return chunks


def build_index(settings: Settings | None = None, reset: bool = True) -> Chroma:
    s = settings or get_settings()
    if reset and s.persist_dir.exists():
        shutil.rmtree(s.persist_dir)

    docs = load_documents(s.docs_dir)
    chunks = split_documents(docs, s.chunk_size, s.chunk_overlap)
    store = Chroma(
        collection_name=s.collection,
        embedding_function=get_embeddings(s.embedding_provider, s.openai_embedding_model),
        persist_directory=str(s.persist_dir),
        collection_metadata={"hnsw:space": "cosine", "embedding_provider": s.embedding_provider},
    )
    store.add_documents(chunks, ids=[c.metadata["chunk_id"] for c in chunks])
    print(f"Indexed {len(chunks)} chunks from {len(docs)} documents into {s.persist_dir} "
          f"(embeddings: {s.embedding_provider})")
    return store


if __name__ == "__main__":
    build_index()
