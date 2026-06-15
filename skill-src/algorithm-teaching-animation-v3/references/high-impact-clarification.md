# High-Impact Clarification

Use this reference to identify and ask only the decisions that would materially change the lesson contract.

## What Counts as High Impact

A gap is high impact when the answer would change any of:

- animation semantics
- teaching focus
- delivery content

If the answer changes only ordinary styling, routine pointer placement, or minor pacing, it is not high impact.

## Decision Classes

### Semantic Forks

Use this class when multiple reasonable interpretations exist and the choice changes what the viewer learns.

Examples:

- insertion sort movement model
- binary search interval convention
- whether graph traversal marks nodes on discovery or on processing

### Teaching-Focus Forks

Use this class when different emphases would change beat structure or visual attention.

Examples:

- binary search as interval reasoning versus branch-control reasoning
- BFS as queue behavior versus layer expansion
- sorting as movement intuition versus boundary progress

### Delivery-Affecting Forks

Use this class when the answer changes deliverable shape or layout obligations.

Examples:

- silent preview versus voiceover preview versus final narrated delivery
- whether overlays are enabled
- whether a support structure must remain visibly present

## First-Class Support Inventories

Use these compact inventories when the intake category is first-class support.

### Array Sorting

Check at least:

- active comparison unit
- meaningful movement-semantics fork
- settled-progress expression
- whether a temporary holding position is part of the lesson

### Binary Search and Two-Pointer Search

Check at least:

- interval convention
- pointer meaning
- stopping rule or success criterion
- whether the lesson emphasizes elimination logic, pointer choreography, or both

### BFS and DFS

Check at least:

- support-structure visibility
- visited timing
- discovery versus processing emphasis
- frontier or stack/path emphasis
- neighbor-order expectations when the sample input makes order visible

## What Not to Ask

Do not spend clarification budget on:

- ordinary color preferences
- default label micro-placement
- routine easing or timing polish
- normal camera restraint choices
- subtitle requests unless the user actually wants overlays

## Clarification Result Schema

Record the clarification result in this shape:

```md
# Clarification Result

## Resolved High-Impact Decisions
- Decision:
- Why it matters:
- Source: user answer / user-approved default

## Delivery Decisions
- Delivery tier:
- Overlay policy:

## Still Blocked
- None

## Proposed Agent Defaults
- Default:
- Why it is low risk:
```

## Proposed Default Rules

When proposing a default, phrase it as an explicit decision the user can approve or edit.

Good pattern:

- "If you do not have a preference, I will treat the active search interval as closed and keep eliminated regions dimmed."

Bad pattern:

- silently writing the interval rule into the brief
- asking a vague question with no explanation of why the choice matters

## Escalation Examples

- If intake suggested two plausible teaching framings and each would change beat emphasis, ask that teaching-focus fork directly instead of choosing one.
- If the user does not care about a high-impact semantic fork, offer a concrete default for approval rather than hiding it in the brief.
- If a delivery-tier change would also change overlays, narration, or support-structure visibility, freeze those decisions together.

## Common Failures

- Asking low-value questions while missing the semantic fork that actually matters.
- Treating a delivery decision as optional when it changes layout or outputs.
- Writing "follow standard semantics" when multiple standards exist.
- Smuggling unresolved ambiguity into broad wording such as "show the normal process."
