"""Streamlit chat UI.  Run:  python -m streamlit run app.py"""
import os
import time
from pathlib import Path

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
from fabrag.ingest import LOADERS, build_index, docs_fingerprint, index_is_current, list_doc_files
from fabrag.rag import FabRAG, explain_llm_error

st.set_page_config(page_title="RAG Troubleshooting Assistant", page_icon="🔧", layout="wide")

LABELS = {"fab": "Semiconductor fab (demo)", "it": "IT / network ops (demo)", "private": "My documents (private)"}
# The public Streamlit Cloud app never offers "My documents" or uploads; your laptop always does.
IS_LOCAL = not Path("/mount/src").exists() and os.getenv("FABRAG_PUBLIC") != "1"
UPLOAD_TYPES = [ext.lstrip(".") for ext in LOADERS]


def key_fingerprint(name: str) -> str:
    key = os.getenv(name, "")
    if not key:
        return "not set"
    return f"{key[:8]}…{key[-4:]} ({len(key)} chars)"


@st.cache_resource
def load_rag(profile: str, mode: str, key_fp: str = "", docs_fp: str = "") -> FabRAG:
    settings = get_settings(profile, retrieval_mode=mode)
    if not index_is_current(settings):
        # First run, or files were added / edited / removed: (re)build automatically
        with st.spinner(f"Reading your documents for {settings.profile.name}…"):
            build_index(settings)
    return FabRAG(settings)


def documents_panel(docs_dir: Path) -> None:
    """Add / remove files for the private knowledge base, right in the app."""
    files = list_doc_files(docs_dir)
    with st.expander(f"📄 Your documents ({len(files)}) · add or remove", expanded=not files):
        st.session_state.setdefault("upload_n", 0)
        uploads = st.file_uploader("Drop runbooks here (PDF, Word, Markdown, text, HTML)", type=UPLOAD_TYPES,
                                   accept_multiple_files=True, key=f"up_{st.session_state.upload_n}")
        if uploads:
            docs_dir.mkdir(parents=True, exist_ok=True)
            for f in uploads:
                (docs_dir / Path(f.name).name).write_bytes(f.getbuffer())
            st.session_state.upload_n += 1  # reset the uploader so files are saved only once
            st.rerun()
        for f in files:
            c1, c2 = st.columns([6, 1])
            c1.markdown(f"`{f.relative_to(docs_dir)}`")
            if c2.button("Remove", key=f"rm_{f}"):
                f.unlink()
                st.rerun()
        st.caption(f"Saved only on this computer in `{docs_dir}` (never uploaded to GitHub). "
                   "New, edited, or removed files are picked up automatically.")


# ---------------- sidebar ----------------
with st.sidebar:
    st.header("Settings")
    options = (["private"] if IS_LOCAL else []) + ["fab", "it"]
    default = os.getenv("FABRAG_PROFILE") or ("private" if IS_LOCAL else "fab")
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

if profile == "private":
    documents_panel(s.docs_dir)
    if not list_doc_files(s.docs_dir):
        st.info("Add a few runbooks above to get started. Then ask a question in the box below.")
        st.stop()

rag = load_rag(profile, mode, key_fingerprint("OPENAI_API_KEY") + key_fingerprint("ANTHROPIC_API_KEY"),
               docs_fingerprint(s.docs_dir))

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
