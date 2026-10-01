# Retrieval Evaluation: OpsAssist (it)

Questions: 27 · Embeddings: `minilm` · Chunks: 56 · LLM: llama3.2 (Ollama, local)

| Retrieval | Doc Hit@1 | Doc Hit@3 | Section Hit@3 | MRR | Hit@3 (semantic) | Hit@3 (exact ID) |
|---|---|---|---|---|---|---|
| vector | 89% | 100% | 100% | 0.94 | 100% | 100% |
| bm25 | 81% | 96% | 89% | 0.90 | 95% | 100% |
| hybrid | 93% | 100% | 100% | 0.96 | 100% | 100% |

## Hybrid misses (not in top 3)

- none

## Generation checks

- Answers with citations: 67%
- Correct abstention on out-of-scope questions: 100%
- Average latency: 2.4s
