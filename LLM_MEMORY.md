# LLM_MEMORY.md — 工作記憶(agent 讀寫;規則見 AGENTS.md,勿在此重複)

> 📌 **先讀 [`COMPONENT_MAP.md`](./COMPONENT_MAP.md)**：記錄專案內各物件的輸入/輸出/上下游關聯與驗證狀態(本檔記「現在做到哪」,COMPONENT_MAP.md 記「程式碼介面長怎樣」)。異動到 `calculation_worker.py`/`utils.py`/`ui_components.py`/`config.py` 的函式簽章或呼叫關係時,務必回頭同步更新該檔對應區塊,否則該檔會產生誤導(該檔尚無 hook 強制連動,全靠自律)。

## A. 目前狀態(每次交接必更新)

- 目前階段: build
- 最後更新: 2026-09-03 11:26 / 當時階段: build
- 交接基準 commit: 0e0176e [maintain] 移除版控執行檔
- 進行中任務: 不同作業系統的uiux相容 畫面顯示 字形排版調整 for 不同作業系統(已完成 Circuit 電路圖區塊)
- 阻塞點: 兩筆待審閱堆疊中,皆需新 session/新工具承接(§2.1 禁止左手審右手):(1) 2026-07-26 22:25 tag 發版 workflow;(2) 2026-07-29 17:33 .venv2 取消版控

## B. 規劃(規劃階段 [plan] 專屬區;狀態: 草稿 | 已定案)

### B1. 架構決策(已定案後鎖定,建置/維運階段不得改)

| # | 決策 | 理由 | 狀態 |
|---|------|------|------|

### B2. 短期目標(本週)

- [ ] 跨作業系統 UI/UX 相容性優化：針對不同作業系統（Windows / Linux 等）進行畫面顯示與字體排版調整，確保視覺體驗一致。

### B3. 中期目標(本月)

- [ ] 核心計算邏輯 API 化：重構計算模組，定義標準化的輸入變數與輸出格式介面，將運算邏輯與 UI 介面解耦。

### B4. 長期目標

- [ ]

## C. 交接日誌(只追加,不刪改;最新在最上,每筆一個小節)

### 2026-09-03 11:26 [build] 使用工具: Claude Sonnet 5 (Claude Code)

- 完成了什麼: 依使用者指示,建立 `COMPONENT_MAP.md` 草稿並在 `LLM_MEMORY.md` 開頭加入指向它的提示。`COMPONENT_MAP.md` 內容係實際讀取 `main.py`、`ui_components.py`、`calculation_worker.py`、`utils.py`、`config.py` 全文後整理:§0 模組關聯圖(資料流,含 main.py↔calculation_worker.py 的 dict-in/queue-out 隱性介面說明)、§1 核心資料流物件表(worker_calculation、run_calculation_trigger、check_queue、preprocess_display_data、utils.py 六個純函式,逐一列輸入/輸出/關聯/驗證狀態)、§2 UI 元件表(FilterWindow、CompactSolverFrame、CircuitCanvas、NotesFrame、configure_system_settings)、§3 main.py 次要 UI glue 方法分類清單(未逐一展開)、§4 config.py 說明、§5 已知落差與後續建議(含測試優先順序建議、與 §B3 中期目標的關聯)。驗證狀態欄位皆據實填寫:專案無 `tests/` 目錄、`requirements.txt` 未列測試框架,故多數物件標記 ❌ 未驗證;`CircuitCanvas`/`configure_system_settings` 依 2026-07-26 22:25 交接日誌的 xvfb-run 手動驗證紀錄標記為 ⚠️ 部分驗證(僅 Linux,且該筆日誌本身仍在待審閱堆疊中)。同時依 §2 規則,把〈目前狀態〉的「交接基準 commit」由舊值 `7219204` 覆蓋為當下 HEAD `0e0176e`(覆蓋前已確認上一筆 2026-08-27 18:28 日誌未標「需要審閱」,依規則順序可直接覆蓋)。未觸碰 `AGENTS.md`。尚未 commit,等待使用者確認後再進行。
- 下一個 agent 該做什麼: 本次改動需要審閱:(1) `COMPONENT_MAP.md` 各表格列出的輸入/輸出/關聯是否與實際程式碼一致(逐列核對 file:line 連結指向的內容);(2) 驗證狀態欄位的 ✅/⚠️/❌ 判定是否有遺漏其他交接日誌中記載過的驗證紀錄;(3) `LLM_MEMORY.md` 開頭新增的指向提示是否會與 §0「先讀 LLM_MEMORY.md」的既有規則衝突或造成閱讀順序混淆。若使用者本次口頭豁免審閱,依 §2.1 在本欄位補記「使用者於<時間>明示豁免本次審閱」即可略過上述三點直接繼續。
- 地雷警告: `COMPONENT_MAP.md` 目前沒有 git hook 強制與程式碼同步(不像 `LLM_MEMORY.md` 有 pre-commit 強制檢查),往後改 `calculation_worker.py`/`utils.py`/`ui_components.py`/`config.py` 的函式簽章或呼叫關係時,若忘記回頭同步,該檔會產生誤導後續 agent 判斷的錯誤資訊。

