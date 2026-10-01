"""Retrieval-augmented generation over the fab knowledge base.

Retrieval is hybrid by default: dense vector search in Chroma plus BM25 keyword
search, merged with Reciprocal Rank Fusion (RRF). Keyword search matters in a fab
because engineers search by exact identifiers (alarm codes like ALM-4021, doc IDs,
recipe names) that embedding models handle poorly.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from .config import Settings, get_settings
from .embeddings import get_embeddings

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-.][a-z0-9]+)*")
STOP = set("a an the of to and or for in on at is are be it this that with as by from what how do does when why which should i my".split())


def tokenize(text: str) -> List[str]:
    toks = TOKEN_RE.findall(text.lower())
    out = []
    for t in toks:
        if t in STOP:
            continue
        out.append(t)
        if "-" in t:  # index "alm-4021" and also "alm", "4021"
            out.extend(p for p in t.split("-") if p)
    return out


class BM25:
    def __init__(self, docs: List[Document], k1: float = 1.5, b: float = 0.75) -> None:
        self.docs = docs
        self.k1, self.b = k1, b
        self.tfs = [Counter(tokenize(d.page_content)) for d in docs]
        self.lens = [sum(tf.values()) for tf in self.tfs]
        self.avgdl = sum(self.lens) / max(len(self.lens), 1)
        df = Counter(t for tf in self.tfs for t in tf)
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def search(self, query: str, k: int) -> List[tuple[Document, float]]:
        q = tokenize(query)
        scores = []
        for i, tf in enumerate(self.tfs):
            s = 0.0
            for t in q:
                if t in tf:
                    f = tf[t]
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.lens[i] / self.avgdl))
            scores.append(s)
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [(self.docs[i], scores[i]) for i in order[:k] if scores[i] > 0]


def rrf_fuse(rankings: List[List[Document]], k: int = 60) -> List[tuple[Document, float]]:
    """Reciprocal Rank Fusion: score = sum(1 / (k + rank))."""
    scores: Dict[str, float] = {}
    by_id: Dict[str, Document] = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            cid = doc.metadata["chunk_id"]
            by_id[cid] = doc
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    return sorted(((by_id[c], s) for c, s in scores.items()), key=lambda x: x[1], reverse=True)


SYSTEM_PROMPT = """You are FabAssist, a troubleshooting assistant for semiconductor fab engineers and technicians.
Answer ONLY using the numbered context passages. Rules:
- Cite every factual statement with the passage number in brackets, e.g. [1] or [2][3].
- Give concrete steps, limits, and alarm codes exactly as written in the context.
- If the context does not contain the answer, say "I could not find this in the knowledge base" and suggest who to escalate to if the context mentions it. Never guess numbers or limits.
- If the question involves safety (gas leaks, chemicals, lockout), put the safety action first."""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Context passages:\n\n{context}\n\nQuestion: {question}"),
])


@dataclass
class Answer:
    question: str
    answer: str
    sources: List[dict] = field(default_factory=list)
    mode: str = ""
    error: str = ""


def get_llm(settings: Settings):
    p = settings.llm_provider.lower()
    if p == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=settings.anthropic_model, temperature=0, max_tokens=800)
    if p == "openai":
        from langchain_openai import ChatOpenAI

        model = settings.openai_model
        # Reasoning models (gpt-5.x, o-series) only accept the default temperature
        if model.startswith(("gpt-5", "o1", "o3", "o4")):
            return ChatOpenAI(model=model)
        return ChatOpenAI(model=model, temperature=0)
    if p == "none":
        return None
    raise ValueError(f"Unknown LLM_PROVIDER: {p}")


LLM_ERROR_HINTS = {
    "invalid_api_key": "The API key was rejected. Create a new key and paste the whole key into Secrets.",
    "insufficient_quota": "The account has no credit. Add billing credit on the provider's billing page.",
    "model_not_found": "This API key cannot use the configured model. Change OPENAI_MODEL / ANTHROPIC_MODEL.",
    "rate_limit_exceeded": "Rate limited. Wait a moment and try again.",
}


def explain_llm_error(e: Exception) -> str:
    """Turn a provider error into a short, key-free message."""
    text = str(getattr(e, "body", "") or "") + " " + str(e)
    code = getattr(e, "code", None) or (re.search(r"'code': '([a-z_]+)'", text) or [None, None])[1]
    if not code and "does not exist" in text:
        code = "model_not_found"
    hint = LLM_ERROR_HINTS.get(code or "", "Check the API key, billing, and model name.")
    return f"LLM call failed ({type(e).__name__}{', ' + code if code else ''}). {hint} Showing the retrieved passages instead."


class FabRAG:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.s = settings or get_settings()
        self.store = Chroma(
            collection_name=self.s.collection,
            embedding_function=get_embeddings(self.s.embedding_provider, self.s.openai_embedding_model),
            persist_directory=str(self.s.persist_dir),
        )
        raw = self.store.get(include=["documents", "metadatas"])
        if not raw["ids"]:
            raise RuntimeError("Vector store is empty. Run `python -m fabrag.ingest` first.")
        self.all_chunks = [Document(page_content=t, metadata=m) for t, m in zip(raw["documents"], raw["metadatas"])]
        self.bm25 = BM25(self.all_chunks)
        self.llm = get_llm(self.s)
        self.chain = PROMPT | self.llm if self.llm is not None else None

    # ---------- retrieval ----------
    def retrieve(self, question: str, k: Optional[int] = None, mode: Optional[str] = None) -> List[tuple[Document, float]]:
        k = k or self.s.top_k
        mode = mode or self.s.retrieval_mode
        pool = max(k * 4, 12)
        vec = self.store.similarity_search_with_score(question, k=pool)  # cosine distance
        if mode == "vector":
            return [(d, 1 - dist) for d, dist in vec[:k]]
        if mode == "bm25":
            return self.bm25.search(question, k)
        kw = self.bm25.search(question, pool)
        return rrf_fuse([[d for d, _ in vec], [d for d, _ in kw]])[:k]

    # ---------- generation ----------
    def ask(self, question: str, k: Optional[int] = None) -> Answer:
        hits = self.retrieve(question, k)
        sources = [{
            "n": i,
            "source": d.metadata.get("source"),
            "doc_id": d.metadata.get("doc_id"),
            "section": d.metadata.get("section"),
            "score": round(float(score), 4),
            "text": d.page_content,
        } for i, (d, score) in enumerate(hits, start=1)]

        if self.chain is None:
            return Answer(question, self._extractive(question, hits), sources, mode="extractive")

        context = "\n\n".join(f"[{s['n']}] ({s['doc_id']} - {s['section']})\n{s['text']}" for s in sources)
        try:
            msg = self.chain.invoke({"context": context, "question": question})
        except Exception as e:  # bad key, quota, network: degrade gracefully instead of crashing
            return Answer(question, self._extractive(question, hits), sources,
                          mode="extractive (LLM unavailable)", error=explain_llm_error(e))
        return Answer(question, msg.content if isinstance(msg.content, str) else str(msg.content), sources, mode=self.s.llm_provider)

    @staticmethod
    def _extractive(question: str, hits: List[tuple[Document, float]]) -> str:
        """No-LLM fallback: return the most relevant lines from the top passages."""
        if not hits:
            return "I could not find this in the knowledge base."
        q = set(tokenize(question))
        lines, seen = [], set()
        for n, (doc, _) in enumerate(hits[:3], start=1):
            for line in doc.page_content.splitlines()[1:]:
                if line.lstrip().startswith("#"):
                    continue
                line = re.sub(r"^[-*#\s]*(\d+\.\s+)?", "", line.strip())
                if len(line) > 25 and not line.startswith("[") and line not in seen and q & set(tokenize(line)):
                    seen.add(line)
                    lines.append((len(q & set(tokenize(line))), n, line))
        lines.sort(key=lambda x: -x[0])
        picked = lines[:6] or [(0, 1, hits[0][0].page_content[:400])]
        return "Most relevant passages from the knowledge base:\n" + "\n".join(f"- {t} [{n}]" for _, n, t in picked)
