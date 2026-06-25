# Batch 3 Implementation Audit — RevenuePilot OS

Audit of the existing `SoloFounder/` code against the Batch 3 spec. Verdict: **the spec is faithfully implemented and all tests pass.** The findings below are the gaps and risks that matter, and the remediation applied in this pass.

## 1. Fidelity summary

| Spec area | Status | Notes |
|---|---|---|
| 13 skills (12 core + content_to_product) | ✅ Complete | Thin wrappers over a shared `executor.run_skill`. |
| Standard `SkillEnvelope` | ✅ Complete | Matches spec fields incl. `confidence_score` (0–100). |
| Per-skill Pydantic result schemas | ✅ Complete | 491 lines; scores bounded `ge/le`, enums for risk/priority/fit. |
| JSON validation + 1 repair retry | ✅ Complete | `executor.run_skill` retries once with a repair prompt, else fails. |
| Skill registry + `get_skill` | ✅ Complete | |
| `SkillRunner` lifecycle | ✅ Complete | Creates run → validates → writes `ai_generations` → maps entities. |
| `entities_to_create` mapping | ✅ Complete | Founder diagnosis → `business_ideas`; others mapped per spec. |
| 3 LangGraph workflows | ✅ Complete | idea_to_offer, deal_to_delivery, content_to_product. |
| `RevenuePilotState` | ✅ Complete | Superset of spec fields + run-tracking. |
| API routes | ✅ Complete | `/api/skills/run`, 3 workflow runners, `GET /workflow-runs[/{id}]`. |
| `workflow_runs` table + RLS | ✅ Complete | `sql/workflow_runs.sql`. |
| Guardrails (spam / regulated advice / faith) | ⚠️ Partial | See §2.1 — only enforced inside the deterministic provider. |
| Tests | ✅ 9 passing | Skill lifecycle, isolation, both guardrails, 3 workflows. |

## 2. Findings that needed fixing

### 2.1 Guardrails were not provider-independent (high)
Spam/deception detection lived **inside `DeterministicRevenuePilotProvider`**, not in the executor. Swapping in a real LLM would silently drop the outreach abuse guardrail — the only protection left would be the prompt. **Fix:** moved abuse detection + safe-alternative into `app/skills/guardrails.py`, enforced in `executor.run_skill` *before* the model is called. Now holds for any provider and short-circuits without spending a model call.

### 2.2 Workflow nodes crash on a sub-skill failure (high, latent)
Every node did `state[x] = result["output"]["result"]`. On a failed `skill_runner.run` the result has no `output` key, so a live-LLM failure mid-workflow raised `KeyError` instead of failing gracefully. With the deterministic stub this never triggers. **Fix:** `record_step()` records the run then raises `WorkflowStepError` on failure, which `WorkflowRunner` catches and marks the workflow `failed`.

### 2.3 No real LLM provider (expected gap)
Only the deterministic stub existed. **Fix:** added `AnthropicProvider` (JSON prefill + fence-stripping extraction) selected by env (`REVENUEPILOT_AI_PROVIDER=anthropic`), deterministic remaining the default so tests/dev need no key.

### 2.4 Prompts heavily condensed (medium)
`prompts/definitions.py` had 2–4 line summaries; the spec's prompts carry the decision rules and anti-patterns that actually steer output (force specificity, ban broad niches like "SMBs/creators", bad-question lists for discovery, paid-pilot preference, faith-tone rules). With the stub this is invisible; with a real model it's most of the quality. **Fix:** expanded all 13 to full spec-grade prompts.

### 2.5 Repos are in-memory only (expected gap)
No persistence beyond process memory. **Fix:** added async Postgres repos (lazy `asyncpg`) behind a factory selectable by env (`REVENUEPILOT_DB=postgres`), parity interface with in-memory; default stays in-memory. Added `sql/skill_runs.sql`, `sql/ai_generations.sql`, `sql/_functions.sql`.

### 2.6 Conditional routing defined but unused (medium)
`routing.py` had skip-if-exists predicates but no graph used `add_conditional_edges`, and the compat shim didn't support them. **Fix:** compat shim now supports conditional edges; `idea_to_offer` skips persona/pain when a persona is pre-seeded and ends early if an upstream artifact is missing.

## 3. Minor / accepted (not changed)

- `confidence_score` is assigned by the envelope builder (80/60) rather than returned by the model — acceptable; can be model-supplied later.
- `entities_to_update` is always empty — spec allows it; no update flows yet.
- `requires-python` was `>=3.12` but the code runs on 3.10 (lazy annotations). Relaxed to `>=3.10`.
- SQL assumes Batch-2 objects (`auth.users`, `business_projects`, `set_updated_at`); `_functions.sql` now ships the trigger fn so the Batch-3 tables are self-contained.

## 4. Verification

`pytest -q` — green before and after. New tests cover: provider-independent outreach guardrail (asserts the model is never called on abusive input), JSON-object extraction, conditional skip routing (persona pre-seeded ⇒ fewer skill runs), and repo-factory default selection.
