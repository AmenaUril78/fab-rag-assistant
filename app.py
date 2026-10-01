"""Streamlit chat UI for FabAssist.  Run:  streamlit run app.py"""
import time

import streamlit as st

from fabrag.config import get_settings
from fabrag.ingest import build_index
from fabrag.rag import FabRAG

st.set_page_config(page_title="FabAssist", page_icon="🔧", layout="wide")


@st.cache_resource
def load_rag(mode: str) -> FabRAG:
    settings = get_settings(retrieval_mode=mode)
    if not (settings.persist_dir / "chroma.sqlite3").exists():
        # First run (e.g. on Streamlit Cloud or Codespaces): build the vector DB automatically
        with st.spinner("Building the vector database (first run only)…"):
            build_index(settings)
    return FabRAG(settings)


with st.sidebar:
    st.header("Settings")
    mode = st.radio("Retrieval mode", ["hybrid", "vector", "bm25"], index=0,
                    help="Hybrid = vector search + BM25 keyword search fused with Reciprocal Rank Fusion")
    k = st.slider("Passages to retrieve (top-k)", 2, 8, 4)
    s = get_settings()
    st.caption(f"Embeddings: `{s.embedding_provider}` · LLM: `{s.llm_provider}`")
    st.divider()
    st.markdown("**Try asking**")
    examples = [
        "Tool shows ALM-4021. What should I do?",
        "What must pass before a PECVD tool is released after PM?",
        "Overlay is out of spec after a reticle change. What could cause it?",
        "How often do we change the SC1 bath?",
        "I smell an unusual odor near a gas cabinet.",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.pending = ex

st.title("🔧 FabAssist")
st.caption("RAG assistant over fab SOPs, troubleshooting guides, alarm codes, and lessons learned. "
           "Sample knowledge base is fictional.")

rag = load_rag(mode)
if "history" not in st.session_state:
    st.session_state.history = []

for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["q"])
    with st.chat_message("assistant"):
        st.markdown(turn["a"])

question = st.chat_input("Describe the problem or ask about a procedure…") or st.session_state.pop("pending", None)
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        t0 = time.time()
        with st.spinner("Searching knowledge base…"):
            ans = rag.ask(question, k=k)
        st.markdown(ans.answer)
        st.caption(f"{time.time() - t0:.1f}s · mode: {ans.mode} · retrieval: {mode}")
        with st.expander(f"Sources ({len(ans.sources)})"):
            for src in ans.sources:
                st.markdown(f"**[{src['n']}] {src['doc_id']} — {src['section']}**  \n"
                            f"`{src['source']}` · score {src['score']}")
                st.text(src["text"][:800])
    st.session_state.history.append({"q": question, "a": ans.answer})
