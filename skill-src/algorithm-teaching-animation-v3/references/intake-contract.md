# Intake Contract

Use this reference to normalize a minimal request into intake notes without freezing later semantic choices.

## Minimum Expected Input

Start intake as soon as you have:

- algorithm name
- sample input or target scenario
- special animation preference, if any

Useful optional inputs:

- audience notes
- desired delivery tier
- pseudocode or implementation code
- known semantic preferences
- explicit overlay requests

## Intake Summary Schema

Produce a compact working summary in this shape:

```md
# Intake Summary

- Algorithm:
- Sample input / scenario:
- Explicit user requests:
- Likely support category:
- Candidate teaching framing:
- Suggested delivery tier:
- Likely high-impact gaps:
```

Keep `Candidate teaching framing` lightweight:

- a `primary framing`
- an optional `secondary framing`
- a short note about why that framing matches the user goal
- the semantic or teaching-focus areas most likely to matter in clarification

## Classification Rules

### First-Class Support

Treat these as first-class support:

- array sorting
- binary search or two-pointer style searching
- basic graph traversal such as BFS or DFS

### Best-Effort Support

Treat categories such as these as best-effort unless the skill adds stronger local guidance:

- dynamic programming table construction
- tree transformations
- greedy or interval algorithms
- specialized graph algorithms

Best-effort status should be visible in later brief notes, not hidden.

## Candidate Teaching Framing

Intake may suggest a likely framing, but it must not lock semantics.

Common framings:

- algorithm walkthrough
- pointer and boundary explainer
- graph traversal explainer
- state-construction explainer
- comparison or intuition explainer

If multiple framings are plausible, carry the ambiguity forward instead of collapsing it early.

## Intake Rules

- Preserve user wording for special requests.
- Do not spend intake budget on low-value styling questions.
- Do not require code when the algorithm and scenario are already clear.
- Do not silently infer final semantics from code unless the user wants code-faithful behavior.
- Do not let one flashy request distort the main teaching target.

## When to Use Code or Pseudocode

Use code or pseudocode to:

- confirm control flow
- resolve implementation-specific branches after code fidelity is made relevant
- disambiguate edge cases that affect the lesson

Do not use code or pseudocode to:

- bypass clarification
- override an explicit teaching preference
- force a concept-first request into a code-first explanation

## Escalation Examples

- If the sample input is missing and the algorithm depends on visible ordering or structure shape, flag the missing scenario for clarification.
- If the user's concept goal and supplied code imply different semantics, preserve both signals and escalate the conflict instead of choosing one.
- If two teaching framings would lead to different beat emphasis, record both as candidate framing and let clarification resolve the emphasis.

## Common Failures

- Refusing to start because the user did not provide code.
- Treating a concrete sample scenario as optional when the lesson depends on it.
- Converting a candidate teaching framing into a settled semantic decision.
- Losing explicit user requests while summarizing the intake.
