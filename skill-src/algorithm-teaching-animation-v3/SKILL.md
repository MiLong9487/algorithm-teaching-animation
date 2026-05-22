---
name: algorithm-teaching-animation-v3
description: Use when turning an algorithm name, sample input, and minimal animation requirements into a contract-governed teaching-animation request that requires explicit phase gates and non-skippable review control.
---

# Algorithm Teaching Animation v3

## Overview
This skill is a contract-first workflow for teaching-oriented algorithm animation work.
The top-level contract controls phase order, gate artifacts, delegation boundaries, and rollback routing.

## Workflow Enforcement
- phase order is mandatory
- do not silently skip phases
- do not preload future-phase executor references
- delegation does not transfer gate responsibility
- downstream phases may not repair upstream semantic gaps by convenience
- technical executability is never a substitute for review or QA passage

## Field Semantics
- `Execution ownership`: states whether the phase is orchestrator-only, delegate-eligible, or requires independent review.
- `Executor-required references`: only the phase executor must read these before doing the phase work.
- `Orchestrator escalation references`: the orchestrator reads these only when an artifact is suspicious, a gate fails, or rollback routing is unclear.
- `Do-not-start-until`: names the preconditions that block early phase entry.
- `Required outputs`: lists every artifact that must exist for the phase to count as complete.
- `Pass / exit gate`: states the exact condition that allows the workflow to advance.
- `Rollback target`: states the upstream phase that owns repair when the current gate fails.

## Artifact Chain
- `clarification_result.md`
- `pre_build_brief.md`
- `teaching_script.md`
- `script_review_result.md`
- `voiceover_status.md`
- `voiceover.md`
- `narration_manifest.json`
- `audio/voiceover/`
- `generated_algo_scene.py`
- `scene_review_result.md`
- `qa_result.md`

`voiceover_status.md` is required when the approved delivery tier is `silent preview`.
`voiceover.md`, `narration_manifest.json`, and usable assets under `audio/voiceover/` are required when the approved delivery tier includes narration.

## Global Rules
- `PRE_BUILD_BRIEF` cannot pass without explicit user approval
- `SCRIPT` produces `teaching_script.md`; `SCRIPT` cannot be treated as direct scene coding
- narration-required tiers may not skip `VOICEOVER`
- `scene_review_result.md` and `qa_result.md` are gate artifacts, not optional commentary
- `scene_review_result.md` and `qa_result.md` must exist as explicit file-backed results; implicit passes, waivers, or undocumented substitutes do not count
- overlays remain opt-in unless the user explicitly enables them
- if a downstream phase finds a semantic gap, route to the named rollback target instead of patching locally

## Phase 1: INTAKE
Normalize the request into a usable teaching target.
This phase prepares clarification; it does not freeze semantics.

- Purpose: capture algorithm identity, sample input or scenario, explicit user asks, and obvious delivery constraints in normalized working form.
- Execution ownership: `orchestrator-only`
- Executor-required references: `references/intake-contract.md`
- Orchestrator escalation references: none
- Do-not-start-until: a user request exists.
- Required outputs: normalized intake summary in working context; preserved explicit user constraints.
- Pass / exit gate: the algorithm target, concrete scenario, and known user asks are clear enough to enter high-impact clarification.
- Rollback target: `INTAKE`

## Phase 2: CLARIFICATION
Resolve high-impact forks before any semantic contract is written.
This phase asks all identified high-impact questions, not just the first convenient one.

- Purpose: identify semantic, teaching-focus, and delivery-affecting gaps, then freeze answers or explicitly approved defaults.
- Execution ownership: `orchestrator-only`
- Executor-required references: `references/high-impact-clarification.md`
- Orchestrator escalation references: `references/intake-contract.md`
- Do-not-start-until: `INTAKE` has produced a normalized request and candidate gaps can be named.
- Required outputs: `clarification_result.md`
- Pass / exit gate: `clarification_result.md` resolves every identified high-impact gap or records an explicit block that prevents advancement; delivery tier and overlay policy are frozen strongly enough to draft the brief.
- Rollback target: `INTAKE`

## Phase 3: PRE_BUILD_BRIEF
Freeze the shared semantic contract before script, voiceover, or scene work begins.
Silence, vague positivity, or implied agreement do not pass this phase.