### 2026-08-27 18:28 [build] 使用工具: GitHub Copilot

- 完成了什麼: 依使用者明確指示刪除版控中的 `bin/VoltMatch.exe`，準備同步移除 GitHub 上的 24 MB 執行檔。
- 下一個 agent 該做什麼: 無。
- 地雷警告: 移除執行檔後，使用者需透過 GitHub Actions 或其他建置流程取得發行版本。


### 2026-08-25 16:04 [maintain] 使用工具: Claude Code

- 完成了什麼: 依使用者指示，將 `AGENTS.md` 整份覆蓋升級至 Playbook v9（原版本 v2）。改動摘要：新增「交接基準 commit」欄位與其填寫規則、覆蓋前後順序規定（§2）；新增 §2.1 Review Loop 審閱提示機制；新增 §4「作用範圍僅限本檔所在目錄」巢狀邊界規則；新增語言與編碼規範明文（UTF-8／繁體中文）；新增 `Playbook-Variant: online` 標記。舊版 AGENTS.md（v2，commit `4462419`）已存於 git 歷史，可用 `git show 4462419:AGENTS.md` 找回，不再另外存檔。同時將 `scripts/hooks/pre-commit`／`commit-msg` 整份覆蓋至 v9 版本（中文檔名相容、管轄錨點收斂避免死鎖、大量檔案效能優化、commit-msg 白名單合併/還原訊息等修正），並確認 `.gitattributes` 已含 `scripts/hooks/* text eol=lf`。同步將〈A. 目前狀態〉的「最新 commit」欄改名為「交接基準 commit」（Playbook v3 起的欄位語意變更：只在接手時填一次、工作期間不再更動，不再是「做到哪」），並填入當下 HEAD。
- 下一個 agent 該做什麼: 本次改動需要審閱：確認 v9 新規則（尤其 §2.1 Review Loop 與 §4 巢狀邊界）是否符合本專案實際工作模式，並確認 hook 版本升級後 commit 仍正常通過。
- 地雷警告: 無

### 2026-08-24 [build] 使用工具: GitHub Copilot

- 完成了什麼: 已提交並推送使用者在 `環境部屬.md` 的部署文件修改：補充 Linux 快速安裝指令、移除多餘編號與整理 Windows 區段空白。此變更未修改程式碼。
- 驗證紀錄: `git diff --check` 通過；提交 `9cfdbcc` 已推送至 `origin/main`。
- 下一個 agent 該做什麼: 無。
- 地雷警告: 無。

### 2026-07-29 17:33 [build] 使用工具: Claude Opus 5 (Claude Code)

