# The Agent Zero Company (Ollama Cloud)

A ready-to-run multi-agent "engineering company" for Agent Zero, designed to
out-*deliver* a single frontier generalist by being specialized, parallel,
persistent and relentless on open-weight models.

The idea: you don't beat a frontier model with a smarter model. You beat it with
an **org** - specialists on the right model each, a hard verification gate, and a
persistent memory that compounds on your domain - running many-at-once.

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

## The economics (why this lineup)

Ollama Cloud Max has **no per-token pricing**. The binding constraints are:

1. **Concurrency: 10 simultaneous requests.** Extras queue in a fixed-depth queue
   and may be rejected. Slots, not tokens, are the currency.
2. **Wall-clock.** Verbose models (GLM-5.2 ~43k output tokens/task; DeepSeek-V4-Pro
   emitted 190M tokens to run one benchmark suite) cost minutes of latency, which
   is fatal on high-frequency paths and irrelevant on async ones.
3. **Session resets every 5 hours** (pace heavy bursts around them).

So the optimization target is **verified work per slot per hour**: intelligence x
speed on hot paths, peak intelligence on rare paths, and never a verbose model in
a loop that fires constantly. Cheap-per-token models (gpt-oss) are dominated once
cost is off the table - nemotron-3-super is both smarter and faster.

## The org (10-slot map)

| Slots | Profile              | Model                | Why (active params / measured intelligence / speed) |
|-------|----------------------|----------------------|------|
| 1     | `orchestrator` (a0)  | `minimax-m3:cloud`   | The ToT router. Best intelligence-per-active-param: 9.8B active, AA v4.1 = 44 (measured), ~1M ctx for whole-company state, multimodal. Dominates deepseek-v4-flash (13B active, unmeasured) on every measured axis |
| 1     | `architect` + `principal-engineer` (time-shared GLM seat) | `glm-5.2:cloud` | CEO seat + hardest-story coder. #1 open (AA 51), same ~1M ctx as M3 but +7 intelligence; #1 open on Code Arena (~1595 Elo). Verbose -> called, never looped |
| 4     | `engineer` swarm     | `kimi-k2.7-code`     | Most verified-stories-per-slot-hour: frontier coder, ~30% fewer thinking tokens, MCP-Mark 81.1% |
| 1     | `executor`           | `kimi-k2.7-code`     | Best tool-routing on the roster (MCP-Mark 81.1% > Opus 4.8's 76.4%) |
| 1     | `qa`                 | `nemotron-3-ultra`   | The gate: best non-hallucination (AA-Omniscience 78.7), 142 t/s, -30% tokens, family-disjoint from every producer |
| 1     | `researcher`         | `deepseek-v4-pro`    | Deepest knowledge, 1M ctx; ~94% answer-anyway rate -> QA verifies, sources pinned |
| 1     | `librarian`          | `nemotron-3-super`   | Fastest on roster (~296 t/s) and smarter than gpt-oss:120b (36 vs 33): speed is the new cheap |

Every profile's utility model is `nemotron-3-super` for the same reason.
`limit_requests` caps are queue backpressure (protecting the 10-slot ceiling),
not budget rationing.

> Model tags reflect the **July 2026** Ollama Cloud roster and are provisional.
> Confirm live tags with `ollama ls` / `ollama.com/search?c=cloud` and adjust the
> `name:` fields as the roster churns - retargeting a role is a one-line edit.

## Activate it

1. **Get an Ollama Cloud key** (Max plan for 10 concurrency) and add it to `.env`:
   ```
   OLLAMA_CLOUD_API_KEY=your_key_here
   ```
2. **Make the orchestrator your top agent** - in Settings set the agent profile to
   `orchestrator` (or run with `--agent_profile=orchestrator`).
3. Give it a goal. It ToT-routes the decomposition, delegates planning to
   `architect`, fans stories to the `engineer` swarm, routes actions to
   `executor`, gates every diff through `qa`, and has `librarian` bank what worked.

## Honest scorecard vs a frontier generalist

**Where this company wins:** tool-routing (Kimi-K2.7-Code beats Opus 4.8 on
MCP-Mark), near-frontier reasoning (GLM-5.2 ~ GPT-5.5 xhigh on GDPval-AA), 10-way
parallelism with a verification gate that converts retries into reliability
(pass@1 ~0.6 becomes ~0.94 by the third gated attempt), 24/7 scheduling, privacy
(zero-retention), flat cost, and a memory flywheel that compounds on your domain.

**Where the frontier generalist still wins:** the hardest single-shot task (best
open SWE-bench Pro trails Opus 4.8 by ~7-11 points, and newer frontier tiers sit
above that), reliability without scaffolding, and the raw ceiling (proprietary
Gemini-3-Flash AA 71 vs best open 51). The org's edge is structural - throughput,
verification, persistence - not per-task IQ. Pick decomposable, verifiable work
and the org out-delivers; hand it one gnarly novel bug and the generalist wins.

## Caveats

- No SOC 2 certification for Ollama Cloud (strong stated privacy posture, but
  note it for sensitive client code).
- `researcher` (DeepSeek-V4-Pro) must never be the final arbiter of facts.
- Most 2026 coding scores are vendor-run; the independent signals (Artificial
  Analysis, Arena) are what this lineup leans on. Roster and specifics are a
  July 2026 snapshot.
