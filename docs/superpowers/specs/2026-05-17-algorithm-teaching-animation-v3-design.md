# Algorithm Teaching Animation v3 Design

Date: 2026-05-17
Status: Draft for user review
Scope: New skill at `skill-src/algorithm-teaching-animation-v3/`

## 1. Goal

`algorithm-teaching-animation-v3` is a new skill that lowers the required initial input for algorithm teaching animation work while preserving strict phase gates, reviewer ownership, and subagent-driven quality control.

`v3` is designed for cases where the user starts with:

- algorithm name
- sample input or target scenario
- a small number of special animation requests

The workflow must then:

1. identify high-impact semantic gaps
2. ask all identified high-impact clarification questions before scene generation
3. produce a single user-confirmable `pre_build_brief.md`
4. block scene generation until that brief is confirmed

`v3` does not replace or mutate `v2`. `skill-src/algorithm-teaching-animation-v2/` remains intact.

## 2. Non-Goals

- `v3` does not preserve the `TRACE` phase.
- `v3` does not require `generated_trace_script.py` or `action_trace.json`.
- `v3` does not expand into a code-first parsing product.
- `v3` does not promise equal stability across all algorithm categories in its first release.
- `v3` does not auto-enable optional overlays.

## 3. Product Positioning

`v3` is a `balanced-brief-first` workflow.

It is not:

- a simplified freeform generator
- a trace-less clone of `v2`
- a scene-first workflow that lets implementation absorb unresolved semantics

It is:

- minimal-input at intake
- clarification-heavy only for high-impact issues
- brief-gated before script and scene work
- strict about rollback when unresolved semantics appear late

## 4. Fixed Phases

`v3` has eight fixed phases:

1. `INTAKE`
2. `CLARIFICATION`
3. `PRE_BUILD_BRIEF`
4. `SCRIPT`
5. `VOICEOVER`
6. `RENDER`
7. `QA`
8. `DELIVERY`

## 5. Workflow Overview

### 5.1 INTAKE

The workflow starts from algorithm specification rather than code specification.

Minimum expected input:

- `algorithm name`
- `sample input` or `target scenario`
- `special animation preference` if any

Code or pseudocode is optional support material, not required startup input.

### 5.2 CLARIFICATION

`CLARIFICATION` exists to resolve all identified high-impact gaps before the brief is frozen.

Governance decisions:

- `first-class support` categories use a `hybrid` semantic inventory
- the agent uses a compact checklist plus case-specific heuristics
- the clarification strategy is `ask-all-identified-high-impact`

This phase must not ask for low-value details such as default pointer colors, normal label micro-placement, or ordinary pacing preferences.

### 5.3 PRE_BUILD_BRIEF

`PRE_BUILD_BRIEF` is the core gate in `v3`.

The workflow must generate a single `pre_build_brief.md` that serves as the shared semantic contract for:

- `SCRIPT`
- `VOICEOVER`
- `RENDER`
- `QA`

Scene generation must not begin before the brief is confirmed.

Confirmation rule:

- `explicit approval` passes the gate
- `targeted edit + proceed` also passes the gate
- silence or implicit drift does not pass the gate

### 5.4 SCRIPT

`SCRIPT` produces `teaching_script.md`.

This artifact is not a trace substitute. It is the teaching-structure layer between the confirmed brief and the final Manim implementation.

Its purpose is to define:

- what each beat is trying to teach
- what visual focus each beat should emphasize
- how the explanation sequence maps onto the algorithm flow

The script can align with loop-oriented Manim code without being identical to raw control flow.

### 5.5 VOICEOVER

The default voiceover language remains English.

This phase produces voiceover artifacts based on the approved script and selected delivery tier. Optional overlays remain opt-in.

### 5.6 RENDER

`generated_algo_scene.py` is generated directly from:

- confirmed `pre_build_brief.md`
- approved `teaching_script.md`
- user follow-up requirements
- algorithm code or pseudocode when needed

This phase does not depend on a trace artifact.

### 5.7 QA

Scene review and render QA remain strict, but external naming is simplified.

Recommended public-facing result names:

- `Clarification Result`
- `Pre-build Brief`
- `Scene Review Result`
- `QA Result`
- `Delivery Status`

Internal rigor remains unchanged:

- phase gate
- `PASS/FAIL`
- evidence paths
- reviewer ownership
- no skipping after failure

### 5.8 DELIVERY

`v3` retains three delivery tiers:

- `silent preview`
- `voiceover preview`
- `final narrated delivery`

## 6. High-Impact Clarification Contract

High-impact gaps are questions that would change any of:

- animation semantics
- teaching focus
- delivery content

