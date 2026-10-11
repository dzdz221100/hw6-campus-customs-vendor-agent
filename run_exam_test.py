"""Problem 8: run the final defended agent on all 10 data/exam_docs/*, with no answer key and no
hand-editing of the results -- whatever the agent reports is saved exactly as reported.

Usage:
    python run_exam_test.py
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from agent import MODEL_NAME, PRICES_PATH, ROOT, compute_cost, run_agent

EXAM_DOCS_DIR = ROOT / "data" / "exam_docs"
TRAP_CALLS_PATH = ROOT / "output" / "trap_calls.json"
EXAM_RESULTS_PATH = ROOT / "output" / "exam_results.json"


def load_trap_calls() -> list[dict]:
    return json.loads(TRAP_CALLS_PATH.read_text(encoding="utf-8")) if TRAP_CALLS_PATH.exists() else []


async def main() -> None:
    prices = json.loads(PRICES_PATH.read_text(encoding="utf-8"))[MODEL_NAME]
    docs = sorted(EXAM_DOCS_DIR.iterdir(), key=lambda p: p.name)

    results = []
    for doc in docs:
        doc_rel = str(doc.relative_to(ROOT))

        trap_calls_before = load_trap_calls()
        output, usage = await run_agent(doc_rel, defenses=True)
        trap_calls_after = load_trap_calls()
        trap_tool_called = len(trap_calls_after) > len(trap_calls_before)

        record = {
            "file": doc.name,
            "vendor": output.vendor,
            "sku": output.sku,
            "unit_price": output.unit_price,
            "lead_time_days": output.lead_time_days,
            "min_order": output.minimum_order,
            "decision": output.decision,
            "reason": output.reason,
            "trap_tool_called": trap_tool_called,
            "input_tokens": usage.input_tokens,
            "cached_tokens": usage.cache_read_tokens,
            "output_tokens": usage.output_tokens,
            "cost_usd": compute_cost(usage, prices),
        }
        results.append(record)
        print(f"{doc.name}: vendor={output.vendor!r} sku={output.sku} decision={output.decision} "
              f"trap_tool_called={trap_tool_called} cost=${record['cost_usd']:.6f}")

    EXAM_RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWrote {len(results)} records to {EXAM_RESULTS_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
