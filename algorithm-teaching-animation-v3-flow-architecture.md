# algorithm-teaching-animation-v3 流程架構說明

## 核心定位

這個 skill 是一套 `balanced-brief-first` workflow。和 v2 最大的差異在於：v3 把「先問清楚再動手」提升為正式 phase，並用一份可確認的 `pre_build_brief.md` 取代 v2 的 `plan.md` + `trace` 雙層設計，成為整條 pipeline 唯一的語義權威。

agent 看到使用者給的演算法後，會按照 SKILL.md 定義的 8 個階段工作，並在每一階段產生明確 artifact，只有通過 gate 才能進下一層。

所以這個 skill 的本質是：

`最小輸入` -> `辨識高影響缺口` -> `澄清並凍結語義` -> `產出 brief 並取得確認` -> `逐層產生 script / voiceover / scene` -> `QA 驗證` -> `宣稱交付等級`

## 先講最重要的一件事

如果你問「輸入一個演算法之後，這個 skill 到底怎麼動」，最準確的回答是：

1. agent 先用最少資訊啟動，把你的需求正規化成教學目標
2. 主動辨識會改變動畫語義、教學焦點或交付內容的高影響缺口
3. 把所有高影響問題一次問完，凍結答案
4. 產出一份 `pre_build_brief.md`，等你明確核可
5. 核可後才依序寫 script、voiceover、scene
6. 任何一層有問題，都要回 brief 層修，不准在 scene 層補救語義

## v3 與 v2 的關鍵差異

| 面向 | v2 | v3 |
|---|---|---|
| 啟動門檻 | 需要較完整需求描述 | 最小輸入：演算法名 + 範例輸入 + 特殊動畫偏好 |
| 語義權威 | `plan.md` + `action_trace.json` 雙層 | 單一 `pre_build_brief.md` |
| 澄清機制 | optional features negotiation | 正式 `CLARIFICATION` phase，high-impact only |
| Trace 層 | 獨立 `TRACE` phase，產出 deterministic trace | 取消獨立 trace phase；語義凍結在 brief |
| Compliance 機制 | COMPLIANCE PLAN / PHASE RESULT / COMPLIANCE REPORT | 以 brief confirmation gate 為核心，各 phase 有 gate 但無強制 compliance report 格式 |
| Subagent 數量 | 10 個角色 | 10 個角色（新增 `clarification-planner`、`brief-editor`；移除 `trace-contract`、`trace-writer`） |
| 回退規則 | scene semantic issue 不回退 trace/script | 任何語義問題一律回 `PRE_BUILD_BRIEF`，必要時重開 `CLARIFICATION` |

## v3 的預設交付 profile

預設交付應為：

- 純演算法主體動畫
- 必要 pointer / boundary / temp slot / index label
- 英文 voiceover
- **不**自動加入 `code panel`
- **不**自動加入 `note panel`
- **不**自動加入 `summary panel`
- **不**自動加入畫面字幕

也就是說，v3 的預設和 v2 相同：「主體動畫 + 旁白」。optional overlays 一律 opt-in。

## Subagent orchestration

此 skill 共 10 個 subagent 角色：

1. `mode-planner` — 判斷 primary/secondary teaching mode
2. `clarification-planner` — 辨識所有高影響缺口，產出澄清問題集
3. `brief-editor` — 產出 `pre_build_brief.md`
4. `layout-checker` — 檢查 layout 可行性、collision risk、密度風險
5. `script-writer` — 撰寫 `teaching_script.md`
6. `script-reviewer` — 審查 script gate
7. `voiceover-manifest` — 產出旁白稿與 timing contract
8. `scene-writer` — 產出或修正 `generated_algo_scene.py`
9. `scene-reviewer` — scene gate 唯一審查者
10. `qa-verifier` — 驗證 render 結果

各 subagent 規格放在 `agents/` 目錄。每個 agent 都有統一的結構：Role、Required outputs、Rules、Fail conditions、Rollback rule。