- 完成了什麼: 把 `.venv2/` 移出版控。使用者刻意刪掉了本機的 `.venv2/` 虛擬環境目錄,但該目錄底下有 2225 個檔案(blob 合計 10.7 MB)當初被 commit 進 repo,導致 `git status` 整片顯示 deleted。改動:(1) `.gitignore` 第 29 行、原 `.venv/` 之後新增 `.venv*/`,一併涵蓋 `.venv2/`、`.venv-1/` 這類 VSCode Python Envs 擴充建立失敗時留下的變體目錄(原本只擋 `.venv/`);(2) `git rm -r --cached .venv2` 將 2225 個檔案自索引移除(檔案本來就已不在工作樹,此步只記錄刪除,不動任何現存檔案)。本次未觸碰任何程式碼、未 push。
- 起因(環境問題,非專案問題): 使用者反映 VSCode 無法快速建立虛擬環境。診斷結果:(a) log 中大量 `ensurepip is not available` 是機器當時缺 `python3.12-venv`,現已安裝(3.12.3-1ubuntu0.15),建 venv 已正常;(b) `/usr/bin/python3: No module named pip` 是 Ubuntu 拆包 + PEP 668 的預期行為,非故障;(c) 「慢」的真因是機器沒裝 uv,Python Envs 擴充每次先探測 `uv --version` 失敗才退回 `python -m venv` + pip。已為使用者安裝 uv 0.12.0 至 `~/.local/bin`(純本機環境變更,不影響 repo)。
- 驗證紀錄: `git check-ignore -v` 確認 `.venv2/` 與 `.venv/` 皆命中 `.gitignore:29:.venv*/`;暫存區內容核對為 2225 筆 D(全屬 `.venv2/`)+ 1 筆 M(`.gitignore`),無其他檔案被誤納;工作樹除 `.venv2/` 刪除外無其他變更。uv 安裝後 `uv --version` 與登入 shell `command -v uv` 均正常回應。
- 下一個 agent 該做什麼: 本次改動需要審閱:(1) `.gitignore` 的 `.venv*/` 這個 glob 是否過寬,會不會誤擋到未來想納管的檔名(例如 `.venvrc`、`.venv.example` 之類——注意結尾斜線只匹配目錄,但仍請確認專案沒有以 `.venv` 開頭的目錄需要版控);(2) 確認 `git rm --cached` 只影響索引,遠端與其他開發者 pull 後會刪掉他們本機的 `.venv2/` 目錄(若有人正在用該環境會被移除,需評估是否要事先告知);(3) 這 10.7 MB 仍留在 git 歷史中,只有未來 commit 不再帶它,如需真正瘦身要 rewrite history(屬架構級決定,須使用者裁示)。另請注意:2026-07-26 22:25 那筆的審閱**尚未完成**,本次未代審(不同主題且§2.1 不允許),請一併處理。
- 地雷警告: 遠端 `bin/VoltMatch.exe`(24MB 二進位)仍在版控中,會持續膨脹 repo;若要清掉需使用者裁示(屬架構級決定)。

### 2026-07-26 22:25 [build] 使用工具: Claude Opus 5 (Claude Code)

- 完成了什麼: 建立 tag 發版流程。原本 `.github/workflows/package.yml` 只在 push main / PR 時觸發,且僅上傳 workflow artifact,推 tag 不會有任何反應、也不會產生 Release。改動:(1) 觸發條件新增 `tags: ["v*"]`;(2) 新增 `release` job(`needs` 兩個 build job、`if: startsWith(github.ref, 'refs/tags/v')`、`permissions: contents: write`),用 `actions/download-artifact@v4` 收兩個 artifact 後,以 runner 內建的 `gh release create --generate-notes` 發佈 Release 並附上 `VoltMatch.exe` 與 `VoltMatch-x86_64.AppImage`(刻意不用第三方 action,降低供應鏈風險);(3) README 的 Artifacts 段落改寫為〈⬇️ Download〉,主推 Releases 頁面連結 <https://github.com/lee18-in/VoltMatch/releases/latest>,並保留 Actions artifact 作為開發版下載說明,同時修掉該段既有的兩個亂碼字元;(4) `config.py` H_TITLE 版號 26.0526.1 → 26.0726.1(使用者指定與 tag 同步)。另外接手時本地落後遠端 3 筆(遠端為 bin/*.exe 的增刪,與本地檔案無重疊),已 `git rebase origin/main` 線性整併。
- 驗證紀錄: 以 PyYAML 解析 workflow 確認語法有效,觸發條件為 `{'push': {'branches': ['main'], 'tags': ['v*']}, 'pull_request': ...}`,job 清單為 build-windows / build-linux-appimage / release,release 的 needs、if、permissions 均如預期。artifact 路徑對應已核對(upload 的 `dist/VoltMatch.exe` 與 `VoltMatch-x86_64.AppImage` 下載後分別落在 `artifacts/voltmatch-windows-exe/` 與 `artifacts/voltmatch-linux-appimage/`)。實際 Actions 執行結果見下一筆或 GitHub Actions 頁面。
- 下一個 agent 該做什麼: 本次改動需要審閱:(1) `release` job 的 artifact 下載路徑與 `gh release create` 的檔案參數是否與兩個 build job 的 upload 設定完全對應;(2) `permissions: contents: write` 是否足夠(repo 設定若限制 GITHUB_TOKEN 權限會導致發佈失敗);(3) 同時推 main 與 tag 會觸發兩次 workflow run,是否需要加 concurrency 控制避免重複建置。
- 追加(22:35): 使用者手動把 README 的〈⬇️ Download〉整段從〈Packaging Notes〉之後上移到〈About VoltMatch〉之後,內容未變(純段落順序調整),依現況提交並推送 main。
- 地雷警告: 遠端 `bin/VoltMatch.exe`(24MB 二進位)仍在版控中,會持續膨脹 repo;若要清掉需使用者裁示(屬架構級決定)。

