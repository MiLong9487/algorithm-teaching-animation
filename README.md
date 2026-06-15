# Algorithm Teaching Animation Skill

這是一個 Codex skill，用來把演算法名稱、範例輸入與特殊動畫需求，轉成先澄清高影響缺口、先確認 brief、再進入腳本、旁白、場景與 QA 的教學動畫工作流。

此 repo 目前提供的可安裝 skill package 是 `v3`。

## Repository Layout（儲存庫結構）

- `skill-src/algorithm-teaching-animation-v3/` - 可安裝的 skill package
- `skill-src/algorithm-teaching-animation-v3/SKILL.md` - 主要 skill 指令
- `skill-src/algorithm-teaching-animation-v3/references/` - 各 phase 專用參考文件
- `skill-src/algorithm-teaching-animation-v3/agents/` - phase-specific subagent contract
- `SKILL_INDEX.md` - 開發用的本機閱讀索引

## Install Locally（本機安裝）

將 skill package 複製或建立 symlink 到你的 Codex skills 目錄：

```powershell
Copy-Item -Recurse `
  -LiteralPath ".\skill-src\algorithm-teaching-animation-v3" `
  -Destination "$env:USERPROFILE\.codex\skills\algorithm-teaching-animation-v3"
```

接著重新啟動 Codex，或重新載入 skills。

## What The Skill Produces（輸出內容）

若進入完整 workflow，此 skill 預期至少會產生：

- `pre_build_brief.md`
- `teaching_script.md`
- `voiceover.md`
- `voiceover_segments.json`
- `narration_manifest.json`
- `generated_trace_script.py`
- `action_trace.json`
- `generated_algo_scene.py`
- `scene_review.md`
- `review_notes.md`

Rendered videos、Manim caches、generated audio 與 Python bytecode 會刻意被 Git 忽略。