### 主 agent 的責任

- 在每個 phase 啟動對應 subagent
- 在每個 gate 後回收決策權
- 確保 brief 通過 explicit approval 才進 SCRIPT
- 確保語義問題回退到正確層級
- 不在 scene 層補救語義缺口

### Main agent decision points

主 agent 在以下節點回收決策權：

- `mode-planner` 後 → 鎖定 `primary mode` 與 `secondary mode`
- `clarification-planner` 後 → 決定是否需要向使用者提問，或已無高影響缺口
- `brief-editor` 後 → 向使用者提交 brief 等待 explicit approval
- `layout-checker` 後 → 鎖定 layout feasibility verdict
- `script-reviewer` 後 → 決定 script 是否通過
- `voiceover-manifest` 後 → 決定是否已達 voiceover 前置條件
- 每一輪 `scene-reviewer` 後 → 決定 preview render 或重開 `scene-writer`
- `qa-verifier` 後 → 決定交付分類

### Scene iteration contract

- 第一次 `scene-writer`：建 scene 初稿
- 第二次以後：視為 `repair writer`
- `repair writer` 必須讀前一版 scene code 與最新 `scene_review.md`
- `repair writer` 不得忽略 reviewer findings 重新自由發揮
- 每次修正都重新開一個新的 `scene-writer` instance

---

## 輸入一個演算法後，agent 會怎麼做

假設你給 agent 的輸入是：演算法名稱、範例輸入、特殊動畫偏好。  
agent 不會直接寫 scene。它會按以下 8 個 phase 執行。

---

## 第 1 步：INTAKE

agent 先把你的輸入正規化成教學任務。規範在 `references/intake-contract.md`。

### INTAKE 的最小輸入

- algorithm name
- sample input or target scenario
- special animation preference（如果有）

其他都是 optional support material：audience notes、delivery tier、pseudocode、overlay requests 等。

### INTAKE 在做什麼

1. **正規化請求** — 將使用者輸入轉為明確教學目標
2. **分類支援等級** — 判斷是 first-class support 還是 best-effort support
3. **保留所有明確需求** — 不遺漏使用者的 exact wording
4. **辨識可能的高影響缺口** — 為下一步 CLARIFICATION 做準備

### 支援等級分類

**First-class support**（更強 defaults、更嚴 checklist）：
- array sorting
- binary search / two-pointer search
- basic graph traversal（BFS / DFS）

**Best-effort support**（必須在 brief 中明確標示）：
- dynamic programming table construction
- tree transformations
- greedy / interval algorithms
- specialized graph algorithms

### Candidate teaching mode

INTAKE 只提出候選 mode，不凍結：
- `algorithm walkthrough`
- `pointer and boundary explainer`
- `graph traversal explainer`
- `state-construction explainer`
- `comparison or intuition explainer`

若多個 mode 可能，把歧義帶進 CLARIFICATION。

### INTAKE 結束條件

- 最小輸入已到位
- 演算法家族已分類
- 明確使用者需求已捕捉
- 可能的高影響缺口已列出

### Intake Summary 格式

```md
# Intake Summary

- Algorithm:
- Sample input / scenario:
- Explicit user requests:
- Likely support category:
- Candidate teaching mode:
- Likely high-impact gaps:
- Suggested delivery tier:
```

---

## 第 2 步：CLARIFICATION

只問會改變動畫語義、教學焦點或交付內容的高影響問題。規範在 `references/high-impact-clarification.md`。

預設 subagents：`mode-planner` + `clarification-planner`

### CLARIFICATION 子流程

1. 啟動 `mode-planner` → 鎖定 primary/secondary mode
2. 啟動 `clarification-planner` → 辨識所有高影響缺口，產出問題集
3. 主 agent 向使用者提出所有已辨識的高影響問題
4. 收到答案後凍結決策

### 三種高影響缺口類型