### 2026-07-26 21:55 [build] 使用工具: Claude Opus 5 (Claude Code)

- 完成了什麼: 修正 Circuit 電路圖在 Linux 下標籤被裁切的排版問題(B2 跨 OS UI 相容)。`ui_components.CircuitCanvas` 原本用寫死像素(畫布 80x210、主幹 cx=30、字級 9/10)排版,Windows 以外的系統字型較寬,V_Target / R_Hi1 / V_Ref / R_Low 標籤超出畫布被切掉。改為:(1) 以 `tkfont.Font` 實際度量(measure / linespace)推算主幹 x 座標、電阻高度與節點間距,字級改為隨 `config.FONTSIZE` 連動(-2 / -3,預設 12 時等同原本的 10 / 9);(2) 電阻標籤由「偏下 +10px」改為垂直置中,V_Ref 文字下移避免壓到分接導線;(3) 新增 `_fit_to_content()`,繪製後依 `bbox("all")` 自動調整畫布尺寸,並以雙電阻模式高度為下限保留,單/雙電阻切換時尺寸固定不跳動;(4) `main.py:250` 移除寫死的 `width=80, height=210`,尺寸交給 draw_circuit 決定。
- 追加(21:58): 補上主視窗最小尺寸限制。`config.py` 新增 `MIN_WINDOW_SIZE = (900, 680)`(緊鄰 `WINDOWS_SIZE`),`main.py:42` 在 `geometry()` 後呼叫 `self.root.minsize(*config.MIN_WINDOW_SIZE)`。下限值來源:實測左欄控制項自然高度 648px,低於此值 About 按鈕會被裁掉;寬度 900 時 Notes 區仍有約 304px 可用。此數值由使用者後續自行微調(使用者已改為 1800x1000,因其環境 tk scaling≈2.0,左欄自然高度實際約 792px)。
- 追加(22:10): 底部 Circuit 區塊改為向上對齊。`main.py:250` 的 `circuit_frame.pack()` 補上 `anchor="n"`;原本 pack(side=LEFT) 未指定 anchor 會在該列垂直置中,Circuit 框比 Notes 矮,標題就比 Quick Solver / Notes 低一截(96dpi 下偏移 6px,144dpi/scaling 2.0 下偏移 21px,DPI 越高越明顯)。實測 anchor="n" 後三個區塊上緣 offset 皆為 0。
- 追加(22:15): Circuit 繪圖區改為填滿該列高度。`main.py:249-251` 的框架加 `fill="y"`、畫布改 `pack(fill=BOTH, expand=True)`;`CircuitCanvas` 拆出 `_render()` 並綁定 `<Configure>`,當實際高度大於自然高度時,把多出來的空間依比例分配給電阻高度與 V_Ref 節點間距(文字與接地符號不縮放),單/雙電阻模式都會填滿。防迴圈設計:`_fit_to_content()` 回報的請求高度一律用「雙電阻模式的自然高度」(`request_h`),不回報拉伸後高度,否則外層會被越撐越大;`_on_resize` 另以 `_last_size` 比對過濾重複事件。實測啟動後只重繪 2 次、閒置與視窗縮放皆 0 次(無無限迴圈),兩種模式底部剩餘 7~9px(即預留的接地留白),無溢出。
- 追加(22:20): 使用者手動微調 `config.py`:`FONTSIZE` 12→10、`WINDOWS_SIZE`/`MIN_WINDOW_SIZE` 1800x1000→1680x1000,一併提交。
- 驗證紀錄: 以 xvfb-run 實際啟動 `main.py`(RVDSApp)確認可正常開啟並重繪;單/雙電阻模式互切後畫布皆為 88x200 且 bbox 完全落在畫布內;另以 WenQuanYi 12 / Noto Sans CJK TC 16 / Helvetica 9 / DejaVu Sans 20 四組字型字級驗證 fits=True 全數通過;並將 canvas 輸出 PostScript 轉圖目視確認無裁切、無重疊。
- 下一個 agent 該做什麼: 本次改動需要審閱:(1) `ui_components.py` CircuitCanvas 幾何計算是否正確(cx 左側預留是否涵蓋 V_Target 半寬、TERM_HALF/GND_HALF/ZIGZAG);(2) `_fit_to_content` 的 min_height 保留值(+18+line_width*2+PAD)是否會在其他字型下造成畫布過高或不足;(3) `main.py:250` 移除固定寬高後,底部 Circuit/Solver/Notes 三欄版面在 Windows 實機上是否仍正常(本次僅在 Linux + Xvfb 驗證,未在 Windows/macOS 實機驗證);(4) `MIN_WINDOW_SIZE` 是依實測得出的寫死值(使用者已調為 1800x1000),在 Windows/macOS 字型較寬時是否仍足夠;(5) `CircuitCanvas._on_resize` / `_fit_to_content` 的防迴圈邏輯是否在其他視窗管理員或 DPI 下仍收斂(請確認請求高度沒有回報拉伸後的值)。
- 地雷警告: 無