- Purpose: turn intake, clarification, explicit user asks, and approved defaults into the single downstream semantic contract.
- Execution ownership: `delegate-eligible`
- Executor-required references: `clarification_result.md`; `references/pre-build-brief.md`
- Orchestrator escalation references: `references/high-impact-clarification.md`
- Do-not-start-until: `clarification_result.md` exists and unresolved high-impact gaps are not being hidden in the draft.
- Required outputs: `pre_build_brief.md`
- Pass / exit gate: `pre_build_brief.md` exists, includes the required contract sections, and receives explicit user approval.
- Rollback target: `PRE_BUILD_BRIEF` for drafting or approval issues; `CLARIFICATION` if the draft exposes unresolved high-impact ambiguity.

## Phase 4: SCRIPT
Convert the approved brief into a teachable beat structure.
`SCRIPT` cannot be treated as direct scene coding.

- Purpose: derive a reviewable `teaching_script.md` that makes viewer goals, beat order, and teaching focus explicit without inventing new semantics.
- Execution ownership: `delegate-eligible`
- Executor-required references: approved `pre_build_brief.md`; `references/teaching-script.md`
- Orchestrator escalation references: `references/pre-build-brief.md`
- Do-not-start-until: approved `pre_build_brief.md` exists.
- Required outputs: `teaching_script.md`; script review handoff context sufficient for an independent reviewer to evaluate the script against the approved brief.
- Pass / exit gate: `teaching_script.md` exists and `script_review_result.md = PASS`; `script_review_result.md` must be produced by an independent reviewer, not by the script writer.
- Rollback target: `SCRIPT` for structure, pacing, or clarity defects; `PRE_BUILD_BRIEF` if script work exposes missing or conflicting semantics.

## Phase 5: VOICEOVER
Voiceover is a contract phase, not an optional polish pass.
When narration is required, this phase cannot start from an unreviewed script.

- Purpose: produce narration artifacts that stay faithful to the approved brief and reviewed teaching script.
- Execution ownership: `delegate-eligible`
- Executor-required references: approved `pre_build_brief.md`; `teaching_script.md`; `script_review_result.md`; `references/voiceover.md`
- Orchestrator escalation references: `script_review_result.md`
- Do-not-start-until: the delivery tier has been frozen; `teaching_script.md` exists; `script_review_result.md = PASS`.
- Required outputs: `voiceover_status.md` when the approved delivery tier is `silent preview`; `voiceover.md`, `narration_manifest.json`, and usable audio assets under `audio/voiceover/` when the approved delivery tier is `voiceover preview` or `final narrated delivery`.
- Pass / exit gate: `silent preview` records `voiceover_status.md` as the explicit no-narration decision and leaves no hidden audio obligation; `voiceover preview` has `voiceover.md`, `narration_manifest.json`, and draft-quality intelligible audio assets ready for downstream render and QA; `final narrated delivery` has `voiceover.md`, `narration_manifest.json`, and viewer-usable audio assets ready for downstream render and QA.
- Rollback target: `VOICEOVER` for wording and pacing fixes; `SCRIPT` for beat-structure mismatch; `PRE_BUILD_BRIEF` for delivery-tier or semantic drift.

## Phase 6: RENDER
Render implements the approved contract; it does not author new semantics.
A runnable render is not a substitute for independent scene review.

