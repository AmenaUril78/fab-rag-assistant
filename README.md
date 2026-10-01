# RAG Troubleshooting Assistant: FabAssist and OpsAssist

One hybrid-retrieval RAG pipeline, three knowledge bases you can switch between in the app:

| Profile | For | Documents |
|---|---|---|
| **FabAssist** (`fab`) | Semiconductor fab engineers and technicians | Fictional SOPs, alarm codes, SPC rules, lessons learned (`data/fab/`) |
| **OpsAssist** (`it`) | IT / network operations | Fictional switch, DHCP, DNS, backup, change-management runbooks, syslog reference, postmortems (`data/it/`) |
| **My documents** (`private`) | Your own work | Anything you drop in `data/private/` (md, txt, pdf, docx, html), **never pushed to GitHub** |

FabAssist answers fab engineers' and technicians' questions ("Tool shows ALM-4021, what do I do?", "Overlay is out of spec after a reticle change") from a knowledge base of SOPs, troubleshooting guides, alarm-code references and lessons-learned reports. Every answer cites the passages it came from.

It is built as a forward-deployed prototype: quick to stand up, measurable, and structured so it could be handed to an IT or MLOps team for production.

**Live demo:** [fab-rag-assistant.streamlit.app](https://fab-rag-assistant-5cbn4sjjp4ntn6toyayd8s.streamlit.app) (runs in retrieval-only mode, with no LLM key, showing cited passages). The full generative version runs locally with a free open-source model via [Ollama](#run-fully-local-with-ollama-no-api-key).

![FabAssist answering a question with Llama 3.2 running locally](docs/screenshot.png)

### FabAssist results (28 labeled questions, MiniLM embeddings, Llama 3.2 via Ollama)

| Retrieval | Doc Hit@1 | Doc Hit@3 | Section Hit@3 | MRR | Hit@3 (exact ID lookups) |
|---|---|---|---|---|---|
| Vector only | 96% | 96% | 86% | 0.96 | 83% |
| BM25 only | 89% | 100% | 96% | 0.95 | 100% |
| **Hybrid (RRF)** | **100%** | **100%** | **100%** | **1.00** | **100%** |

Hybrid retrieval fixed the cases each method missed on its own: vector search missed exact alarm-code and document-ID lookups, and BM25 missed paraphrased questions at rank 1.

| Generation check | Result |
|---|---|
| Answers that include citations | 82% |
| Correct "not found" on out-of-scope questions | 100% (2 of 2) |
| Average latency (local Llama 3.2, Apple Silicon) | 1.7 s |

### OpsAssist results (27 labeled IT questions, MiniLM embeddings, Llama 3.2 via Ollama)

| Retrieval | Doc Hit@1 | Doc Hit@3 | Section Hit@3 | MRR |
|---|---|---|---|---|
| Vector only | 89% | 100% | 100% | 0.94 |
| BM25 only | 81% | 96% | 89% | 0.90 |
| **Hybrid (RRF)** | **93%** | **100%** | **100%** | **0.96** |

Generation: 67% of answers included citations, 100% correct "not found" on out-of-scope questions, 2.4 s average latency. The lower citation rate comes from the small 3B local model sometimes answering without bracketed citations; a larger model or a citation-enforcing output format is the next fix.

*Limitations: the evaluation set is small and was written alongside the documents, so these numbers show the method works, not production accuracy. Next steps are a larger engineer-labeled set and a re-ranker.*

> The sample knowledge bases in `data/fab/` and `data/it/` are **fictional**. They were written for this project to resemble real documentation and do not describe any real organization.

## Architecture

```mermaid
flowchart LR
    A[Markdown SOPs / guides] --> B[Section-aware chunking<br/>LangChain splitters]
    B --> C[Embeddings<br/>MiniLM / OpenAI]
    C --> D[(Chroma<br/>vector DB)]
    B --> E[BM25 keyword index]
    Q[User question] --> D & E
    D --> F[Reciprocal Rank Fusion]
    E --> F
    F --> G[Prompt with numbered context<br/>LangChain + Claude / GPT]
    G --> H[Cited answer]
    H --> UI[Streamlit UI] & API[FastAPI /ask]
```

**Design decisions**
- **Hybrid retrieval (vector + BM25 with RRF).** Engineers search by exact identifiers such as alarm codes (`ALM-4021`), document IDs and incident numbers. Embedding models blur those. BM25 catches exact matches, vectors catch paraphrases ("line width keeps moving" → CD drift), and RRF merges the two lists without tuning score scales.
- **Section-aware chunking.** Documents are split on markdown headers first, so a troubleshooting procedure stays together. Each chunk is prefixed with `[Document > Section]` so it keeps its context.
- **Grounded prompting.** The model must cite passage numbers, must not guess numeric limits, must say "I could not find this" when the answer isn't in context, and must put safety actions first.
- **Pluggable providers.** Embeddings (`minilm` local/free, `openai`, `hashing` offline) and the LLM (`anthropic`, `openai`, `none` = extractive) are set by environment variables. With `LLM_PROVIDER=none` the app runs with no API key.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # add your ANTHROPIC_API_KEY (or set LLM_PROVIDER=none)

python -m fabrag.ingest --profile fab   # chunk + embed + store (the app also does this on first launch)
python -m streamlit run app.py   # chat UI at http://localhost:8501
uvicorn api:app --reload         # REST API, docs at http://localhost:8000/docs
```

### Use it with your own work documents

1. Copy your runbooks, SOPs, and notes into `data/private/`. Subfolders are fine. Supported: `.md`, `.txt`, `.pdf`, `.docx`, `.html`.
2. Start the app, choose **My documents (private)** in the sidebar, and click **Rebuild index**. Click it again whenever you add or edit files.
3. Use Ollama (below) so documents and questions never leave your computer.

`data/private/` is listed in `.gitignore`, and a test checks that it stays ignored, so your files are not committed or pushed. Check your organization's data policy before using internal documents with any AI tool, and treat answers as a pointer to the right runbook, not a replacement for it: always open the cited source before changing a production device.

### Run fully local with Ollama (no API key)

1. Install [Ollama](https://ollama.com) and run `ollama pull llama3.2`.
2. Put this in `.env`:
   ```
   LLM_PROVIDER=openai
   OPENAI_BASE_URL=http://localhost:11434/v1
   OPENAI_API_KEY=ollama
   OPENAI_MODEL=llama3.2
   EMBEDDING_PROVIDER=minilm
   ```
3. `python -m streamlit run app.py`

Everything (embeddings, vector search, and generation) stays on your machine, which matters in a fab where documents often cannot leave the site. Any OpenAI-compatible endpoint works the same way by changing `OPENAI_BASE_URL`.

API example:
```bash
curl -X POST localhost:8000/ask -H "Content-Type: application/json" \
     -d '{"question": "What do I do for ALM-4021?", "top_k": 4}'
```

## Evaluation

`eval/questions_fab.json` (28 questions) and `eval/questions_it.json` (27 questions) contain paraphrased "semantic" questions plus "exact-ID" lookups (alarm codes, syslog mnemonics, exception names, document IDs). Each one is labeled with the expected document and section.

```bash
python -m eval.run_eval --profile fab              # retrieval metrics: vector vs BM25 vs hybrid
python -m eval.run_eval --profile it --generate    # also citation rate, out-of-scope abstention, latency
```

Metrics are Doc Hit@1, Doc Hit@3, Section Hit@3 and MRR, broken down by question type. Results are written to `eval/results_<embedding>.md`.

## Tests

```bash
pytest -q     # runs fully offline: hashing embeddings + extractive mode, includes FastAPI endpoint tests
```

## Project layout

```
fabrag/config.py      profiles (fab, it, private) and settings from env vars
fabrag/embeddings.py  MiniLM (ONNX) / OpenAI / hashing embeddings behind LangChain's Embeddings interface
fabrag/ingest.py      load md/txt/pdf/docx/html → section-aware chunk → embed → Chroma
fabrag/rag.py         BM25, RRF hybrid retrieval, grounded prompt, LLM call, extractive fallback
app.py                Streamlit chat UI: knowledge-base switcher, rebuild index, source viewer, retrieval-mode toggle
api.py                FastAPI: /health, /ask, /search
eval/                 labeled question set + evaluation script
tests/                pytest suite
data/fab/             fictional fab knowledge base (9 documents)
data/it/              fictional IT / network ops knowledge base (9 documents)
data/private/         your own documents (git-ignored)
```

## Path to production (what I'd do next)

- Connect real document sources (SharePoint/Confluence) with incremental re-indexing on document change.
- Enforce document-level access control by filtering on metadata at retrieval time.
- Add a cross-encoder re-ranker and run evaluation on a larger, engineer-labeled question set.
- Log questions, retrieved chunks and user feedback (thumbs up/down) to find gaps in the knowledge base.
- Containerize (Docker), add CI that runs `pytest` and the retrieval eval, and fail the build if Hit@3 regresses.
