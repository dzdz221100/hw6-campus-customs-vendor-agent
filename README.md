# Campus Customs — Vendor Desk Agent (HW6)

A PydanticAI agent that reads a vendor quote (HTML, PDF, or email) and recommends `recommend` /
`do_not_recommend` against the Campus Customs Shop Handbook's purchasing rules — defended against
prompt-injection attacks hidden in the documents it reads.

Full write-up: [`output/hw6_report.html`](output/hw6_report.html) (open directly in a browser — one
self-contained file, no server or internet needed). Problem-by-problem detail is in
[`output/`](output/) (`handbook_estimate.md`, `harness.md`, `cache_test.md`, `attack_results.md`,
`defense_results.md`, `red_team.md`) and the full prompt log is in [`AI_prompts.md`](AI_prompts.md).

## Setup

Requires Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and fill in your own PORTKEY_API_KEY
```

## Running the agent

```bash
# Defended (default) -- all three Problem 6 defenses on
python agent.py --doc data/practice_docs/p01_bluehen_quote.html

# No defenses -- reproduces the original Problem 3/5 agent
python agent.py --doc data/practice_docs/p03_ivyprint_catalog.html --no-defenses
```

Each run prints the structured decision and appends to `output/usage_log.json`,
`output/audit_trail.json`, and (only if a document ever talks the agent into it)
`output/trap_calls.json`.

### Batch test scripts

Each one reruns a whole document set and regenerates the matching `output/*.json`/`.md` files:

```bash
python run_cache_test.py     # Problem 4: with/without-cache cost comparison, all 12 practice docs
python run_attack_test.py    # Problem 5: unmodified agent vs. all 12 practice docs
python run_defense_test.py   # Problem 6: defended agent vs. all 12 practice docs
python run_exam_test.py      # Problem 8: defended agent vs. all 10 exam docs (no answer key)
```

The two red-team documents (`data/my_attacks/`) were run directly, not via a batch script — see
`output/red_team.md` for the exact commands and results.

## Repo layout

- `agent.py` — entry point; `build_agent`/`build_system_prompt`/`run_agent` all take a `defenses`
  flag.
- `tools.py` — `read_document` (with the Problem 6 sanitizer), and the `send_email`/`approve_payment`
  trap tools.
- `models.py` — the structured types (`VendorAssessment`, `AuditEntry`, `TrapCallRecord`,
  `UsageLogEntry`).
- `prompts/prompt.md` — the defended system prompt; `prompts/prompt_baseline.md` — the frozen
  Problem 3/5 prompt, used by `--no-defenses`.
- `data/` — the course-provided handbook, prices, and practice/exam documents, plus
  `data/my_attacks/` (the two Problem 7 red-team documents).
- `output/` — every deliverable from Problems 2–9, including the already-generated results from
  every run described above.
