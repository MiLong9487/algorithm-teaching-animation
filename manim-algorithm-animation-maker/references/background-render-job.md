# Managed Foreground Render Job

使用 `scripts/render_job.py` 在同步預檢通過後啟動受管理前景渲染。這裡的「前景」是相對於工具平台的執行 cell：`start` 命令會一直執行到 render 結束，但 agent 可在平台回傳仍在執行的 cell id 後結束回覆。不得自行使用 detached process、`Start-Process`、`nohup`、`start_new_session` 或反覆輪詢取代此 runner；受管理環境會在命令工作階段結束時回收這類脫離的子程序。

## Render plan

在動畫專案根目錄建立 `render_job_plan.json`：

```json
{
  "version": 1,
  "project_dir": ".",
  "code_path": "generated_algo_scene.py",
  "expected_code_sha256": "<64 hex>",
  "handoff_path": "scene_code_review_handoff.md",
  "review_path": "scene_review_result.md",
  "layout_audit_path": "layout_audit_result.md",
  "required_inputs": ["audio/voiceover/beat-001.wav"],
  "scene_outputs": [
    {"scene": "Scene1", "path": "rendered/scenes/Scene1.mp4"},
    {"scene": "Scene2", "path": "rendered/scenes/Scene2.mp4"},
    {"scene": "Scene3", "path": "rendered/scenes/Scene3.mp4"},
    {"scene": "Scene4", "path": "rendered/scenes/Scene4.mp4"},
    {"scene": "Scene5", "path": "rendered/scenes/Scene5.mp4"},
    {"scene": "Scene6", "path": "rendered/scenes/Scene6.mp4"}
  ],
  "combined_output": "rendered/final.mp4",
  "commands": [
    {
      "name": "render Scene1",
      "argv": ["{python}", "-m", "manim", "-qh", "generated_algo_scene.py", "Scene1", "--output_file", "rendered/scenes/Scene1.mp4"],
      "expected_outputs": ["rendered/scenes/Scene1.mp4"]
    }
  ],
  "env": {"MANIM_LAYOUT_AUDIT": "0"},
  "manifest_path": "render_manifest.md",
  "status_path": "render_status.json",
  "log_path": "render.log",
  "minimum_free_bytes": 1073741824,
  "allow_overwrite": false,
  "notify": true
}
```

實際 plan 必須包含六個 render commands 與一個合併 command，且每個必要輸出都列在對應 command 的 `expected_outputs`。命令使用 argv array，不能使用 shell string、pipe 或 redirect。Runner 只允許 Python、Manim 與 FFmpeg executable；`{python}` 會替換成 runner 使用的 Python。

將所有音訊、字型、資料檔及 concat list 等必要輸入完整列入 `required_inputs`。輸出已存在時預設拒絕啟動；只有使用者確實要求覆寫且已核對目標後，才設定 `allow_overwrite: true`。

## Preflight and launch

先執行同步 preflight：

```bash
python path/to/skill/scripts/render_job.py preflight render_job_plan.json
```

Preflight 必須為 `PASS`。它會檢查 code/review/QA hash、正式 PASS、Python 語法、六幕與合併輸出覆蓋、必要輸入、允許的 executables、可寫目錄、磁碟空間、舊 job 與桌面通知環境。

Windows 通知只使用 `render_job.py` 內建的 Python／PowerShell WinRT 路徑，不需要 .NET、NuGet、Windows App SDK 或額外 helper。Runner 會用 `Get-StartApps` 解析已註冊的 PowerShell／Terminal App ID，再由非互動式 PowerShell 提交 Toast；不得以任意未註冊名稱取代 App ID。

Windows 上的同步 `preflight` 與後續 `start` 必須使用相同的工具權限：都在受管理 sandbox 外、目前已登入使用者的非 elevated desktop session 執行。對兩個命令提出範圍明確的 sandbox／GUI 權限請求；這不是要求以系統管理員身分執行。

Preflight 會在 Python 中記錄 mechanism、identity、Session ID、elevated 與 App ID。`start` 的二次 preflight 與 worker 的三次 preflight 必須得到相同 fingerprint；App ID 解析失敗、elevated 或 fingerprint 改變都要在 render 前阻止 job。

Preflight 通過後，在工具平台可持續維護、且 timeout 長於預期 render 時間的執行 cell 中執行：

```bash
python -u path/to/skill/scripts/render_job.py start render_job_plan.json
```

Windows 上必須以和同步 preflight 相同的 sandbox 外、非 elevated desktop session 啟動 `start`。`start` 會再次執行相同預檢，接著在同一個前景程序中執行全部 commands；不得替它增加任何 detached flags。工具平台回傳仍在執行的 cell id 後：

1. 不得對該 cell 呼叫 wait，也不得持續讀取它的輸出。
2. 另用短命令執行 `status render_status.json`，確認狀態是 `RUNNING`；如果 render 很快完成，`PASS` 也可接受。若 cell 剛建立而狀態檔尚不存在，只能在 15 秒的啟動確認期限內短暫重試；檔案一旦出現就停止，進入 `RUNNING` 後絕不再輪詢。
3. 回報 job id、cell id、狀態檔與 log 路徑後立即結束 agent 工作。

長時限是避免工具平台因 command timeout 主動終止 worker；它不表示 agent 必須保持回覆或消耗 token 等待。若平台沒有回傳可持續維護的執行 cell，則不得啟動 render，應回報目前環境不支援此工作模式。

Worker 依序執行 commands，在每個 command 前重新驗證 code hash，並在執行期間自行更新 heartbeat；agent 不需輪詢。最後驗證六個 MP4 與合併 MP4 非空、自動建立 `render_manifest.md`，並原子更新 `render_status.json`。結束時由 Python runner 透過 PowerShell WinRT 桌面通知回報 `PASS` 或 `FAIL`；通知提交時的 context 必須與 render 前 fingerprint 相同。狀態檔以 `notification.submitted` 記錄是否成功提交，因為 Windows 不提供使用者實際看見通知的回執。通知失敗只記錄結構化 error，不改寫已完成的 render 結果。

## Next conversation

下次進入此 skill 且專案根目錄存在 `render_status.json` 時，先執行：

```bash
python path/to/skill/scripts/render_job.py status render_status.json
```

- `PASS`：向使用者回報合併影片、manifest 與通知結果，再執行 `ack`。
- `FAIL`：回報 error 與 log 路徑，不自動修改程式碼，再執行 `ack`。
- `INTERRUPTED`：表示前一次受管理前景程序已不存在；回報 error 與 log 路徑，再執行 `ack`。不得把它誤報成仍在渲染。
- `STARTING` 或 `RUNNING`：只回報仍在執行，不輪詢，也不 ack。
- 已有 `acknowledged_at`：不重複主動回報。

```bash
python path/to/skill/scripts/render_job.py ack render_status.json
```
