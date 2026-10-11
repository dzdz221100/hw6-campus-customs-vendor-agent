# Handbook token and cost estimate

## How the token count was found

`data/shop_handbook.md` has no public tokenizer for `gpt-6-luna`, so the closest available
stand-in was used: OpenAI's `tiktoken` library, which ships the tokenizer used by the
current generation of OpenAI models.

```python
import tiktoken

with open("data/shop_handbook.md", "r", encoding="utf-8") as f:
    text = f.read()

enc = tiktoken.get_encoding("o200k_base")
tokens = enc.encode(text)
len(tokens)
```

- File size: 28,903 characters / 6,127 words.
- `o200k_base` encoding (current-generation OpenAI tokenizer, used as the primary estimate): **10,058 tokens**.
- `cl100k_base` encoding (older GPT-4 family tokenizer, used only as a sanity check): 10,184 tokens.

The two encodings land within ~1.3% of each other, so **10,058 tokens** is used as the
handbook's token count for the rest of this estimate. Because the real `gpt-6-luna`
tokenizer isn't public, this number is an approximation — Problem 4 compares it against
the token counts the real API reports.

## Price list used

From `data/prices.json` (`gpt-6-luna`, OpenAI Standard pricing, per 1M tokens):

| Price | $ / 1M tokens | $ / token |
|---|---|---|
| Input (no cache) | $0.10 | $0.0000001 |
| Cached input | $0.01 | $0.00000001 |
| Cache write | $0.125 | $0.000000125 |
| Output | $0.50 | $0.0000005 |

This estimate only prices the handbook text going **in** as part of the prompt — no
output tokens are counted, since the handbook itself doesn't generate a reply.

## Cost without caching

Every call pays the full input price for the handbook, 10,058 tokens:

- **1 call:** 10,058 × $0.0000001 = **$0.0010058** (~$0.001)
- **1,000 calls:** 1,000 × $0.0010058 = **$1.0058** (~$1.01)

## Cost with caching

OpenAI's prompt caching bills the *first* time a prefix is sent at the **cache write**
rate, and every later call that hits the same cached prefix at the much cheaper
**cached input** rate. The handbook is a fixed block of text sent identically on every
call, so it's exactly the kind of prefix caching is built for:

- **Cache write** (first call only): 10,058 × $0.000000125 = **$0.00125725**
- **Cached hit** (every call after the first, same session/cache window): 10,058 × $0.00000001 = **$0.00010058**

So:

- **1 call** (necessarily a cache write, nothing to hit yet): **$0.00125725** (~$0.0013)
- **1,000 calls** (1 write + 999 cached hits):
  - Write: $0.00125725
  - 999 hits: 999 × $0.00010058 = $0.10047942
  - Total: $0.00125725 + $0.10047942 = **$0.10173667** (~$0.102)

## Summary table

| Scenario | 1 call | 1,000 calls |
|---|---|---|
| No caching | $0.0010058 | $1.0058 |
| With caching | $0.0012573 (write) | $0.1017 (1 write + 999 hits) |

Caching turns 1,000 calls of sending this handbook from about **$1.01** into about
**$0.10** — roughly a 10x saving, because 999 of the 1,000 calls only pay the
$0.01/1M cached-input rate instead of the $0.10/1M full input rate.

## Caveat

These numbers price the handbook alone, assuming it is the *only* thing in the prompt and that caching holds across all 1,000 calls (no cache expiry, no other text ahead of the handbook invalidating the cached prefix). Real calls in Problem 4 will also include the vendor document, the system prompt, and the model's output tokens, so the measured per-call cost there will be higher than the numbers here — this file isolates just the handbook's contribution.
