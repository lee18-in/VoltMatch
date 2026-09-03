# LLM_MEMORY.md — 工作記憶(agent 讀寫;規則見 AGENTS.md,勿在此重複)

> 📌 **本專案有三份記憶檔,每個 session 開始時都要讀**(見 `AGENTS.md` §0〈三份檔案的分工〉):
>
> | 檔案 | 存什麼 |
> |---|---|
> | `AGENTS.md` | 規則(不變) |
> | **本檔 `LLM_MEMORY.md`** | **會衰減的**:目前狀態、下一步、交接事件流水帳 |
> | [`COMPONENT_MAP.md`](./COMPONENT_MAP.md) | **不衰減的**:專案結構與跨模組契約、決策理由、環境條件、驗證台帳。開頭有〈六十秒進入狀況〉,先讀它最快上手 |
>
> ⚠️ **寫日誌時就分流**:本檔只記「做了什麼」;「為什麼這樣決定／試過什麼不行／驗證了什麼」當場寫進 `COMPONENT_MAP.md`。本檔日誌會被封存,那些事實卻不會過期——寫錯地方等於預約遺失。單筆日誌上限約 1200 bytes。

## A. 目前狀態(每次交接必更新)

- 目前階段: build
- 最後更新: 2026-09-03 18:12 / 當時階段: build
- 交接基準 commit: 0e0176e [maintain] 移除版控執行檔
- 遠端狀態: 已依使用者指示 push 至 origin/main,工作樹乾淨、無未推送 commit(不記雜湊:記憶檔一寫進去雜湊就變,見 AGENTS.md §2 的自我指涉條款)
- 進行中任務: 不同作業系統的uiux相容 畫面顯示 字形排版調整 for 不同作業系統(已完成 Circuit 電路圖區塊)
- 阻塞點: 三筆待審閱堆疊中,皆需新 session/新工具承接(§2.1 禁止左手審右手):(1) 2026-09-03 18:04 AGENTS.md 升級 Playbook v10;(2) 2026-07-26 22:25 tag 發版 workflow;(3) 2026-07-29 17:33 .venv2 取消版控

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
### 2026-09-03 18:04 [build] 使用工具: Claude Opus 5 (Claude Code)

- 完成了什麼: (1) 依使用者授權升級 `AGENTS.md` Playbook v9→v10:新增〈三份檔案的分工〉與〈寫入時分流〉、交接日誌單筆 1200 bytes 上限、防膨脹門檻由「20 筆」改為「10 KB」、技術脈絡改掛 `COMPONENT_MAP.md`。(2) `COMPONENT_MAP.md` 重構為不衰減層知識庫(8 節,新增決策紀錄/環境知識/驗證台帳)。(3) 依新門檻封存 10 筆舊日誌至 `ARCHIVE.md`,並把本 session 自己先前兩筆逾長條目(共 8.3 KB)壓縮成本筆。設計理由與實測數據見 `COMPONENT_MAP.md` §6 決策 #8~#12。
- 下一個 agent 該做什麼: 本次改動需要審閱(異動憲法層 `AGENTS.md`):(1) v10 新條文與既有條文是否衝突;(2) 1200 bytes 上限實務上是否可行;(3) 封存後〈阻塞點〉指向的兩筆待審閱是否完整保留。之後續行 B2: Windows 實機驗證 UI(缺口見 `COMPONENT_MAP.md` §8)。
- 地雷警告: `AGENTS.md` 是跨專案共用 Playbook 副本,本次使此副本領先母本至 v10;新條文已刻意寫成專案無關以便回移植。

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

## D. 已封存結論(自〈總結封存〉搬入,唯讀)

原文保留於 [`ARCHIVE.md`](./ARCHIVE.md)；不衰減知識已萃取至 [`COMPONENT_MAP.md`](./COMPONENT_MAP.md)。

- **2026-09-03 11:26 [build]** 建立 `COMPONENT_MAP.md` 初版（介面對照表形式）。同日即被重構為不衰減層知識庫，內容全數取代。
- **2026-08-27 18:28 [build]** 依使用者指示刪除版控中的 `bin/VoltMatch.exe`（24 MB）。
- **2026-08-25 16:04 [maintain]** `AGENTS.md` 由 Playbook v2 升級至 v9，同步升級 `scripts/hooks/` 兩支腳本，〈最新 commit〉欄改名〈交接基準 commit〉。舊版 v2 存於 commit `4462419`。
- **2026-08-24 [build]** 提交並推送 `環境部屬.md` 部署文件修改（補 Linux 安裝指令）。
- **2026-07-26 21:55 [build]** 修正 `CircuitCanvas` 在 Linux 下標籤被裁切：改為字型度量動態排版、新增 `_fit_to_content()`、加 `MIN_WINDOW_SIZE`、Circuit 區塊改 `anchor="n"` 並填滿列高。設計理由與驗證結果已萃取至 `COMPONENT_MAP.md` §6／§7／§8。
- **2026-07-06 18:10 [maintain]** 提交 Git Hook 腳本權限修復（chmod +x）。
- **2026-07-06 18:05 [maintain]** Playbook v1→v2 升級；新增 `LLM_MEMORY.md`〈E. 專案技術脈絡〉（該節已於 v10 移至 `COMPONENT_MAP.md`）。
- **2026-07-06 18:00 [maintain]** Git Hook 驗證：`pre-commit` / `commit-msg` 攔截功能實測通過（已入 `COMPONENT_MAP.md` §8 台帳）。
- **2026-07-06 16:50 [plan]** Playbook v1 導入：建立 `AGENTS.md` 與 `scripts/hooks/`，啟用 `core.hooksPath`。
- **2026-07-05 21:24 [build]** 導入 AI agent 工作流，建立 `AGENTS.md`／`LLM_MEMORY.md`／`CLAUDE.md`／`GEMINI.md`。

## E. 專案技術脈絡(依專案填寫,agent 得隨專案實況更新,保持精簡)

自 Playbook v10 起，建置／測試指令與程式碼慣例改記於 [`COMPONENT_MAP.md`](./COMPONENT_MAP.md) §1（不衰減層）——這類資訊不會過期作廢，不該放在會被封存的本檔。
