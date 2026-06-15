# Scene Review Checklist

This document defines the `RENDER` gate review for `algorithm-teaching-animation-v3`.

The reviewer checks scene fidelity and viewer clarity. The reviewer does not invent or repair semantics.

## Required Output

Return `scene_review_result.md` with:

- `PASS` or `FAIL`
- independent reviewer authorship of the review result
- reviewer ownership of the `RENDER` gate
- categorized findings
- evidence references
- repair direction

Use these finding categories:

- `styling`
- `layout`
- `semantic ambiguity`
- `contract mismatch`

## Review Inputs

Review against:

- approved `pre_build_brief.md`
- approved `teaching_script.md`
- `generated_algo_scene.py`
- rendered preview or render evidence
- layout audit output when available

## Review Questions

### Contract Fidelity

- Does the scene implement the frozen semantics rather than a new interpretation?
- Does each major beat match the teaching purpose in the approved script?
- Are support structures present when the brief says they matter?

### Visual Clarity

- Is the current focus obvious?
- Are pointers, boundaries, and temporary structures readable?
- Do resolved regions remain understandable without stealing focus?

### Layout Safety

- Are labels and structures free of collisions?
- Is important content kept inside safe margins?
- If overlays are enabled, do they avoid the teaching-critical area?
- If layout audit warnings exist, do they correspond to real visible problems in the rendered evidence, or are they intentional containment/noisy bounding boxes?

### Semantic Safety

- Does any styling choice force the viewer to infer a rule the brief never froze?
- Does any implementation convenience change what the viewer learns?
- Does any mismatch reveal unresolved semantic ambiguity, a semantic mismatch, or a missing upstream decision?

## Repair Routing

### Stay Within RENDER

Use this when the problem is limited to:

- styling
- spacing
- layout execution
- implementation fidelity without semantic ambiguity

The repaired scene must keep the same confirmed semantics.

### Return to SCRIPT

Use this when:

- the scene exposes a beat-structure mismatch against the approved script
- the approved brief is clear, but the script did not give scene work enough faithful beat guidance
- the approved brief is clear, but script-layer incompleteness forced the scene to guess structure, sequencing, or emphasis

Do not patch beat logic locally inside `RENDER` just because the implementation is already in motion.

### Return to PRE_BUILD_BRIEF

Use this when the issue is:

- semantic ambiguity
- missing upstream decision
- conflicting upstream guidance
- any newly surfaced high-impact fork

If the needed decision was never frozen, or the brief no longer resolves the surfaced semantic fork, return through clarification before resuming scene work.

## Contract Mismatch Rule

Use `contract mismatch` when the scene conflicts with the confirmed brief or approved script.

Default handling:

- keep it inside `RENDER` when the brief and script are clear and the scene simply violated them
- return to `SCRIPT` when the brief is clear but the approved script is the layer that mismatched the intended beat structure or otherwise left scene work with script-layer incompleteness
- return to `PRE_BUILD_BRIEF` only when the mismatch proves unresolved semantic ambiguity, a missing upstream decision, conflicting upstream guidance, or a newly surfaced high-impact fork that was never frozen upstream

## PASS Standard

Pass only when:

- the scene is faithful to the contract
- the scene is visually readable
- layout is safe
- no unresolved semantic question remains visible to the reviewer
- `scene_review_result.md` is written by an independent reviewer rather than the render executor
- `scene_review_result.md` exists as the explicit review artifact; implicit passes, waivers, or undocumented substitutes do not count

## Common Failures

- Approving a scene because it runs, even though it invented semantics.
- Mislabeling a semantic problem as styling to avoid rollback.
- Returning `FAIL` without evidence or without naming the repair level.
- Treating support-structure removal as harmless cleanup when it changes the lesson.
