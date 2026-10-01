"""FastAPI service for FabAssist.  Run:  uvicorn api:app --reload"""
from functools import lru_cache
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from fabrag.config import get_settings
from fabrag.rag import FabRAG

app = FastAPI(title="FabAssist API", version="1.0",
              description="Retrieval-augmented Q&A over fab troubleshooting documents.")


@lru_cache
def get_rag() -> FabRAG:
    return FabRAG()


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["What do I do for ALM-4021?"])
    top_k: int = Field(4, ge=1, le=10)


class Source(BaseModel):
    n: int
    source: str
    doc_id: Optional[str] = None
    section: Optional[str] = None
    score: float
    text: str


class AskResponse(BaseModel):
    answer: str
    mode: str
    sources: List[Source]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(5, ge=1, le=20)
    mode: Literal["hybrid", "vector", "bm25"] = "hybrid"


@app.get("/health")
def health():
    s = get_settings()
    return {"status": "ok", "chunks": len(get_rag().all_chunks),
            "embeddings": s.embedding_provider, "llm": s.llm_provider}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        a = get_rag().ask(req.question, k=req.top_k)
    except Exception as e:  # surface provider/config errors clearly
        raise HTTPException(status_code=500, detail=str(e))
    return AskResponse(answer=a.answer, mode=a.mode, sources=a.sources)


@app.post("/search")
def search(req: SearchRequest):
    """Retrieval only (no LLM) — useful for debugging relevance."""
    hits = get_rag().retrieve(req.query, k=req.top_k, mode=req.mode)
    return [{"source": d.metadata["source"], "section": d.metadata.get("section"),
             "score": round(float(s), 4), "text": d.page_content} for d, s in hits]
