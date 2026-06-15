# algorithm-teaching-animation-v2 流程架構說明

## 核心定位

這個 skill 不是「丟進一個演算法，然後某支固定程式自動跑完」；它是一套強制流程的製作規範。  
agent 看到使用者給的演算法後，會按照 SKILL.md 定義的 7 個階段工作，並在每一階段產生明確 artifact，只有通過 gate 才能進下一層。

所以這個 skill 的本質是：

`使用者輸入` -> `agent 依 skill 規範做決策` -> `逐層產生文件 / trace / scene / audio` -> `QA 驗證` -> `宣稱交付等級`

## 先講最重要的一件事

如果你問「輸入一個演算法之後，這個 skill 到底怎麼動」，最準確的回答是：

1. agent 先把你的需求翻成「教學任務」
2. 再把教學任務拆成「可驗證的中間產物」
3. 再把中間產物一路往下轉成動畫與旁白
4. 任何一層有問題，都要回上一層修，不准直接靠 scene 補救

## v2 的預設交付 profile

v2 和一般教學動畫 workflow 最大的差別之一，是它的預設不是「把所有教學輔助層都打開」。

預設交付應為：

- 純演算法主體動畫
- 必要 pointer / boundary / temp slot / index label
- 英文 voiceover
- **不**自動加入 `code panel`
- **不**自動加入 `note panel`
- **不**自動加入 `summary panel`
- **不**自動加入畫面字幕

也就是說，v2 的預設是「主體動畫 + 旁白」。

## Optional features negotiation contract

以下功能都屬於 optional teaching overlays，不得在使用者未確認前自動啟用：

- `code panel`
- `note panel`
- `summary panel`
- on-screen subtitles

若需求中沒有明講是否需要上述功能，主 agent 必須在正式規劃前逐項詢問使用者。

詢問完成前的規則：

- 可以先鎖定演算法、輸入、交付層級、是否要旁白
- 不得先把 `code panel`、`set_note`、`show_summary_panel`、字幕列寫進 plan 或 trace
- 不得因為 example 或既有模板常用這些功能，就視為本次也要啟用

## 硬性 compliance contract

v2 引入了一套完整的 compliance 機制，這是整個 workflow 的合規骨架。

### 啟動前置條件

- 必須使用 subagent orchestration；若不能 delegation，禁止繼續
- 在至少一個實際 subagent 已成功啟動前，不得開始任何 phase
- 不可 silent fallback 成單 agent 流程

### 首個正式輸出：COMPLIANCE PLAN

第一個正式內容必須是 `COMPLIANCE PLAN`，必須先於 artifact 產出。  
它必須覆蓋 `PLAN`、`TRACE`、`SCRIPT`、`VOICEOVER`、`RENDER`、`QA`、`DELIVERY`，每個 phase 至少列出：

- phase 名稱
- 負責 subagent 角色
- 實際 `subagent id`（若尚未啟動，標記 blocked）
- 預期 artifact
- gate 條件

### 階段執行：PHASE RESULT

每個 phase 結束都必須回報 `PHASE RESULT`，至少包含：

- phase 名稱
- `PASS` 或 `FAIL`
- 負責 subagent 角色與實際 `subagent id`
- 證據檔案路徑
- gate 判定理由

任一 phase `FAIL` 時，不得進入下一階段。

### 結尾驗收：COMPLIANCE REPORT

最終必須輸出 `COMPLIANCE REPORT`，逐條對照 skill 規範與 phase gate，列出所有實際 `subagent id`。任一條未滿足時，必須標示未完成，不得宣稱 final delivery。

## Subagent orchestration

此 skill 強制使用主 agent orchestration 與實際 subagent，共 10 個角色：

