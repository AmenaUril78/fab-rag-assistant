"""Streamlit chat UI.  Run:  python -m streamlit run app.py"""
import os
import time

import streamlit as st

# Copy Streamlit Cloud secrets into environment variables (stripping stray spaces/quotes)
# BEFORE the fabrag modules read their settings.
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ[_k] = _v.strip().strip('"').strip("'").strip()
except Exception:  # no secrets file locally: fine, .env / shell env is used instead
    pass

from fabrag.config import PROFILES, get_settings
from fabrag.ingest import LOADERS, build_index
from fabrag.rag import FabRAG, explain_llm_error

st.set_page_config(page_title="RAG Troubleshooting Assistant", page_icon="🔧", layout="wide")

LABELS = {"fab": "Semiconductor fab (demo)", "it": "IT / network ops (demo)", "private": "My documents (private)"}


def private_doc_count() -> int:
    d = PROFILES["private"].docs_dir
    if not d.exists():
        return 0
    return sum(1 for p in d.rglob("*") if p.is_file() and p.suffix.lower() in LOADERS
               and not (p.name == "README.md" and p.parent == d))


def key_fingerprint(name: str) -> str:
    key = os.getenv(name, "")
    if not key:
        return "not set"
    return f"{key[:8]}…{key[-4:]} ({len(key)} chars)"


@st.cache_resource
def load_rag(profile: str, mode: str, key_fp: str = "") -> FabRAG:
    settings = get_settings(profile, retrieval_mode=mode)
    if not (settings.persist_dir / "chroma.sqlite3").exists():
        # First run (e.g. on Streamlit Cloud or a fresh clone): build the vector DB automatically
        with st.spinner(f"Building the vector database for {settings.profile.name} (first run only)…"):
            build_index(settings)
    return FabRAG(settings)


# ---------------- sidebar ----------------
with st.sidebar:
    st.header("Settings")
    options = ["fab", "it"] + (["private"] if private_doc_count() else [])
    default = os.getenv("FABRAG_PROFILE", "fab")
    profile = st.selectbox("Knowledge base", options, format_func=LABELS.get,
                           index=options.index(default) if default in options else 0)
    mode = st.radio("Retrieval mode", ["hybrid", "vector", "bm25"], index=0,
                    help="Hybrid = vector search + BM25 keyword search fused with Reciprocal Rank Fusion")
    k = st.slider("Passages to retrieve (top-k)", 2, 8, 4)

    s = get_settings(profile)
    st.caption(f"Embeddings: `{s.embedding_provider}` · LLM: `{s.llm_provider}`")
    key_name = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}.get(s.llm_provider)
    if key_name:
        st.caption(f"API key: `{key_fingerprint(key_name)}`")
    if s.llm_provider == "openai":
        base = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        st.caption(f"Endpoint: `{base}` · Model: `{s.openai_model}`")
        if st.button("Check available models", use_container_width=True):
            try:
                from openai import OpenAI

                ids = sorted(m.id for m in OpenAI().models.list())
                st.success(f"Key works. {len(ids)} models available:")
                st.code("\n".join(ids[:60]) or "(none listed)")
            except Exception as e:
                st.error(explain_llm_error(e).replace(" Showing the retrieved passages instead.", ""))

    if st.button("Rebuild index", use_container_width=True,
                 help="Re-read every file in this knowledge base's folder. Use after adding or editing documents."):
        with st.spinner("Rebuilding…"):
            build_index(get_settings(profile))
        st.cache_resource.clear()
        st.rerun()
    if st.button("Clear chat", use_container_width=True):
        st.session_state[f"history_{profile}"] = []

    st.divider()
    st.markdown("**Try asking**")
    for ex in s.profile.examples:
        if st.button(ex, use_container_width=True, key=f"ex_{profile}_{ex}"):
            st.session_state.pending = ex

# ---------------- main ----------------
st.title(f"{s.profile.icon} {s.profile.name}")
st.caption(s.profile.subtitle)

try:
    rag = load_rag(profile, mode, key_fingerprint("OPENAI_API_KEY") + key_fingerprint("ANTHROPIC_API_KEY"))
except RuntimeError as e:
    st.info(f"{e}\n\nThen click **Rebuild index** in the sidebar.")
    st.stop()

docs = len({c.metadata.get("source") for c in rag.all_chunks})
st.caption(f"{docs} documents · {len(rag.all_chunks)} chunks indexed from `{s.docs_dir.name}/`")

hist_key = f"history_{profile}"
st.session_state.setdefault(hist_key, [])
for turn in st.session_state[hist_key]:
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
        if ans.error:
            st.warning(ans.error)
        st.markdown(ans.answer)
        st.caption(f"{time.time() - t0:.1f}s · mode: {ans.mode} · retrieval: {mode}")
        with st.expander(f"Sources ({len(ans.sources)})"):
            for src in ans.sources:
                label = f"{src['doc_id']} — " if src.get("doc_id") else ""
                st.markdown(f"**[{src['n']}] {label}{src['section']}**  \n`{src['source']}` · score {src['score']}")
                st.text(src["text"][:800])
    st.session_state[hist_key].append({"q": question, "a": ans.answer})
