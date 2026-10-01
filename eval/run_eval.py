"""Retrieval evaluation: compare vector, BM25, and hybrid retrieval.

Metrics (per question, then averaged):
  - Doc Hit@1 / Hit@3: correct source document appears in the top 1 / top 3 chunks
  - Section Hit@3:     correct document AND section appears in the top 3
  - MRR:               mean reciprocal rank of the first chunk from the correct document

Usage:  python -m eval.run_eval            (retrieval metrics, no API key needed)
        python -m eval.run_eval --generate (also calls the LLM and checks citations)
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from fabrag.config import get_settings
from fabrag.rag import FabRAG

HERE = Path(__file__).parent

UNANSWERABLE = [
    "What is the cafeteria menu for Friday?",
    "What is the maximum ion implant dose for the source/drain step?",
]


def evaluate(rag: FabRAG, questions: list, mode: str, k: int = 5) -> dict:
    rows, totals = [], {"hit1": 0, "hit3": 0, "sec3": 0, "mrr": 0.0}
    by_type: dict = {}
    for item in questions:
        hits = rag.retrieve(item["q"], k=k, mode=mode)
        srcs = [d.metadata["source"] for d, _ in hits]
        secs = [(d.metadata["source"], d.metadata.get("section")) for d, _ in hits]
        rank = next((i for i, s in enumerate(srcs, 1) if s == item["source"]), None)
        hit1 = int(rank == 1)
        hit3 = int(rank is not None and rank <= 3)
        if item.get("section"):
            sec3 = int((item["source"], item["section"]) in secs[:3])
        else:
            sec3 = hit3
        rr = 1.0 / rank if rank else 0.0
        for key, v in (("hit1", hit1), ("hit3", hit3), ("sec3", sec3), ("mrr", rr)):
            totals[key] += v
        t = by_type.setdefault(item["type"], {"n": 0, "hit3": 0})
        t["n"] += 1
        t["hit3"] += hit3
        rows.append({**item, "rank": rank, "top3": srcs[:3]})
    n = len(questions)
    return {"mode": mode, **{k_: v / n for k_, v in totals.items()},
            "by_type": {t: v["hit3"] / v["n"] for t, v in by_type.items()}, "rows": rows}


def check_generation(rag: FabRAG, questions: list) -> dict:
    cited, abstained, latencies = 0, 0, []
    for item in questions:
        t0 = time.time()
        a = rag.ask(item["q"])
        latencies.append(time.time() - t0)
        cited += bool(re.search(r"\[\d\]", a.answer))
    for q in UNANSWERABLE:
        a = rag.ask(q)
        abstained += "could not find" in a.answer.lower()
    return {"citation_rate": cited / len(questions), "abstention_rate": abstained / len(UNANSWERABLE),
            "avg_latency_s": sum(latencies) / len(latencies)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true", help="also evaluate LLM answers (needs API key)")
    args = ap.parse_args()

    questions = json.loads((HERE / "questions.json").read_text())
    s = get_settings()
    rag = FabRAG(s)
    results = [evaluate(rag, questions, m) for m in ("vector", "bm25", "hybrid")]

    lines = [f"# Retrieval Evaluation\n",
             f"Questions: {len(questions)} · Embeddings: `{s.embedding_provider}` · "
             f"Chunks: {len(rag.all_chunks)}\n",
             "| Retrieval | Doc Hit@1 | Doc Hit@3 | Section Hit@3 | MRR | Hit@3 (semantic) | Hit@3 (exact ID) |",
             "|---|---|---|---|---|---|---|"]
    for r in results:
        bt = r["by_type"]
        lines.append(f"| {r['mode']} | {r['hit1']:.0%} | {r['hit3']:.0%} | {r['sec3']:.0%} | {r['mrr']:.2f} | "
                     f"{bt.get('semantic', 0):.0%} | {bt.get('exact-id', 0):.0%} |")

    misses = [row for row in results[-1]["rows"] if not row["rank"] or row["rank"] > 3]
    lines.append("\n## Hybrid misses (not in top 3)\n")
    lines += [f"- {m['q']} → expected `{m['source']}`, got {m['top3']}" for m in misses] or ["- none"]

    if args.generate:
        g = check_generation(rag, questions)
        lines += ["\n## Generation checks\n",
                  f"- Answers with citations: {g['citation_rate']:.0%}",
                  f"- Correct abstention on out-of-scope questions: {g['abstention_rate']:.0%}",
                  f"- Average latency: {g['avg_latency_s']:.1f}s"]

    report = "\n".join(lines)
    print(report)
    (HERE / f"results_{s.embedding_provider}.md").write_text(report + "\n")


if __name__ == "__main__":
    main()