1. `mode-planner` — 判斷 primary/secondary mode
2. `layout-checker` — 檢查 layout contract、collision risk
3. `trace-contract` — 鎖定 trace schema 是否足夠
4. `trace-writer` — 產出 `generated_trace_script.py` 與 `action_trace.json`
5. `script-writer` — 撰寫 `teaching_script.md`
6. `script-reviewer` — 審查 script gate
7. `voiceover-manifest` — 產出旁白稿與 timing contract
8. `scene-writer` — 產出或修正 `generated_algo_scene.py`
9. `scene-reviewer` — scene gate 唯一審查者
10. `qa-verifier` — 驗證 render 結果

各 subagent 規格放在 `agents/` 目錄，每個 agent 都有統一的 **Compliance return contract**，回傳時固定列出 `agent`、`phase`、`status`、`owned scope`、`artifacts`、`evidence or rationale`、`open blockers`。

### 主 agent 的責任

- 在任何 phase 前先確認 delegation 可用
- 第一個正式輸出先給 `COMPLIANCE PLAN`
- 啟動對應 subagent，只給最小必要 artifact
- 在每個 gate 後回收決策權
- 在每個 phase 後輸出 `PHASE RESULT`
- 最後輸出 `COMPLIANCE REPORT`

### Main agent decision points

主 agent 在以下節點回收決策權：

- `mode-planner` 後 → 鎖定 `primary mode` 與 `secondary mode`
- `layout-checker` 後 → 鎖定 layout contract
- `trace-contract` 後 → 鎖定 trace contract
- `trace-writer` 後 → 做 trace gate 判定
- `script-reviewer` 後 → 決定 script 是否通過
- `voiceover-manifest` 後 → 決定是否達 `voiceover preview` 前置條件
- 每一輪 `scene-reviewer` 後 → 決定 preview render 或重開 `scene-writer`
- `qa-verifier` 後 → 決定交付分類

### Render 專用規則

- `scene-reviewer` 是 scene gate 唯一審查者
- `scene-reviewer` 發現問題後，不回用原本的 `scene-writer`
- 每次 scene 修正都重新開一個新的 `scene-writer` instance
- 新的 `scene-writer` 只拿最新 `generated_algo_scene.py`、`scene_review.md`、必要正式 artifacts
- scene 層允許做顯式補償、adapter、defensive mapping、layout rebalance
- 主 agent 不把 scene semantic issue 再往回退到 `trace` 或 `script`

### Scene iteration contract

- 第一次 `scene-writer`：建 scene 初稿
- 第二次以後：視為 `repair writer`
- `repair writer` 必須讀前一版 scene code 與最新 `scene_review.md`
- `repair writer` 不得忽略 reviewer findings 重新自由發揮

## 輸入一個演算法後，agent 會怎麼做

假設你給 agent 的輸入是：演算法名稱、輸入資料、教學目標、觀眾、語言、是否需要旁白。  
agent 不會直接寫 `generated_algo_scene.py`。它會按以下流程執行。

## 第 0 步：辨識任務類型

agent 先判斷這個演算法屬於哪一種教學模式，由 `references/modes.md` 指導。6 種主要模式：

- `algorithm walkthrough` — 排序、完整流程
- `data structure state transition` — Heap、BST、Queue 等
- `pointer and control-flow explainer` — Binary Search、Two Pointers、Sliding Window
- `graph traversal explainer` — BFS、DFS
- `dynamic programming construction` — Knapsack、LCS、Edit Distance
- `comparison or intuition explainer` — 為什麼某做法有效

mode 會影響後面所有東西：`plan.md` 規劃、trace 記錄、beat 切法、畫面焦點。

## 第 1 步：PLAN

agent 先產生 `plan.md`，不先寫程式。規範在 `references/planning.md`。

預設 subagents：`mode-planner` + `layout-checker`

### PLAN 子流程

1. 主 agent 做 request normalization
2. 啟動 `mode-planner` → 鎖定 primary/secondary mode
3. 產出 `plan.md` 初稿
4. 啟動 `layout-checker` → 驗證 layout contract
5. 主 agent 整合結果並定稿 `plan.md`

### plan.md 要回答什麼