### 2026-07-06 18:10 [maintain] 使用工具: Claude Haiku 4.5

- 完成了什麼: 提交 Git Hook 腳本權限修復（chmod +x），確保 pre-commit 與 commit-msg 脚本在 push 時可正確执行。
- 下一個 agent 該做什麼: 無（權限修復完成，可進行 push）。
- 地雷警告: 無

### 2026-07-06 18:05 [maintain] 使用工具: Claude Haiku 4.5

- 完成了什麼: Playbook v1→v2 升級完成。AGENTS.md 整份覆蓋至新版模板（Playbook-Version: 2），§5 改為純文字指向 LLM_MEMORY.md〈E. 專案技術脈絡〉；新增 LLM_MEMORY.md〈E. 專案技術脈絡〉區塊，搬入 v1 §5 既填值（建置指令、測試指令、程式碼慣例）。
- 下一個 agent 該做什麼: 無（升級完成，可恢復原定 build 階段任務）。
- 地雷警告: 無

### 2026-07-06 18:00 [maintain] 使用工具: Claude Haiku 4.5

- 完成了什麼: Git Hook 驗證完成。發現 pre-commit 與 commit-msg 腳本權限未設置為可執行，執行 `chmod +x` 修復；測試結果：pre-commit 成功攔截缺少 LLM_MEMORY.md 變更的 commit、commit-msg 成功攔截不符合 [plan]/[build]/[maintain]/[takeover] 格式的 commit 訊息。
- 下一個 agent 該做什麼: 無（Hook 驗證完成，可恢復 build 階段任務；稍後執行 Playbook v1→v2 升級）。
- 地雷警告: 無

### 2026-07-06 16:50 [plan] 使用工具: Claude Haiku 4.5

- 完成了什麼: 完成 Playbook v1 防禦導入：AGENTS.md 整份覆蓋至新版模板（保留 Playbook-Version: 1 標記與 §5 技術脈絡值），CLAUDE.md/GEMINI.md 格式確認無誤，README.md 已有頂端註解；建立 `scripts/hooks/pre-commit` 與 `scripts/hooks/commit-msg`，並執行 `git config core.hooksPath scripts/hooks` 啟用。
- 下一個 agent 該做什麼: 本次改動需要審閱：驗證 Git Hook 在下次 commit 時能正常攔截非標格訊息與未更新 LLM_MEMORY.md 的情況。驗證後可繼續推進原定 build 階段任務。
- 地雷警告: 無

### 2026-07-05 21:24 [build] 使用工具: Antigravity

- 完成了什麼: 導入 AI agent 工作流，建立 AGENTS.md, LLM_MEMORY.md, CLAUDE.md, GEMINI.md，並修改 README.md 頂部。
- 下一個 agent 該做什麼: 繼續處理不同作業系統的 uiux 相容性、畫面顯示、字形排版調整任務。
- 地雷警告: 無

## D. 已封存結論(自〈總結封存〉搬入,唯讀)

## E. 專案技術脈絡(依專案填寫,agent 得隨專案實況更新,保持精簡)

- 建置指令: `pyinstaller VoltMatch.spec` (若需編譯執行檔)
- 測試指令: `python main.py`
- 程式碼慣例: Python 3.x, 使用 Tkinter (UI), NumPy 等
