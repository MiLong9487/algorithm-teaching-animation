# Algorithm Teaching Animation Skill Index

此檔案是開發 v3 skill 時使用的本機閱讀索引，不屬於 runtime skill package。

## V3 Skill Package

- [SKILL.md](skill-src/algorithm-teaching-animation-v3/SKILL.md)
- [references](skill-src/algorithm-teaching-animation-v3/references)
- [agents](skill-src/algorithm-teaching-animation-v3/agents)

## References（參考文件）

- [Intake Contract](skill-src/algorithm-teaching-animation-v3/references/intake-contract.md)
- [High-Impact Clarification](skill-src/algorithm-teaching-animation-v3/references/high-impact-clarification.md)
- [Pre-Build Brief](skill-src/algorithm-teaching-animation-v3/references/pre-build-brief.md)
- [Teaching Script](skill-src/algorithm-teaching-animation-v3/references/teaching-script.md)
- [Voiceover](skill-src/algorithm-teaching-animation-v3/references/voiceover.md)
- [Visual Language](skill-src/algorithm-teaching-animation-v3/references/visual-language.md)
- [Default Visual Semantics](skill-src/algorithm-teaching-animation-v3/references/default-visual-semantics.md)
- [Manim Guidelines](skill-src/algorithm-teaching-animation-v3/references/manim-guidelines.md)
- [Script Review Checklist](skill-src/algorithm-teaching-animation-v3/references/script-review-checklist.md)
- [Scene Review Checklist](skill-src/algorithm-teaching-animation-v3/references/scene-review-checklist.md)
- [Render QA Checklist](skill-src/algorithm-teaching-animation-v3/references/render-qa-checklist.md)

## Agents（代理角色）

- [clarification-planner](skill-src/algorithm-teaching-animation-v3/agents/clarification-planner.md)
- [brief-editor](skill-src/algorithm-teaching-animation-v3/agents/brief-editor.md)
- [layout-checker](skill-src/algorithm-teaching-animation-v3/agents/layout-checker.md)
- [script-writer](skill-src/algorithm-teaching-animation-v3/agents/script-writer.md)
- [script-reviewer](skill-src/algorithm-teaching-animation-v3/agents/script-reviewer.md)
- [voiceover-manifest](skill-src/algorithm-teaching-animation-v3/agents/voiceover-manifest.md)
- [scene-writer](skill-src/algorithm-teaching-animation-v3/agents/scene-writer.md)
- [scene-reviewer](skill-src/algorithm-teaching-animation-v3/agents/scene-reviewer.md)
- [qa-verifier](skill-src/algorithm-teaching-animation-v3/agents/qa-verifier.md)

## Suggested Reading Flow（建議閱讀順序）

1. 閱讀 `SKILL.md`，先確認 `INTAKE -> CLARIFICATION -> PRE_BUILD_BRIEF` 的 gate。
2. 只開啟目前要修改 phase 所需的 reference file。
3. 對照最接近的 agent contract，而不是回讀整包歷史 example。