Three major classes:

### 6.1 Semantic forks

Multiple reasonable animation semantics exist, and different choices change what the viewer learns.

Examples:

- `insertion sort`: `shift` as `hole`, `temp slot`, or repeated movement
- `BFS`: `visited` on discovery vs on processing
- `binary search`: search interval convention or first-valid vs existence search

### 6.2 Teaching-focus forks

Different teaching emphasis would change beat structure or visual focus.

Examples:

- `binary search`: emphasize interval shrinkage vs branch control flow
- `BFS`: emphasize queue semantics vs layer expansion

### 6.3 Delivery-affecting forks

The answer changes layout obligations or deliverable shape.

Examples:

- whether optional overlays are enabled
- whether the deliverable target is silent, voiceover, or final narrated
- whether traversal support structures must be visibly present

Low-impact items must not trigger clarification by default.

## 7. Pre-build Brief Contract

`pre_build_brief.md` is the single formal pre-scene planning artifact in `v3`.

It must be understandable by both:

- the user
- downstream subagents

Required sections:

- `Algorithm Identity`
- `Teaching Goal`
- `Audience`
- `Sample Input / Scenario`
- `Confirmed User Requests`
- `Resolved High-Impact Clarifications`
- `Agent Default Decisions`
- `Chosen Visual Semantics`
- `Pointer / Boundary / Temp Slot Plan`
- `Beat Outline`
- `Overlay Policy`
- `Delivery Tier`
- `Known Risks / Best-Effort Notes`

Gate rules:

- any identified high-impact issue missing from the brief is a `FAIL`
- vague wording that hides a high-impact fork is a `FAIL`
- unconfirmed briefs cannot advance to `SCRIPT`

## 8. Governance Philosophy

### 8.1 Chosen model

`v3` uses `brief-is-strong-default`.

That means:

- the confirmed brief is the primary semantic authority
- downstream phases may fix `visual styling`
- downstream phases may not invent new semantic decisions

### 8.2 Allowed render-layer fixes

`RENDER`-stage fixes are limited to `visual styling` and layout execution details such as:

- arrow appearance
- color styling
- label micro-placement
- spacing and safe-margin tuning

### 8.3 Disallowed render-layer fixes

The render layer may not decide or revise:

- `swap` vs `shift` semantics
- `hole` vs `temp slot`
- pointer meaning
- visited/discovered semantics
- search variant semantics
- any new delivery-affecting decision

## 9. Subagent Orchestration

`v3` retains hard subagent orchestration as a quality gate.

Principle:

- if work can be split into an independent responsibility, it should be delegated
- the workflow must not silently collapse into an all-in-one main-agent execution model

### 9.1 Retained and rewritten roles

- `mode-planner`
- `layout-checker`
- `script-writer`
- `script-reviewer`
- `voiceover-manifest`
- `scene-writer`
- `scene-reviewer`
- `qa-verifier`

### 9.2 Removed roles

- `trace-contract`
- `trace-writer`

### 9.3 New roles

- `clarification-planner`
- `brief-editor`

## 10. Subagent Responsibilities

### 10.1 mode-planner

Purpose:

- classify the teaching mode
- provide high-level framing for downstream clarification

Expected outputs:

- `primary mode`
- optional `secondary mode`
- rationale
- suggested semantic focus areas

### 10.2 layout-checker

Purpose:

- test whether the current brief can fit the intended visual layout

Expected outputs:

- layout feasibility verdict
- collision risks
- layout overload warnings

It may fail a brief for feasibility reasons, but it may not rewrite semantics.

### 10.3 script-writer

Purpose:

- write `teaching_script.md` from the confirmed brief
- turn semantic decisions into a teachable beat structure

This role does not replace the algorithm loop. It defines how the loop should be taught.

### 10.4 script-reviewer

Purpose:

- verify that the script faithfully reflects the brief
- catch drift before voiceover or scene implementation

Typical failures:

- hidden semantic substitutions
- missing teaching focus
- script beats that contradict confirmed semantics

### 10.5 voiceover-manifest

Purpose:

- convert approved script structure into voiceover artifacts and timing expectations

### 10.6 scene-writer

Purpose:

- implement the confirmed teaching design in `generated_algo_scene.py`

It may choose technical implementation structure, including loop-oriented Manim code, but it may not redefine semantics.

### 10.7 scene-reviewer

Purpose:

- act as the sole `RENDER` gate reviewer

It reviews:

- implementation fidelity
- visual clarity
- layout safety
- styling consistency

It does not own semantic invention.

### 10.8 qa-verifier

Purpose:

- validate rendered outputs against the confirmed brief, approved script, and target delivery tier

## 11. Rollback Rules

### 11.1 Level 1: stay within RENDER

Use when the problem is limited to:

- visual styling
- spacing
- layout execution
- implementation fidelity without semantic ambiguity

Action:

- `scene-reviewer` returns `FAIL`
- a new repair `scene-writer` instance is opened
- repair stays within the current confirmed semantics

### 11.2 Level 2: return to PRE_BUILD_BRIEF

Use when the issue is:

- semantic ambiguity
- semantic mismatch
- a newly surfaced high-impact fork

Action:

- `scene-reviewer` marks the issue as semantic
- main agent stops render-only repair
- workflow returns to `PRE_BUILD_BRIEF`
- if needed, re-enter `CLARIFICATION`
- update the brief and get confirmation again before resuming

Decision rule:

- `styling wrong` -> remain in `RENDER`
- `semantics unclear` -> rollback to `PRE_BUILD_BRIEF`

## 12. First-Class Support Strategy

Initial `first-class support`:

- array sorting
- binary search / two-pointer style searching
- basic graph traversal such as `BFS` / `DFS`

These categories should receive:

- stronger default visual semantics
- compact high-impact clarification checklists
- better reviewer checklist coverage
- more stable QA expectations

### 12.1 Array sorting

Initial stable targets may include:

- `insertion sort`
- `selection sort`
- `bubble sort`

Key support areas:

- comparison emphasis
- swap/shift semantics
- boundary signaling
- active-element focus

### 12.2 Binary search / two-pointer

Key support areas:

- pointer meaning
- interval semantics
- stopping condition semantics
- convergence or crossing behavior

### 12.3 BFS / DFS

Key support areas:

- queue or stack visibility
- visited semantics
- discovery vs processing
- frontier emphasis
- neighbor-order expectations

## 13. Best-Effort Support

Initial `best-effort` categories:

- dynamic programming table construction
- tree transformations
- greedy / interval algorithms
- specialized graph algorithms

When a request falls into this scope, the brief must explicitly document:

- assumptions
- risks
- incomplete default coverage
- possible rollback pressure points

## 14. Reference Set

### 14.1 New references

- `references/intake-contract.md`
- `references/high-impact-clarification.md`
- `references/pre-build-brief.md`
- `references/default-visual-semantics.md`

### 14.2 Retained and rewritten references

- `references/planning.md`
- `references/teaching-script.md`
- `references/voiceover.md`
- `references/manim-guidelines.md`
- `references/scene-review-checklist.md`
- `references/render-qa-checklist.md`
- `references/visual-language.md`

### 14.3 References not carried into the v3 main flow

- `references/trace-schema.md`
- `references/tracer-api.md`

These remain part of `v2`, not `v3`.

## 15. Metadata Expectations

`agents/openai.yaml` and `SKILL.md` frontmatter must clearly state that:

- `v3` is for minimal-input algorithm animation requests
- the workflow asks high-impact clarification questions before scene generation
- `pre_build_brief.md` must be confirmed before script and scene generation
- the default output remains main animation plus English voiceover
- optional overlays remain opt-in

## 16. Validation Plan

### 16.1 Structural validation

- run `quick_validate.py` against `skill-src/algorithm-teaching-animation-v3/`
- verify required files exist
- verify `v2` remains unchanged

### 16.2 Workflow validation

Forward-test at least:

1. `insertion sort`
   Special request example: key rises above the array before insertion search.
   Verify high-impact clarification is targeted and the resulting brief is adequate.

2. `binary search`
   Minimal-input case with little extra detail.
   Verify the agent fills low-risk defaults but still asks all identified high-impact questions.

3. `BFS`
   Verify queue, visited, and traversal semantics can be frozen by brief without trace artifacts.

## 17. Acceptance Criteria

- The workflow starts successfully from minimal input.
- All identified high-impact gaps are handled before the brief is frozen.
- `pre_build_brief.md` is sufficient for user confirmation before scene generation.
- Unconfirmed briefs do not advance to `SCRIPT`.
- Render-stage fixes stay limited to `visual styling` and layout execution.
- Semantic ambiguity discovered in scene review triggers rollback.
- `first-class support` cases can reliably produce brief, script, scene, and QA artifacts.
- Optional overlays never auto-enable without opt-in.
- `v2` remains usable and unmodified by `v3` work.

## 18. Open Implementation Notes

- `v3` should simplify external phase naming without weakening internal gate rigor.
- `teaching_script.md` remains a formal script artifact, not a reduced beat-sheet surrogate.
- The absence of trace artifacts increases the importance of well-defined brief and script contracts.