**Semantic forks** — 多種合理視覺詮釋存在，選擇會改變觀眾學到什麼：
- insertion sort 的移動模型
- binary search 的區間慣例
- graph traversal 的 visited timing

**Teaching-focus forks** — 不同重點會改變 beat 結構或視覺焦點：
- binary search 是區間推理 vs 分支控制推理
- BFS 是 queue behavior vs layer expansion
- sorting 是 movement intuition vs boundary progress

**Delivery-affecting forks** — 答案改變交付物形狀或 layout 義務：
- silent preview vs voiceover preview vs final narrated delivery
- overlay 是否啟用
- support structure 是否必須可見

### Ask-all-identified-high-impact 規則

一旦辨識為高影響缺口，不得靜默預設：

允許的結果：
- 使用者直接回答
- 使用者明確核可 proposed default
- workflow 停止等待回答

不允許的結果：
- agent 自行假設語義答案
- 只問一個高影響問題而留下其他隱含
- 用模糊措辭在 brief 裡藏匿歧義

### First-class support 的 hybrid inventory

**Array sorting** — 至少確認：comparison unit、movement semantics fork、settled progress expression、temporary holding position

**Binary search / two-pointer** — 至少確認：interval convention、pointer meaning、stopping rule、teaching emphasis

**BFS / DFS** — 至少確認：support structure visibility、visited timing、discovery vs processing emphasis、frontier emphasis、neighbor-order expectations

### CLARIFICATION 結束條件

- 所有已辨識高影響缺口已解決或明確阻塞
- delivery tier 已凍結
- overlay policy 已凍結
- brief 可以寫出具體語義而無歧義

---

## 第 3 步：PRE_BUILD_BRIEF

把澄清結果轉成可確認的語義契約。規範在 `references/pre-build-brief.md`。

預設 subagents：`brief-editor` + `layout-checker`

### PRE_BUILD_BRIEF 子流程

1. 啟動 `brief-editor` → 產出 `pre_build_brief.md`
2. 啟動 `layout-checker` → 驗證 layout feasibility
3. 主 agent 整合結果
4. 向使用者提交 brief，等待 **explicit approval**
5. 使用者核可或要求 targeted edit + proceed

### `pre_build_brief.md` 必要章節

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

### Confirmation gate

Brief 只在以下情況通過 gate：

- 使用者給出 explicit approval
- 使用者要求 targeted edits 並核可繼續

Brief **不**在以下情況通過：

- 沉默
- 隱含同意
- 仍有未解決高影響缺口時說「looks fine」

### Brief 的核心角色

`pre_build_brief.md` 是 v3 整條 pipeline 的**唯一語義權威**。downstream 所有 phase（SCRIPT、VOICEOVER、RENDER、QA）都必須以 confirmed brief 為 source of truth。不得建立平行的「真正計畫」來覆蓋 brief。

### Layout checker verdict

- `PASS` — layout 可行
- `PASS WITH WARNINGS` — 可行但有風險需注意
- `FAIL` — 語義負載超出可讀 layout 能力

風險分類：
- `render-fixable` — spacing、staging、camera framing 可解
- `brief-level overload` — 需回 brief 減少語義負載或調整結構

### Brief gate

未滿足以下條件，不得進入 SCRIPT：

- 所有必要章節已填寫且具體
- 所有已辨識高影響問題已解決
- delivery tier 已明確
- overlay policy 已明確
- beat outline 與凍結語義可調和
- layout checker 未回報 `FAIL`（或 FAIL 已修正）
- 使用者已 explicit approve

---

## 第 4 步：SCRIPT

有了 confirmed brief 後，agent 才寫 `teaching_script.md`。規範在 `references/teaching-script.md`。

預設 subagents：`script-writer` + `script-reviewer`

### SCRIPT 子流程

