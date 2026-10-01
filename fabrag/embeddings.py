"""Embedding providers, all exposed through LangChain's Embeddings interface."""
from __future__ import annotations

from typing import List

import numpy as np
from langchain_core.embeddings import Embeddings


class MiniLMEmbeddings(Embeddings):
    """Local all-MiniLM-L6-v2 via Chroma's bundled ONNX runtime.

    Free, no API key, ~80 MB model downloaded on first use. 384-dim vectors.
    """

    def __init__(self) -> None:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

        self._fn = DefaultEmbeddingFunction()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [np.asarray(v, dtype=float).tolist() for v in self._fn(texts)]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


class HashingEmbeddings(Embeddings):
    """Offline, dependency-light embeddings (hashed word + character n-grams).

    Not semantic like a neural model, but deterministic and fast. Used for unit
    tests and environments without internet access.
    """

    def __init__(self, n_features: int = 2048) -> None:
        from sklearn.feature_extraction.text import HashingVectorizer

        self._word = HashingVectorizer(n_features=n_features, ngram_range=(1, 2),
                                       alternate_sign=False, norm=None, stop_words="english")
        self._char = HashingVectorizer(n_features=n_features, analyzer="char_wb",
                                       ngram_range=(3, 5), alternate_sign=False, norm=None)

    def _embed(self, texts: List[str]) -> List[List[float]]:
        w = self._word.transform(texts).toarray()
        c = self._char.transform(texts).toarray()
        m = np.hstack([np.log1p(w) * 2.0, np.log1p(c)])
        m /= np.linalg.norm(m, axis=1, keepdims=True) + 1e-12
        return m.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]


def get_embeddings(provider: str, openai_model: str = "text-embedding-3-small") -> Embeddings:
    provider = provider.lower()
    if provider == "minilm":
        return MiniLMEmbeddings()
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=openai_model)
    if provider == "hashing":
        return HashingEmbeddings()
    raise ValueError(f"Unknown EMBEDDING_PROVIDER: {provider}")
