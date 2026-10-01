"""Offline tests (no API keys, no model downloads): hashing embeddings + extractive mode."""
import pytest

from fabrag.config import get_settings
from fabrag.ingest import build_index, load_documents, split_documents
from fabrag.rag import FabRAG, rrf_fuse, tokenize


@pytest.fixture(scope="module")
def rag(tmp_path_factory):
    s = get_settings(persist_dir=tmp_path_factory.mktemp("chroma"), embedding_provider="hashing",
                     llm_provider="none")
    build_index(s)
    return FabRAG(s)


def test_chunks_keep_section_metadata():
    s = get_settings()
    chunks = split_documents(load_documents(s.docs_dir), 700, 100)
    assert len(chunks) > 20
    assert all(c.metadata["section"] and c.metadata["source"] for c in chunks)
    assert len({c.metadata["chunk_id"] for c in chunks}) == len(chunks)


def test_tokenizer_keeps_alarm_codes():
    toks = tokenize("Tool shows ALM-4021 again")
    assert "alm-4021" in toks and "4021" in toks


def test_rrf_prefers_docs_ranked_high_in_both_lists(rag):
    a, b, c = rag.all_chunks[:3]
    fused = rrf_fuse([[a, b, c], [b, a, c]])
    assert {fused[0][0].metadata["chunk_id"], fused[1][0].metadata["chunk_id"]} == {
        a.metadata["chunk_id"], b.metadata["chunk_id"]}


@pytest.mark.parametrize("q,expected", [
    ("What do I do for ALM-4021?", "alarm_code_reference.md"),
    ("when should the polishing pad be replaced", "cmp_process_guide.md"),
    ("gas leak response", "safety_lockout_gas.md"),
])
def test_hybrid_retrieval_finds_right_doc(rag, q, expected):
    hits = rag.retrieve(q, k=3)
    assert expected in [d.metadata["source"] for d, _ in hits]


def test_ask_returns_cited_sources(rag):
    ans = rag.ask("How often do we change the SC1 bath?")
    assert ans.sources and ans.sources[0]["n"] == 1
    assert "[1]" in ans.answer


def test_api_endpoints(rag, monkeypatch):
    from fastapi.testclient import TestClient

    import api

    monkeypatch.setattr(api, "get_rag", lambda: rag)
    client = TestClient(api.app)
    assert client.get("/health").json()["status"] == "ok"
    r = client.post("/ask", json={"question": "What is CVD-2210?", "top_k": 3})
    assert r.status_code == 200 and len(r.json()["sources"]) == 3
    r = client.post("/search", json={"query": "overlay", "mode": "bm25"})
    assert r.status_code == 200 and r.json()