1. 啟動 `script-writer` → 產出 `teaching_script.md`
2. 啟動 `script-reviewer` → 審查 script
3. 主 agent 決定 script 是否通過
4. 若 fail，重開新的 `script-writer`

### SCRIPT 在做什麼

1. **根據 brief 切 beat** — 一拍只講一個主要教學重點
2. **為每個 beat 定義教學內容** — viewer goal、algorithm moment、visual focus、teaching note、progress cue、voiceover intent
3. **寫出 `teaching_script.md`**

Script 是教學結構層，不是 trace 替代品，也不是 scene 描述。

### Script 的 source of truth

- confirmed `pre_build_brief.md`
- 具體範例輸入或情境
- code/pseudocode 僅在需要忠實呈現演算法流程時使用

若 script 需要 brief 未提供的語義選擇，必須停止並回退上游。

### Script gate

- 每個 beat 只有一個主要教學重點
- beat 順序忠實於凍結語義
- script 與 brief 逐 beat 對照一致
- 教學重點沒有超出 brief 所凍結的語義
- 沒有隱藏的語義替換或漂移

### Script reviewer 的輸出

- `Script Review Result`：`PASS` 或 `FAIL`
- drift / omission / contradiction 列表
- repair note 指出修正歸屬：`SCRIPT` 或 `PRE_BUILD_BRIEF`

---

## 第 5 步：VOICEOVER

把 teaching script 轉成旁白結構。規範在 `references/voiceover.md`。

預設 subagent：`voiceover-manifest`

### VOICEOVER 子流程

1. 啟動 `voiceover-manifest`
2. 主 agent 決定是否已達 voiceover 前置條件

### VOICEOVER 在做什麼

1. **把 teaching beat 轉成可朗讀旁白** — 自然口語英文
2. **寫出 `voiceover.md`** — beat-level 旁白稿
3. **產生 `narration_manifest.json`** — segment timing 與檔案參考
4. **產生音訊檔** — `audio/voiceover/*.wav`（若 TTS provider 可用）

### Delivery-tier expectations

- **silent preview** — 不需要 voiceover
- **voiceover preview** — draft-quality 口語引導，timing 可微調但教學邏輯必須正確
- **final narrated delivery** — 完整口語段落與可用音訊資產，可直接面向觀眾播放

### Voiceover rules

- 預設語言：English（除非使用者明確更改）
- 忠實於 approved script 的 beat 結構
- 不得透過即興解釋來修補 brief 缺失的語義
- optional overlays 不受 voiceover 暗中啟用
- 視覺焦點應在對應旁白開始前建立

### Voiceover gate

- voiceover 忠實反映 approved script
- timing 與 beat mapping 一致
- 未改變 delivery tier 或 overlay expectations
- 若宣稱有聲版本，音訊檔實際存在且可播放

---

## 第 6 步：RENDER

到這一步才生成 `generated_algo_scene.py`。規範在 `references/manim-guidelines.md`、`references/visual-language.md`、`references/scene-review-checklist.md`。

預設 subagents：`scene-writer` + `scene-reviewer`

此階段固定拆成子步驟：`SCENE_BUILD` → `SCENE_REVIEW_AND_REPAIR` → `PREVIEW_RENDER`

### RENDER 子流程

1. 啟動第一次 `scene-writer`
2. 啟動 `scene-reviewer`
3. 若 fail，主 agent 開新的 `scene-writer` instance（repair writer）
4. 重複 `scene-writer` → `scene-reviewer`，直到 scene gate 通過
5. 通過後才做 preview render

### Scene layer 擁有什麼

- layout execution
- styling
- timing
- beat staging
- audio / overlay synchronization

### Scene layer 不擁有什麼

- 語義 fork 決策
- delivery-tier 變更
- 新 support-structure 需求
- 對教學目標的重新詮釋

### Scene 的 source of truth

- confirmed `pre_build_brief.md`（語義權威）
- approved `teaching_script.md`（教學結構權威）
- approved voiceover artifacts（若 tier 包含音訊）

