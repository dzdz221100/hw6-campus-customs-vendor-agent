"""Problem 4: does reusing the handbook from cache actually save money?

Runs the vendor desk agent on all 12 data/practice_docs/*.{html,pdf,eml} twice:

  - "without_cache": every call gets a unique random token glued onto the very front of the
    system prompt, so the full prompt is different every time and there is nothing for prompt
    caching to match -- cache_read_tokens must come back 0 on every single call here.
  - "with_cache": the system prompt is the normal fixed handbook + instructions text (same as
    a real `python agent.py --doc ...` run), run back-to-back on all 12 documents so later
    calls can actually hit the cache the first call writes.

Every one of the 24 calls is recorded to output/cache_test.json (setup, document, every token
count the API reports, and the dollar cost from data/prices.json). This file is overwritten
fresh each time this script runs -- it's a one-shot measurement, not a growing log like
output/usage_log.json (which still gets all 24 calls appended too, since run_agent() always
logs a normal run there regardless of who's calling it).

Usage:
    python run_cache_test.py
"""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path

from agent import MODEL_NAME, PRICES_PATH, ROOT, compute_cost, run_agent

PRACTICE_DOCS_DIR = ROOT / "data" / "practice_docs"
CACHE_TEST_PATH = ROOT / "output" / "cache_test.json"


def list_practice_docs() -> list[Path]:
    return sorted(PRACTICE_DOCS_DIR.iterdir(), key=lambda p: p.name)


async def run_setup(setup: str, docs: list[Path], prices: dict) -> list[dict]:
    records = []
    for doc in docs:
        doc_rel = str(doc.relative_to(ROOT))
        # A fresh uuid4 per call: every "without_cache" prompt is unique, so no two calls in
        # this script (or any earlier/later run) can ever share a cacheable prefix.
        cache_bust = uuid.uuid4().hex if setup == "without_cache" else None

        _output, usage = await run_agent(doc_rel, cache_bust=cache_bust)

        record = {
            "setup": setup,
            "document": doc_rel,
            "input_tokens": usage.input_tokens,
            "cache_read_tokens": usage.cache_read_tokens,
            "cache_write_tokens": usage.cache_write_tokens,
            "output_tokens": usage.output_tokens,
            "cost_usd": compute_cost(usage, prices),
        }
        records.append(record)
        print(f"[{setup}] {doc.name}: cache_read={usage.cache_read_tokens} cache_write={usage.cache_write_tokens} cost=${record['cost_usd']:.6f}")
    return records


async def main() -> None:
    docs = list_practice_docs()
    prices = json.loads(PRICES_PATH.read_text(encoding="utf-8"))[MODEL_NAME]

    all_records: list[dict] = []
    # "without_cache" first: proves cache-busting works on a cold cache, not just one that
    # happens to be empty anyway. Order doesn't affect correctness either way, since every
    # without_cache prompt is unique regardless of what ran before it.
    all_records += await run_setup("without_cache", docs, prices)
    all_records += await run_setup("with_cache", docs, prices)

    CACHE_TEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_TEST_PATH.write_text(json.dumps(all_records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWrote {len(all_records)} call records to {CACHE_TEST_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
