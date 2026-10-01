# Retrieval Evaluation

Questions: 28 · Embeddings: `minilm` · Chunks: 59 · LLM: llama3.2 (Ollama, local)

| Retrieval | Doc Hit@1 | Doc Hit@3 | Section Hit@3 | MRR | Hit@3 (semantic) | Hit@3 (exact ID) |
|---|---|---|---|---|---|---|
| vector | 96% | 96% | 86% | 0.96 | 100% | 83% |
| bm25 | 89% | 100% | 96% | 0.95 | 100% | 100% |
| hybrid | 100% | 100% | 100% | 1.00 | 100% | 100% |

## Hybrid misses (not in top 3)

- none

## Generation checks

- Answers with citations: 82%
- Correct abstention on out-of-scope questions: 100%
- Average latency: 1.7s