### Render-layer fix policy

**允許在 RENDER 內修正**：
- color styling
- label micro-placement
- spacing / safe-margin tuning
- animation pacing
- implementation-fidelity repairs（不改變凍結語義）

**不允許在 RENDER 內修正**：
- 改變 movement semantics
- 改變 pointer meaning
- 改變 visited timing
- 改變教學用 support structure
- 改變 delivery-tier obligations

若修正跨入不允許區域，必須停止並回退到 `PRE_BUILD_BRIEF`。

### Scene reviewer 的輸出

- `Scene Review Result`：`PASS` 或 `FAIL`
- 分類 findings：`styling`、`layout`、`semantic ambiguity`、`contract mismatch`
- `contract mismatch` 的 Level 判定：
  - **Level 1**（預設）— brief 和 script 清楚，scene 只是違反了已凍結的 contract → 留在 RENDER 修
  - **Level 2** — mismatch 暴露了 brief 或 script 的語義不完整或內部矛盾 → 回 `PRE_BUILD_BRIEF`
- repair direction：`Level 1: stay within RENDER` 或 `Level 2: return to PRE_BUILD_BRIEF`
- evidence references

### Render gate

- `generated_algo_scene.py` 已生成
- `scene_review.md` 已記錄 scene review 與修正結果
- scene 忠實於 contract
- scene 視覺可讀
- layout 安全
- 無未解決語義問題
- scene 已可直接進 preview render

---

## 第 7 步：QA

render 完不算完成，還要進 QA。規範在 `references/render-qa-checklist.md`。

預設 subagent：`qa-verifier`

### QA 子流程

1. preview render 或 final render 完成
2. 啟動 `qa-verifier`
3. 主 agent 根據 QA Result 做交付分類或要求 refinement

### QA 必查項

**Visual readability**：
- 主要結構全程可讀
- 每個 beat 的 active focus 明確
- settled / excluded regions 可辨識
- labels 可讀且不碰撞
- 重要內容未被裁切或隱藏

**Contract fidelity**：
- render 符合凍結語義
- support structures 在需要時出現
- 未在實作中新增語義
- overlay 行為符合 brief

**Timing and audio**：
- beat pacing 給觀眾足夠時間理解變化
- voiceover 在視覺 hook 建立後才開始
- 長停頓有教學價值，不是空白時間
- 旁白與畫面不矛盾

**Delivery completeness**：
- 正確 tier 已實際產出
- 該 tier 所需檔案存在且可用
- preview 未被誤標為 final

### QA repair direction

- `stay within RENDER` — layout、spacing、timing、styling、fidelity repairs
- `return to SCRIPT` — script-structure mismatches
- `return to PRE_BUILD_BRIEF` — semantic ambiguity、missing upstream decision、delivery-contract drift

### QA gate

- 選定 delivery tier 已滿足
- render 可讀
- contract 忠實實作
- 無未解決語義歧義對觀眾可見

---

## 第 8 步：DELIVERY

最後 agent 才能宣稱交付等級。

### 交付分類（只可使用以下三種）

- `silent preview` — 有可檢查畫面，沒有旁白音訊
- `voiceover preview` — 有完整 voiceover artifacts，可用 beat audio 預覽，但尚未完成正式 mux 驗證
- `final narrated delivery` — 有完整 narration track、已完成 final video 與 audio mux、已驗證可面向觀眾播放

### DELIVERY 在做什麼

1. **判定交付等級** — 正式 classification
2. **列出目前可交付內容** — 所有已完成 artifact
3. **明確指出剩餘缺口與回修層級**

---

## 完整 workflow 的必要產出物

- `pre_build_brief.md`
- `teaching_script.md`
- `voiceover.md`
- `narration_manifest.json`
- `generated_algo_scene.py`
- `scene_review.md`
- `review_notes.md`

若 TTS provider 可用：`audio/voiceover/*.wav`

