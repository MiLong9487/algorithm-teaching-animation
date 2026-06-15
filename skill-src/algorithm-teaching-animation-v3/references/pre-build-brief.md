# Pre-build Brief

This document defines `pre_build_brief.md`, the core gate artifact in `algorithm-teaching-animation-v3`.

No script, voiceover, or scene work may begin until this brief is confirmed.

## Purpose

`pre_build_brief.md` is the single shared contract for:

- script writing
- script review
- voiceover planning
- scene implementation
- scene review
- render QA

It exists so downstream work can be strict without inventing semantics late.

## Confirmation Gate

The brief passes the gate only when one of these happens:

- the user gives explicit approval
- the user requests targeted edits and then approves proceeding

The brief does not pass on:

- silence
- implied agreement
- "looks fine" when unresolved forks remain hidden

## Required Sections

Every brief must include:

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
- `Narration Language`
- `Known Risks / Best-Effort Notes`

If any of these sections would be vague because a high-impact question remains open, the brief is not ready.

## Section Guidance

### Algorithm Identity

State the algorithm or concept plainly. If the request is variant-specific, name the variant.

### Teaching Goal

State the main thing the viewer should understand by the end.

### Audience

Record the user's audience if given. Otherwise state the working assumption.

### Sample Input / Scenario

Use a concrete case the scene can actually build around.

### Confirmed User Requests

List only explicit user asks, not agent guesses.

### Resolved High-Impact Clarifications

List each frozen decision and why it matters. This section is where the workflow proves that clarification was completed.

### Agent Default Decisions

Record only low-risk defaults from `default-visual-semantics.md` or other non-semantic conventions.

### Chosen Visual Semantics

Describe the specific viewer-facing rules the scene must honor.

Examples:

- how active regions are shown
- what counts as settled progress
- how support structures remain visible

### Pointer / Boundary / Temp Slot Plan

Make pointer meaning explicit. If a temporary holding area is part of the lesson, say so here. If none exists, say that too.

### Beat Outline

Give the high-level lesson arc, not full narration.

### Overlay Policy

State whether overlays are off, optional, or required.

### Delivery Tier

State exactly one of:

- `silent preview`
- `voiceover preview`
- `final narrated delivery`

### Narration Language

If the delivery tier is `silent preview`, state that no narration is owed.

If the delivery tier requires narration, freeze the spoken language explicitly.

If the user did not specify a narration language and the workflow applies the default, record that the language was defaulted to English instead of presenting it as a user instruction.

### Known Risks / Best-Effort Notes

Use this section to document support-tier limits, layout pressure, or remaining non-semantic uncertainty.

## Writing Rules

- write concrete viewer-facing language
- avoid implementation trivia unless it changes the lesson
- do not hide semantic forks behind broad wording
- separate explicit user requests from agent defaults
- keep the brief strong enough that script and scene agents can be audited against it

## Planning Discipline

Before the brief is approved:

- normalize the request into a concrete algorithm target and sample scenario
- surface every high-impact semantic or delivery-affecting fork before writing beats
- freeze the delivery tier, narration language, and overlay policy strongly enough that downstream phases do not guess
- do not keep a parallel "real plan" that silently outranks the brief

Temporary scratch notes are allowed, but any decision that matters downstream must appear in `pre_build_brief.md`.

If the request is best-effort support, say so explicitly in `Known Risks / Best-Effort Notes` instead of weakening the contract language elsewhere.

## Beat Outline Guidance

The beat outline should answer:

- what stable mental model the viewer needs first
- what local action changes that model
- what progress cue should persist after the action
- which support structure is teaching-critical
- where a viewer is most likely to misread the algorithm

## Failure Conditions

The brief fails when:

- a known high-impact issue is missing
- semantics are vague enough to support multiple conflicting scenes
- delivery obligations are unstated
- narration language obligations are unstated or hidden inside implied defaults
- overlay policy is unstated
- the beat outline cannot be reconciled with the frozen semantics

## Recommended Template

```md
# Pre-build Brief

## Algorithm Identity

## Teaching Goal

## Audience

## Sample Input / Scenario

## Confirmed User Requests

## Resolved High-Impact Clarifications

## Agent Default Decisions

## Chosen Visual Semantics

## Pointer / Boundary / Temp Slot Plan

## Beat Outline

## Overlay Policy

## Delivery Tier

## Narration Language

## Known Risks / Best-Effort Notes
```

## Downstream Rule

After confirmation, downstream phases may refine styling and execution, but they may not revise the semantics frozen here.

If a new high-impact fork appears later, the workflow must return to this phase and confirm an updated brief before continuing.
