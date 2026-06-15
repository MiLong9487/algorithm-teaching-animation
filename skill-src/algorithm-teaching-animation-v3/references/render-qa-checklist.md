# Render QA Checklist

This document defines the final QA pass for `algorithm-teaching-animation-v3`.

Scene review asks whether the scene implementation faithfully expresses the contract. Render QA asks whether the rendered output is actually safe to deliver for the chosen tier.

## Required Output

Return `qa_result.md` with:

- `PASS` or `FAIL`
- independent reviewer authorship of the review result
- reviewer ownership of the `QA` gate
- delivery tier under review
- findings with evidence
- repair direction

If `scene_review_result.md` is missing or not `PASS`, `QA` is blocked from starting. In that case, do not emit `qa_result.md`; return an upstream gate-block notice that names the blocking scene-review condition and its repair target. When `scene_review_result.md` is missing entirely, use `RENDER` as the default repair target so the scene-review gate can be completed.

`QA` is an independent review gate. `qa_result.md` must be authored by an independent reviewer rather than any contributing author to the output under review.

Do not start `QA` unless `scene_review_result.md = PASS` exists as the explicit file-backed scene-review result. A failing or missing `scene_review_result.md` blocks `QA` entry and must be honored as an upstream review gate, not converted into an ordinary `QA`-only judgment or a synthetic `qa_result.md`.

## QA Inputs

Review against:

- approved `pre_build_brief.md`
- approved `teaching_script.md`
- `scene_review_result.md`
- rendered media output
- `voiceover_status.md` when the tier is `silent preview`
- approved `voiceover.md`, `narration_manifest.json`, and usable audio assets when the tier includes narration
- overlay output when overlays are enabled

## Delivery-Tier Checks

### Silent Preview

Verify:

- `voiceover_status.md` explicitly records that narration is not owed
- the render is visually understandable without narration
- no audio-dependent teaching step is left unexplained
- overlays are absent unless explicitly enabled

### Voiceover Preview

Verify:

- voiceover artifacts and draft-quality intelligible audio assets exist
- narration language matches the approved brief
- timing is close enough to assess the teaching flow
- the preview may be rough, but not semantically misleading

### Final Narrated Delivery

Verify:

- all required audio assets are present
- narration language matches the approved brief
- visual focus and voiceover remain aligned beat by beat
- the result is clean enough to deliver, not just debug

## Core Checklist

### Visual Readability

- primary structures remain legible throughout
- active focus is obvious in each beat
- settled or excluded regions remain distinguishable
- labels are readable and non-colliding
- nothing important is cropped or hidden

### Contract Fidelity

- the render matches the confirmed semantics
- support structures appear when required
- no new semantics were added during implementation
- overlay behavior matches the brief

### Timing and Audio

- beat pacing gives the viewer time to register the change
- voiceover starts after the visual hook is established
- long holds are justified by teaching value, not by dead air
- narration and visuals do not contradict each other

### Delivery Completeness

- the correct tier was actually produced
- required files for that tier exist and are usable
- preview outputs are not mislabeled as final

## Repair Direction

Use these paths:

- `stay within RENDER` for layout, spacing, timing, styling, or fidelity repairs that keep the same frozen semantics
- `return to VOICEOVER` when QA discovers missing audio assets, wrong-language narration, narration-text drift, or audio-sync defects rooted in the narration artifacts
- `return to SCRIPT` when QA discovers a beat-structure mismatch that render changes alone cannot fix
- `return to PRE_BUILD_BRIEF` when QA discovers semantic ambiguity, a missing upstream decision, or delivery-contract drift the brief failed to freeze

QA may not silently rewrite the contract.
QA may not override a failing scene review by issuing an independent pass or by rerouting the same blocked work as a normal `QA` defect.

## PASS Standard

Only pass when all of these are true:

- `scene_review_result.md = PASS` exists as the explicit file-backed scene-review result
- the chosen delivery tier is satisfied
- the render is readable
- the contract is implemented faithfully
- no unresolved semantic ambiguity remains visible to the viewer
- `qa_result.md` is written by an independent reviewer rather than any contributing author to the output under review

## Common Failures

- Passing a scene that is semantically correct but visually unreadable.
- Treating missing audio in a narrated tier as a minor note.
- Fixing a contract gap by improvising new semantics inside QA notes.
- Calling a debug-quality preview "final" because the algorithm logic is correct.
