# The Agent Zero Company (Ollama Cloud)

A ready-to-run multi-agent "engineering company" for Agent Zero, designed to
out-*deliver* a single frontier generalist by being specialized, parallel,
persistent and relentless on cheap open-weight models.

The idea: you don't beat a frontier model with a smarter model. You beat it with
an **org** - specialists on the right model each, a hard verification gate, and a
persistent memory that compounds on your domain - running many-at-once at low
marginal cost.

## What this adds to Agent Zero

Vanilla Agent Zero gives every agent the single model from global settings;
`call_subordinate` only swaps the prompt profile, never the model. This setup adds
**per-profile model routing** so each role runs on its own Ollama Cloud model:

- `python/helpers/agent_profile.py` - loads an optional `agents/<profile>/_config.yaml`
  and overrides the chat/utility model for that profile. No file = unchanged
  behavior, so every stock profile still works exactly as before.
- `python/tools/call_subordinate.py` - applies the profile's model when a subordinate
  is spawned.
- `initialize.py` - applies it to the top-level agent too.
- `conf/model_providers.yaml` - adds an `ollama_cloud` provider (LiteLLM
  `ollama_chat`, `api_base https://ollama.com`).

## The org (maps to the 10-slot concurrency ceiling)

Ollama Cloud Max allows **10 concurrent models** - that, not token quota, is the
real cap on how big the company can run at once. Billing is by GPU-time usage
level (1-4), with a 5-hour session reset and a 7-day weekly reset, so heavy models
must be rationed and cheap models carry the volume (and free concurrency slots).

| Profile              | Ollama Cloud model      | Level | Role |
|----------------------|-------------------------|-------|------|
| `orchestrator` (a0)  | `gpt-oss:120b-cloud`    | 2     | Router / PM you talk to; runs the hot loop cheap |
| `architect`          | `glm-5.2:cloud`         | 4     | Strategy & system design (#1 open-weight, AA v4.1 = 51). Rationed |
| `engineer`           | `gpt-oss:120b-cloud`    | 2     | The parallel dev swarm - one story each |
| `principal-engineer` | `qwen3-coder:480b-cloud`| 3     | Heavy / whole-codebase coding (alt: `minimax-m3:cloud`, ~1M ctx) |
| `executor`           | `kimi-k2.7-code`        | 3     | Tool-runner: MCP/A2A/shell/browser (best tool-routing) |
| `qa`                 | `nemotron-3-ultra`      | 3-4   | Adversarial gate; different family, best non-hallucination |
| `researcher`         | `deepseek-v4-pro`       | 4     | Deep knowledge / long-context (verify - ~94% hallucination) |
| `librarian`          | `gpt-oss:20b-cloud`     | 1     | Memory & knowledge-base curation; cheap always-on glue |

The `limit_requests` in each `_config.yaml` is a per-minute rate cap that encodes
budget discipline (level-4 models get the tightest caps). Tune to your plan.

> Model tags reflect the **July 2026** Ollama Cloud roster and are provisional -
> many 2026 coding scores are vendor-run. Confirm live tags with `ollama ls` /
> `ollama.com/search?c=cloud` and adjust the `name:` fields as the roster churns.

## Activate it

1. **Get an Ollama Cloud key** (Max plan for 10 concurrency) and add it to `.env`:
   ```
   OLLAMA_CLOUD_API_KEY=your_key_here
   ```
2. **Make the orchestrator your top agent** - in Settings set the agent profile to
   `orchestrator` (or run with `--agent_profile=orchestrator`).
3. Give it a goal. It will delegate to `architect`, fan stories to `engineer`s,
   route actions to `executor`, gate every diff through `qa`, and have `librarian`
   bank what worked.

To retarget a role at a different model, edit that profile's `_config.yaml` - no
code changes needed.

## Honest scorecard vs a frontier generalist

**Where this company wins:** tool-routing/agentic execution (Kimi-K2.7-Code beats
Opus 4.8 on MCP-Mark, 81.1% vs 76.4%), reasoning is now close (GLM-5.2 ~ GPT-5.5
xhigh on GDPval-AA), 10-way parallelism, 24/7 scheduling, privacy (zero-retention),
flat cost, and a memory flywheel that compounds on your codebase.

**Where the generalist still wins:** hardest single-shot SWE (MiniMax-M3's SWE-bench
Pro 58.6% trails Opus 4.8's 69.2%), reliability without heavy scaffolding (open
models need the QA gate to be trustworthy - see DeepSeek's hallucination rate), and
the raw frontier ceiling (proprietary Gemini-3-Flash AA index 71 vs best open 51).

So: pick decomposable, verifiable, repeatable work; wrap streaky cheap models in a
hard gate; run them in parallel; and let memory compound. That's a company that
out-delivers a single generalist on that slice - even though the generalist would
out-reason any one of its agents.

## Caveats

- No SOC 2 certification for Ollama Cloud (strong stated privacy posture, but note
  it for sensitive client code).
- `researcher` (DeepSeek-V4-Pro) must never be the final arbiter of facts - QA and
  source-pinning are mandatory.
- Roster and usage-level bands shift month to month; treat this as a July 2026
  snapshot.
