# Voiceover

This document defines voiceover work in `algorithm-teaching-animation-v3`.

When narration is required and no other language was explicitly approved, the default spoken language is English. Optional overlays remain separate and opt-in.

## Purpose

Voiceover should turn the approved teaching script into spoken guidance that is:

- natural to hear
- synchronized beat by beat
- faithful to the confirmed brief

Voiceover is not allowed to repair missing semantics by improvising new explanation.

## Start Gate

Narration work may start only after:

- the approved `pre_build_brief.md` exists
- `teaching_script.md` exists
- `script_review_result.md = PASS`

No narration work may begin before script review passes.

## Delivery-Tier Expectations

### Silent Preview

- no voiceover is required
- produce `voiceover_status.md` to record that narration is not owed for the frozen tier
- do not pretend an on-screen text-heavy scene is an audio-free substitute for clear teaching

### Voiceover Preview

- provide draft-quality spoken guidance
- provide draft-quality intelligible audio assets, not just planning files
- timing can still be refined, but the teaching logic must already be correct

### Final Narrated Delivery

- provide approved spoken segments and usable audio assets
- the delivered result must be ready for viewer-facing playback

## Required Artifacts

When the tier includes voiceover, produce:

- `voiceover.md` for the beat-level script
- `narration_manifest.json` for segment timing and file references
- `audio/voiceover/` for the generated or recorded audio files

The voiceover must stay beat-faithful to the approved script rather than inventing new teaching logic locally.

For silent tiers, do not produce `voiceover.md`, `narration_manifest.json`, or audio assets; instead preserve the explicit no-narration decision in `voiceover_status.md` tied to the frozen delivery tier.

## Recommended Structure

```md
# Voiceover

## Summary
- Language:
- Delivery tier:
- Source script:

## Beats

### beat-001: ...
- Scene hook:
- Narration:
- Pacing target:
- Pronunciation notes:
```

## Beat Rules

Each beat-level voiceover entry should include:

- a stable beat id or title
- the scene hook it speaks over
- the actual narration text
- a pacing target
- pronunciation notes only when needed

The narration should make sense when heard once, in real time.

## Writing Rules

- keep the narration faithful to the approved script
- explain why the current moment matters, not just what is visible
- use short, spoken sentences natural in the approved narration language
- prefer one main takeaway per beat
- if a line sounds like a paragraph from a textbook, rewrite it

## Source Contract

Derive the narration from:

- approved `pre_build_brief.md`
- approved `teaching_script.md`
- `script_review_result.md`

If `script_review_result.md` did not pass, stop and return to script repair instead of drafting narration around ambiguity.

## Sync Rules

- the visual focus should be established before the narration begins
- the beat should remain coherent until the narration ends
- if narration is too long, repair the script or split the beat upstream
- do not pad the scene with dead time to hide weak voiceover drafting

## Provider Contract

Any voiceover provider must support:

- input narration text per beat
- output audio per beat
- duration reporting per beat

Do not store secrets in skill artifacts.

For `voiceover preview`, draft-quality intelligible audio assets are required before `RENDER` and `QA`.
For `final narrated delivery`, viewer-usable audio assets are required before `RENDER` and `QA`. Do not defer actual audio-file production to `QA` or leave narrated tiers with only planning artifacts.

## Common Failures

- Reading the script too literally instead of writing for speech.
- Starting narration from an unreviewed script and forcing voiceover to choose missing teaching logic.
- Smuggling new semantic explanation into voiceover because the brief was thin.
- Treating missing audio files as acceptable for a narrated tier.
- Letting narration timing drift so far that the scene and speech stop matching.