- Purpose: turn the approved brief, reviewed script, and required narration plan into scene code and render evidence.
- Execution ownership: `delegate-eligible`
- Executor-required references: approved `pre_build_brief.md`; `teaching_script.md`; `voiceover_status.md` when the approved delivery tier is `silent preview`; `voiceover.md`, `narration_manifest.json`, and usable assets under `audio/voiceover/` when narration is required; `references/manim-guidelines.md`
- Orchestrator escalation references: `references/scene-review-checklist.md`; `script_review_result.md`
- Do-not-start-until: `teaching_script.md` exists and `script_review_result.md = PASS`; when the approved delivery tier is `silent preview`, `voiceover_status.md` exists; when narration is required, the required voiceover artifacts and usable audio assets exist.
- Required outputs: `generated_algo_scene.py`; render evidence; scene review handoff context sufficient for an independent reviewer to check contract fidelity and viewer clarity.
- Pass / exit gate: `generated_algo_scene.py` and render evidence exist, and `scene_review_result.md = PASS`; `scene_review_result.md` must be produced by an independent reviewer, not by the render executor, and a successful render run does not count as review passage.
- Rollback target: `RENDER` for styling, spacing, timing, layout, implementation-fidelity defects, or contract mismatch when the approved brief and script are clear and the scene simply violated them; `SCRIPT` for beat-structure mismatch or script-layer incompleteness that forced scene work to guess structure, sequencing, or emphasis; `PRE_BUILD_BRIEF` for unresolved semantic ambiguity, missing upstream decisions, or contract mismatch that proves the upstream contract is incomplete or internally conflicting.

## Phase 7: QA
QA verifies delivery safety against the contract, not just technical playback.
QA cannot be replaced by a smoke render.

- Purpose: independently verify that the produced output matches the approved brief, reviewed script, chosen delivery tier, overlay policy, and narration obligations.
- Execution ownership: `independent-review-required`
- Executor-required references: approved `pre_build_brief.md`; `teaching_script.md`; rendered media output; `scene_review_result.md`; `voiceover_status.md` when the approved delivery tier is `silent preview`; `voiceover.md`, `narration_manifest.json`, and usable audio assets under `audio/voiceover/` when narration is required; `references/render-qa-checklist.md`
- Orchestrator escalation references: `scene_review_result.md`; `references/scene-review-checklist.md`
- Do-not-start-until: `scene_review_result.md = PASS` exists as an explicit file-backed review result; implicit review passage or waivers are invalid. `QA` must be performed by an independent reviewer with no contribution to the output under review. If `scene_review_result.md` is missing or not `PASS`, `QA` is blocked from starting, `qa_result.md` must not be emitted, and when the scene-review artifact is missing entirely the default repair target is `RENDER` so the scene-review gate can be completed. When `scene_review_result.md` exists as `FAIL`, `QA` must honor that artifact's named repair target rather than inventing a fresh QA-side route.
- Required outputs: `qa_result.md`
- Pass / exit gate: `qa_result.md = PASS`; `QA` cannot start without `scene_review_result.md = PASS`.
- Rollback target: `RENDER` for visual, timing, layout, or implementation-fidelity issues; `VOICEOVER` for missing audio assets, wrong-language narration, narration-text drift, or audio-sync issues rooted in narration artifacts; `SCRIPT` for beat-structure mismatch; `PRE_BUILD_BRIEF` for semantic or delivery-contract drift.

## Phase 8: DELIVERY
Delivery claims must be backed by passed gate artifacts.
This phase reports only what the workflow has actually cleared.

- Purpose: deliver the correct tier of artifacts and summarize them without overstating what passed.
- Execution ownership: `orchestrator-only`
- Executor-required references: `qa_result.md`; `scene_review_result.md`; approved `pre_build_brief.md`
- Orchestrator escalation references: `references/render-qa-checklist.md`
- Do-not-start-until: `qa_result.md = PASS`.
- Required outputs: delivery summary tied to the actual produced artifacts and approved delivery tier.
- Pass / exit gate: delivered artifacts match the approved delivery tier and are supported by passed gate artifacts; `DELIVERY` cannot start without `qa_result.md = PASS`.
- Rollback target: `QA` for missing delivery evidence or tier-completeness issues; `PRE_BUILD_BRIEF` if delivery claims reveal contract drift.

## Failure Patterns
These are contract failures, not shortcuts:

- "The brief is detailed enough, so I can skip `SCRIPT`."
- "The render runs, so review is implicit."
- "QA can be replaced by a smoke render."
- "I should read every reference now just to be safe."
- "I delegated the phase, so I no longer own the gate."
- "This semantic gap is small enough to patch in `RENDER`."

## Supporting Files Policy
- `SKILL.md` is the hard contract.
- `references/*.md` hold phase-local detail.
- `agents/*.md` hold role-local behavior.
- support files must not silently override `SKILL.md`.
- not reading a support file is never permission to skip a contract requirement already stated in `SKILL.md`.