- 主要教學目標
- 主要 mode、audience
- 核心資料結構
- 關鍵 pointer / boundary / temp slot
- 關鍵 invariant
- 高層 beat 順序
- 固定版面區塊（預設只保留 main state area、pointer safe area、temp slot area、safe margin）
- 可能 collision 風險
- optional overlays 哪些已啟用、哪些關閉

### 預設 layout 原則

若使用者沒有明確要求額外教學輔助，layout 應先以最小可教學集合規劃。以下區塊只有在使用者明確同意後才納入：`code panel zone`、`note panel zone`、`summary panel zone`、`subtitle-safe area`。

### Plan gate

未滿足以下條件，不得進入下一階段：

- 已定義 `main state area`、pointer / label 安全區、與 `safe margin`
- 若啟用 optional overlays，已明確定義對應 zone
- 已指出 pointer 上下方用途
- 已指出 temp slot 或 hole 視覺化需求
- 已指出最容易發生的畫面衝突
- 已指出每個 beat 的主焦點應落在哪個區塊

## 第 2 步：TRACE

把演算法執行過程轉成 deterministic trace。規範在 `references/trace-schema.md` 和 `references/tracer-api.md`。

預設 subagents：`trace-contract` + `trace-writer`

### TRACE 子流程

1. 啟動 `trace-contract` → 鎖定必要 action families、欄位、禁止 scene 猜測的語義
2. 主 agent 鎖定 trace contract
3. 啟動 `trace-writer` → 產出 `generated_trace_script.py` 與 `action_trace.json`
4. 主 agent 做 trace gate 判定

### TRACE 吃什麼 input

- 演算法本身與範例輸入資料
- 使用者教學重點
- `plan.md` 中的 mode / invariant / pointer / temp slot / layout 語義

### TRACE 在做什麼

1. **決定要記錄哪些事件** — 根據演算法類型與教學目標選擇語義單位
2. **檢查 schema 夠不夠** — 對照 `references/trace-schema.md`，不夠就先擴 schema
3. **寫出 `generated_trace_script.py`** — trace 的生成器，以 deterministic 方式重現流程
4. **執行得到 `action_trace.json`** — 正式的演算法語義事件序列

trace 不是「畫面效果列表」，而是「演算法語義事件列表」。例如 insertion sort 不能只寫 `overwrite`，要用 `park_value`、`shift_cell`、`insert_from_slot` 等有語義的 action。

### Teaching-support actions 規則

`show_code_panel`、`highlight_code_lines`、`show_tracker`、`set_note`、`show_summary_panel` 等 action 可存在於 trace，但使用者未明確啟用對應 overlay 時，這些 action 不應出現。

### Trace gate

- 每個教學重點都能回對到 trace action
- sorting / shift / temp-value 類語義有明確 action contract
- pointer / boundary / region 類語義不靠 scene 推測
- 若演算法使用暫存值，trace 已表達 temp slot 與回填語義

## 第 3 步：SCRIPT

有了 trace 後，agent 才寫 `teaching_script.md`。規範在 `references/teaching-script.md`。

預設 subagents：`script-writer` + `script-reviewer`

### SCRIPT 子流程

1. 啟動 `script-writer`
2. 啟動 `script-reviewer`
3. 主 agent 決定 script 是否通過
4. 若 fail，重開新的 `script-writer`

### SCRIPT 在做什麼

1. **根據 trace 切 beat** — 照「一拍只講一個主焦點」切
2. **為每個 beat 指定主焦點與次焦點** — 一拍只能有一個主焦點
3. **為每個 beat 寫教學說明** — 包含 trace mapping、visual contract
4. **寫出 `teaching_script.md`**

若 optional overlay 未被使用者確認，不應混入 script 的 `Secondary support`。

### Script gate

- 每個 beat 只有一個主焦點
- 若同一 beat 需要多個新資訊區塊，已拆拍
- beat 的說明與 trace mapping 一致
- 教學重點沒有超出 trace 可支撐的內容

## 第 4 步：VOICEOVER

把 teaching script 轉成旁白結構。規範在 `references/voiceover.md`。

預設 subagent：`voiceover-manifest`

### VOICEOVER 子流程

