# Manim Layout Audit

Use this reference when reviewing or hardening `generated_algo_scene.py` for layout problems such as overlapping labels, text outside panels, title collisions, or elements drifting out of frame.

## Purpose

Manim layout bugs are best checked after mobjects exist. Static code review cannot reliably know the size of rendered `Text`, font fallback, transformed objects, or dynamic trace-driven labels.

Use the bundled script `scripts/manim_layout_audit.py` as a small reusable helper copied into the generated Manim project.

## When to Add It

Add the audit helper during `RENDER AND REVIEW` when:

- the scene contains panels, legends, invariant boxes, dynamic path text, tables, graph labels, or multiple text regions
- generated text comes from `action_trace.json`
- a preview render shows crowding or possible overlap
- the user asks to detect layout issues automatically
- CI or repeated generation should fail on obvious visual collisions

For tiny scenes with one or two fixed objects, a visual review may be enough.

## Install Into a Project

Copy the helper into the same folder as `generated_algo_scene.py`:

```text
<project>/
├── generated_algo_scene.py
└── manim_layout_audit.py
```

Then import it:

```python
import os
from manim_layout_audit import LayoutAudit

LAYOUT_AUDIT_ENABLED = os.getenv("MANIM_LAYOUT_AUDIT", "1").lower() not in {"0", "false", "no"}
LAYOUT_AUDIT_FAIL = os.getenv("MANIM_LAYOUT_AUDIT_FAIL", "0").lower() in {"1", "true", "yes"}
```

## Scene Adapter Pattern

Keep project-specific knowledge in a thin adapter inside the scene. The helper should stay generic.

```python
def _audit_layout(self, context, nodes, labels, panels, header=None, extra_items=None):
    audit = LayoutAudit(context=context, enabled=LAYOUT_AUDIT_ENABLED)
    header = header or []
    extra_items = extra_items or []
    all_items = nodes + labels + panels + header + extra_items

    for name, mob in all_items:
        audit.check_inside_frame(name, mob)

    audit.check_no_internal_overlaps(labels, min_gap=0.05)
    audit.check_no_overlaps_between(labels, nodes, min_gap=0.03)
    audit.check_no_overlaps_between(nodes + labels, panels, min_gap=0.05)
    audit.check_no_overlaps_between(header + extra_items, nodes + labels + panels, min_gap=0.05)
    audit.report(raise_on_issue=LAYOUT_AUDIT_FAIL)
```

Call the adapter after stable states, not just at the beginning:

```python
self._audit_layout("initial", nodes, labels, panels, header=[("title", title)])
self._audit_layout(f"beat:{beat_id}", nodes, labels, panels, header=[("title", title), ("message", message)])
self._audit_layout("final", nodes, labels, panels, extra_items=[("result", result_text)])
```

## Common Checks

- `check_inside_frame(name, mob, margin=0.1)` detects out-of-frame objects.
- `check_fits(inner_name, inner, outer_name, outer, padding=0.15)` detects text that does not fit inside a panel or box.
- `check_no_overlap(a_name, a, b_name, b, min_gap=0.05)` detects true overlaps and near misses.
- `check_no_internal_overlaps(items, min_gap=0.05)` checks repeated labels or table cells.
- `check_no_overlaps_between(group_a, group_b, min_gap=0.05)` checks whole categories.

`check_no_overlap` reports true bounding-box intersection as `overlaps`; if objects do not intersect but violate `min_gap`, it reports `is too close to`. Treat these differently in review.

## Review Rules

- Treat warnings as candidates, not final truth.
- Compare warnings against a render or extracted still frames.
- Ignore transient warnings from in-between animation frames unless they persist in stable frames.
- If a warning references a helper panel that is absent from the MP4, verify the MP4 was rendered from the same `generated_algo_scene.py`.
- Prefer fixing repeated stable-frame warnings in `generated_algo_scene.py`.
- If the scene cannot express a needed layout state from trace data, fix the trace schema or teaching script first.

## CI Usage

Default behavior prints warnings and lets render continue:

```bash
manim -ql generated_algo_scene.py AlgorithmScene
```

Disable audits:

```bash
MANIM_LAYOUT_AUDIT=0 manim -ql generated_algo_scene.py AlgorithmScene
```

Fail on audit findings:

```bash
MANIM_LAYOUT_AUDIT_FAIL=1 manim -ql generated_algo_scene.py AlgorithmScene
```

On Windows PowerShell:

```powershell
$env:MANIM_LAYOUT_AUDIT_FAIL = "1"
python -m manim -ql .\generated_algo_scene.py AlgorithmScene
```

## Avoid Overreach

Do not rely only on bounding boxes for arrows or curved paths. Arrow bounding boxes often cover large empty triangular regions and can create false positives. Prefer checking labels, nodes, text panels, headers, legends, tables, and result text first. Add line/path-specific checks only when the project has a concrete need.