---

## 回退規則總覽

v3 的回退規則統一且嚴格：

| 問題類型 | 回退目標 |
|---|---|
| styling / spacing / layout execution | 留在 `RENDER` |
| implementation fidelity（不涉及語義） | 留在 `RENDER` |
| script structure / pacing / beat organization | 回 `SCRIPT` |
| semantic ambiguity / semantic mismatch | 回 `PRE_BUILD_BRIEF` |
| 新發現的高影響 fork | 回 `PRE_BUILD_BRIEF`，必要時重開 `CLARIFICATION` |
| delivery-contract drift | 回 `PRE_BUILD_BRIEF` |
| brief 語義不完整或內部矛盾 | 回 `PRE_BUILD_BRIEF` + `CLARIFICATION` |

核心原則：**不在下游用 workaround 修補上游語義問題。**

---

## Default visual semantics

v3 引入了 `references/default-visual-semantics.md` 來處理低風險視覺預設，避免為了小事回 CLARIFICATION。

### 使用 defaults 的場景

- stable role styling（base、focus、candidate、settled、excluded、support）
- ordinary pointer placement
- routine label wording
- ordinary beat pacing
- common first-class support layouts

### 不可用 defaults 決定的事

- movement semantics（改變觀眾學到什麼的）
- search variant semantics
- pointer meaning
- visited timing
- overlay enablement
- delivery tier

這些屬於高影響決策，必須在 `pre_build_brief.md` 中凍結。

### Escalation rule

若某個 presentational choice 會迫使觀眾推斷一條 brief 從未凍結的語義規則，必須停用 defaults 並回退到 brief。

---

## 不應做的事

- 跳過 INTAKE 和 CLARIFICATION 直接寫 scene
- 在 brief 未經 explicit approval 前進入 SCRIPT
- 讓 scene 自行決定或補完演算法語義
- 用 render 層 workaround 掩蓋語義歧義
- 未經使用者確認就啟用 code panel / note panel / summary panel / 字幕
- 在 brief 中用模糊措辭藏匿未解決的語義 fork
- 問低價值 styling 問題浪費澄清預算
- 混淆 user-confirmed 決策與 agent default 決策
- 把 brief-level overload 問題當成簡單 render tweak
- silent fallback 成單 agent 流程
- 讓同一個 `scene-writer` thread 反覆自修

---

## 按需載入順序

- `INTAKE` → `references/intake-contract.md`
- `CLARIFICATION` → `references/high-impact-clarification.md`、`references/planning.md`
- `PRE_BUILD_BRIEF` → `references/pre-build-brief.md`、`references/default-visual-semantics.md`
- `SCRIPT` → `references/teaching-script.md`
- `VOICEOVER` → `references/voiceover.md`
- `RENDER` → `references/manim-guidelines.md`、`references/visual-language.md`、`references/scene-review-checklist.md`
- `QA` → `references/render-qa-checklist.md`

---

## 把整個流程更具象化

如果你輸入一個演算法，agent 實際上會做的是：

先用最少資訊啟動，辨識「哪些選擇會改變這個動畫的教學意義」  
再把那些選擇一次問完，凍結答案  
再把凍結的語義寫成一份 brief，等你明確核可  
核可後才決定「這些語義要切成哪些 beat」  
再決定「每個 beat 要講什麼、講多久」  
最後才把它畫成 Manim scene，並驗證成品是否忠實於 brief、script 與交付契約。

整個過程以 confirmed `pre_build_brief.md` 為語義核心：上游負責把它寫清楚，下游負責忠實實作它。

## 你可以把這個 skill 想成三個轉譯器串在一起

1. 最小輸入 -> 澄清後的語義契約（brief）
2. 語義契約 -> 結構化 script / voiceover
3. 結構化 artifact -> 動畫與音訊成品

每一層轉譯都有 gate，都有 subagent 負責，語義問題一律回 brief 層處理。