1. 啟動 `voiceover-manifest`
2. 主 agent 決定是否已達 `voiceover preview` 前置 contract

### VOICEOVER 在做什麼

1. **把 teaching beat 濃縮成可朗讀旁白**
2. **寫出 `voiceover.md`** — 給人 review 的文字版
3. **寫出 `voiceover_segments.json`** — TTS 的單一結構化輸入
4. **產生或整理 `narration_manifest.json`** — 正式時間軸契約

若使用者明確要求字幕，才另外讀 `references/subtitles.md` 並產出 `subtitle_script.md`。字幕是 opt-in 功能，不是預設。

### TTS provider contract

Windows 預設使用 `Windows SAPI.SpVoice`，voice 為 `Microsoft Zira Desktop - English (United States)`。若找不到，必須停止並說明。

### Voiceover gate

- `voiceover_segments.json` 與 beat mapping 完整
- `narration_manifest.json` 包含 `duration_seconds`、`start_time_seconds`、`end_time_seconds`
- 若宣稱有聲版本，音訊檔實際存在且可播放

## 第 5 步：RENDER

到這一步才生成 `generated_algo_scene.py`。規範在 `references/manim-guidelines.md`、`references/visual-language.md`、`references/scene-review-checklist.md`。

預設 subagents：`scene-writer` + `scene-reviewer`

此階段固定拆成 3 個子步驟：`SCENE_BUILD` → `SCENE_REVIEW_AND_REPAIR` → `PREVIEW_RENDER`

### RENDER 子流程

1. 啟動第一次 `scene-writer`
2. 啟動 `scene-reviewer`
3. 若 fail，主 agent 開新的 `scene-writer` instance（repair writer）
4. 重複 `scene-writer` → `scene-reviewer`，直到 scene gate 通過
5. 通過後才做 preview render

### 5-1. 先生成 `generated_algo_scene.py`

把 `plan.md`、`action_trace.json`、`teaching_script.md`、`narration_manifest.json` 轉成 Manim scene：

- 把 layout contract 落成固定座標
- 讀取 trace 與 narration manifest
- 為每種必要 action 實作 handler
- 接上 beat timing helpers

Scene 不得重新計算演算法決策、不得猜測 `overwrite` 語義、不得偷偷建立未啟用的 optional overlay。

### 5-2. Scene review 與修正

`scene-reviewer` 讀 code 檢查所有 render 前可辨識問題，依 `references/scene-review-checklist.md` 八大類：

- A. Artifact and data entry
- B. Handler coverage
- C. Layout and formatting risks
- D. Pointer and state lifecycle
- E. Timing and audio contract
- F. Mutation semantics
- G. Runtime and animation bug risks
- H. Readability and maintainability

產出 `scene_review.md`，記錄問題、修正要求、原因、補償做法。

### 5-3. 修好後才做 preview render

preview render 檢查畫面結果、timing 結果、靜態 review 之後仍需靠影片確認的問題。

### Render gate

- `generated_algo_scene.py` 已生成
- `scene_review.md` 已記錄 scene review 與修正結果
- render 前靠讀 code 就能看出的主要問題都已處理
- scene 已可直接進 preview render

### Sorting renderer contract

- `swap` = whole-cell movement
- `shift_cell` = source cell 搬進 hole
- `park_value` = temp slot 必須可見
- `insert_from_slot` = 從 temp slot 回填，不從 tracker 飛回

## 第 6 步：QA

render 完不算完成，還要進 QA。規範在 `references/rendering.md` 和 `references/render-qa-checklist.md`。

預設 subagent：`qa-verifier`

### QA 子流程

1. preview render 或 final render 完成
2. 啟動 `qa-verifier`
3. 主 agent 根據 `review_notes.md` 做交付分類或要求 refinement

### QA 必查項（render-qa-checklist 六大類）

- **A. Layout** — collision 檢查
- **B. Focus** — 每個 beat 主焦點是否明確
- **C. Mutation semantics** — swap/shift/insert-back 語義正確性
- **D. Pointer clarity** — pointer label 可讀性
- **E. Audio and timing** — manifest timeline、beat audio、final MP4 audio stream
- **F. Review notes** — `review_notes.md` 已記錄問題與層級

### `scene_review.md` vs `review_notes.md`

- `scene_review.md` — 處理 render 前的 code、排版風險、動畫 bug 風險
- `review_notes.md` — 處理 render 後才看得到的成品問題

### QA gate

- layout 沒有關鍵遮擋
- mutation 視覺語義與演算法語義一致
- `review_notes.md` 已記錄問題、根因層級、修正策略與目前判定
- 若是 narrated delivery，final MP4 已驗證有 audio stream

## 第 7 步：DELIVERY

最後 agent 才能宣稱交付等級。由 `references/narrated-delivery-contract.md` 約束。

### 交付分類（只可使用以下三種）

- `silent preview` — 有可檢查畫面，沒有旁白音訊 contract
- `voiceover preview` — 有完整 voiceover artifacts，scene 可用 beat audio 預覽，但尚未完成正式 mux 驗證
- `final narrated delivery` — 有完整 narration track、已完成 final video 與 audio mux、已驗證 final MP4 有 audio stream

### DELIVERY 在做什麼

1. **判定交付等級** — 正式 classification
2. **列出目前可交付內容** — 所有已完成 artifact
3. **明確指出剩餘缺口與回修層級**
4. **輸出 COMPLIANCE REPORT** — 逐條對照 skill 規範

## 完整 workflow 的必要產出物

- `plan.md`
- `teaching_script.md`
- `voiceover.md`
- `voiceover_segments.json`
- `narration_manifest.json`
- `generated_trace_script.py`
- `action_trace.json`
- `generated_algo_scene.py`
- `scene_review.md`
- `review_notes.md`

若 TTS provider 可用：`audio/voiceover/*.wav`、`audio/narration_full.wav`

## 不應做的事

- 跳過 `plan.md` 直接寫 scene
- 讓 scene 自行重算或補完演算法邏輯
- 把 collision 當成小美術問題
- 用 swap 假裝 shift
- 用 tracker 文字冒充 temp slot
- 在沒有驗證 final MP4 audio 前宣稱 narrated delivery 完成
- 因 scene semantic issue 而回退整條 pipeline
- 讓同一個 `scene-writer` thread 反覆自修
- silent fallback 成單 agent 流程
- 未經使用者確認就啟用 code panel / note panel / summary panel / 字幕

## 按需載入順序

- `PLAN` → `references/planning.md`、`references/modes.md`、必要時 `references/visual-language.md`
- `TRACE` → `references/trace-schema.md`、`references/tracer-api.md`、必要時 `references/sorting-visual-patterns.md`
- `SCRIPT` → `references/teaching-script.md`
- `VOICEOVER` → `references/voiceover.md`、`references/narrated-delivery-contract.md`、要字幕時才讀 `references/subtitles.md`
- `RENDER` → `references/visual-language.md`、`references/manim-guidelines.md`、`references/scene-review-checklist.md`
- `QA` → `references/rendering.md`、`references/render-qa-checklist.md`

## 把整個流程更具象化

如果你輸入一個演算法，agent 實際上會做的是：

先決定「我要怎麼教這個演算法」  
再決定「哪些演算法事件必須被記錄」  
再決定「這些事件要切成哪些 beat」  
再決定「每個 beat 要講什麼、講多久」  
最後才把它畫成 Manim scene，並驗證成品是否真的符合旁白、版面與語義契約。

整個過程受 compliance 機制約束：先出 COMPLIANCE PLAN，每階段出 PHASE RESULT，最後出 COMPLIANCE REPORT。

## 你可以把這個 skill 想成三個轉譯器串在一起

1. 演算法描述 -> 教學設計
2. 教學設計 -> 結構化 trace / script / voiceover
3. 結構化 artifact -> 動畫與音訊成品

每一層轉譯都有 gate，都有 subagent 負責，都有 compliance 回報。
