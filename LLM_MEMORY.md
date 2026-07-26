# LLM_MEMORY.md — 工作記憶(agent 讀寫;規則見 AGENTS.md,勿在此重複)

## A. 目前狀態(每次交接必更新)

- 目前階段: plan(2026-07-26 23:30 由使用者宣告,自 build 切入)
- 最後更新: 2026-07-26 23:30 / 當時階段: plan
- 最新 commit: 見 git log(已發版 tag: v26.0726.1;目前工作分支 `refactor/divider-math-core`,已推遠端同名分支,未合併 main)
- 進行中任務: 規劃「運算與 UI 解耦」的後續路線,已將解耦審查的三項待辦寫入 B1/B2/B3。
- 阻塞點: B 區新增內容目前全部標記〈草稿〉,**未定案前 build 階段不得依此改動程式碼**(AGENTS.md §1);需使用者逐項確認是否定案。

## B. 規劃(規劃階段 [plan] 專屬區;狀態: 草稿 | 已定案)

> 本區 2026-07-26 23:30 新增的 D1~D3 與 B2/B3 條目狀態一律為〈草稿〉,依 AGENTS.md §1,未標記〈已定案〉前禁止依此改動程式碼。

### B1. 架構決策(已定案後鎖定,建置/維運階段不得改)

| # | 決策 | 理由 | 狀態 |
|---|------|------|------|
| D1 | 領域知識單一來源:分壓公式、E 系列標準值判定等領域規則,全庫只能有一份實作,UI 層一律呼叫共用模組,不得自行寫第二份 | 已實際出事兩次:分壓公式曾同時存在於 `calculation_worker` 與 Quick Solver(已修);E 系列判定至今仍有兩份且結果不一致,造成單電阻模式 E24_Count 錯誤 | 草稿 |
| D2 | 分層為 core / app / ui 三層:core 零 UI 依賴、零執行緒依賴(進度以 callback 或 generator 回報);app 負責輸入驗證、契約定義與結果格式化;ui 只處理 tkinter、顏色與版面 | 為 B3 的 API 化與日後 Web 前端鋪路;現況 core 邊界已可精確畫出(`divider_math` + `get_resistor_list` + 7 個領域常數),拆分屬機械工 | 草稿 |
| D3 | core 層模組維持最小依賴,`divider_math.py` 維持零 import(不得 import config/numpy/UI) | 確保運算核心可原封不動移植到其他前端(Web/API/CLI) | 草稿 |

### B2. 短期目標(本週)

- [ ] 跨作業系統 UI/UX 相容性優化：針對不同作業系統（Windows / Linux 等）進行畫面顯示與字體排版調整，確保視覺體驗一致。
  - 進度：Circuit 電路圖區塊已改為依字型度量排版並填滿版面（已完成）；`MIN_WINDOW_SIZE` 已導入。**尚未在 Windows / macOS 實機驗證**。
- [ ] 【草稿・Bug】修正 E24_Count 判定不一致：`calculation_worker.py:128-131` 用 `np.isin(值, e24_full_list)`、`utils.py:51` `determine_r_color()` 用有效數字比對，兩法對 `0` 的判定相反（根因：`config.E24_BASE` / `E96_BASE` 最後一個元素為 `0`，使 `0` 進了電阻表）。後果：單電阻（Disable）模式下 `r_hi2_rng = [0.0]`，每列 `E24_Count` 比畫面綠色格子多 1。
  - 驗收條件：抽出「回傳 E 系列分類、不回傳顏色」的共用函式供兩邊使用，顏色映射留在 UI；並明確定義 `0` 是否算標準值。修正後單電阻模式下 `E24_Count` 需與畫面綠色格子數一致。
  - 復現：`r_hi_mode='Disable'`、R_Low 鎖 10000、V_Ref 3.3、V_Target 81.92 → R_Hi1=240000/R_Hi2=0 該列 worker 算 E24_Count=3，畫面綠格只有 2。

### B3. 中期目標(本月)

- [ ] 核心計算邏輯 API 化：重構計算模組，定義標準化的輸入變數與輸出格式介面，將運算邏輯與 UI 介面解耦。拆解為四步，依序執行：
  - [x] **步驟 1（已完成，使用者審閱通過）** 分壓公式抽離至零依賴的 `divider_math.py`，`calculation_worker` 與 Quick Solver 共用同一份。
  - [ ] **步驟 2【草稿】** 統一 E 系列判定（即 B2 的 bug 項），完成後領域知識即無第二份實作。
  - [ ] **步驟 3【草稿】** 拆分 `utils.py` / `config.py` 的職責。已查明呼叫者零重疊，可機械拆分：`get_resistor_list` → core；`fmt_rkm` / `determine_r_color` / `calc_gradient_hex` → presentation；`get_resource_path` → packaging。`config.py` 需將領域常數（E24_BASE、E96_BASE、PRECISION_DIGITS、MAX_TOLERANCE、MIN_TOLERANCE、WORKER_CHUNK_SIZE、WORKER_MAX_RETRY）與 UI 常數（WINDOWS_SIZE、FONTSIZE、UI_COLORS、SHEET_COLUMN_WIDTHS 等）切開。
  - [ ] **步驟 4【草稿】** 訊息格式與輸入契約（動靜最大，最後做）：(a) 移除運算層的表示層概念 —— status 訊息自帶的顏色字串、`calculation_worker.py:60` 純視覺用途的 `time.sleep(0.1)`；(b) `params` 14 個 key 改為顯式契約（dataclass/schema），驗證邏輯自 `main.py:360` `validate_input` 移出 UI（現況直接寫回 `tk_var`，與 widget 綁死）；(c) 檢討 `limit`（顯示筆數上限）反向驅動 `calculation_worker.py:142-160` 收緊容差的設計 —— 展示需求不應控制演算法行為；(d) 回報格式 `("status"|"error"|"update_tol"|"success", data)` 改為有明確 schema 的形式，便於換成 WebWorker postMessage / SSE。

### B4. 長期目標

- [ ]

## C. 交接日誌(只追加,不刪改;最新在最上,每筆一個小節)

### 2026-07-26 23:30 [plan] 使用工具: Claude Opus 5 (Claude Code)

- 完成了什麼: 依使用者宣告自 build 切入 plan 階段,將 23:20 那筆審查提案的三項待辦正式寫入〈B. 規劃〉:B1 新增三條架構決策 D1(領域知識單一來源)、D2(core/app/ui 三層)、D3(core 維持最小依賴、`divider_math.py` 零 import);B2 新增 E24_Count bug 修正項(含驗收條件與復現步驟),並補註跨 OS 任務的實際進度(Circuit 已完成、Windows/macOS 未實機驗證);B3 將「核心計算邏輯 API 化」拆為四個步驟(步驟 1 已完成並勾選,步驟 2~4 為草稿)。**新增內容一律標記〈草稿〉,B 區開頭已加註未定案前禁止依此改程式碼。**
- 防膨脹維護: 已檢查〈交接日誌〉現有 11 筆(含本筆),未達 20 筆門檻,不需壓縮;〈已封存結論〉為空,不需搬 ARCHIVE.md。
- 下一個 agent 該做什麼: 等待使用者逐項裁示 D1~D3 與 B2/B3 草稿是否〈已定案〉。定案前不得動程式碼。若使用者裁示定案並切回 [build],建議從 B3 步驟 2(E24 判定統一)開始,它同時關閉 B2 的 bug 項,範圍最小且有現成復現步驟。
- 地雷警告: 無

### 2026-07-26 23:20 [build] 使用工具: Claude Opus 5 (Claude Code)

- 完成了什麼: 第二次「運算與 UI 解耦」現況審查(比 22:55 那次更深)。確認 22:55 抽離的 `divider_math.py` 已切乾淨(全庫 grep 無第二份分壓公式,模組維持零 import);同時挖出一個先前漏掉、且已在產生錯誤畫面的重複實作。以下三項是審查產出的待辦提案,依建議順序排列。**本筆僅為 [build] 階段的留言提案,未寫入〈B. 規劃〉區(該區為 [plan] 專屬,建置階段不得改計畫);是否納入計畫由使用者裁示。**

  **(1) [Bug,優先] E24 標準值判定有兩份實作且結果不一致**
  - 兩處判定:`calculation_worker.py:128-131` 用 `np.isin(值, e24_full_list)`(完整清單比對);`utils.py:51` `determine_r_color()` 用尾數 `int(round(mantissa*100)) in E24_SIGS`(有效數字比對)。
  - 實測 799 個標準電阻值,只有 `0` 這個值兩法不一致:worker 判 True、顯示層判 False(走 `val <= 0` 回 C_RED)。根因是 `config.E24_BASE` / `E96_BASE` 的最後一個元素是 `0`,使 `0` 進了電阻表。
  - 使用者可見的後果:單電阻(Disable)模式下 `r_hi2_rng = [0.0]`,每一列的 `E24_Count` 都比畫面上實際的綠色格子多 1。實測範例:R_Low=10000/R_Hi1=240000/R_Hi2=0 → worker 算 E24_Count=3,畫面綠格只有 2。
  - 建議修法:抽出一個「回傳 E 系列分類、不回傳顏色」的共用函式供兩邊使用,顏色映射留在 UI;並順帶決定 `0` 是否算標準值。

  **(2) 拆 `utils.py` / `config.py` 的職責**
  - 已查明每個 utils 函式的呼叫者「零重疊」,可機械拆分:`get_resistor_list` → core(僅 calculation_worker 用);`fmt_rkm` / `determine_r_color` / `calc_gradient_hex` → presentation(僅 main 用);`get_resource_path` → packaging(僅 main 用)。
  - core 的邊界已可精確畫出:`divider_math` + `get_resistor_list` + config 的 7 個領域常數(E24_BASE、E96_BASE、PRECISION_DIGITS、MAX_TOLERANCE、MIN_TOLERANCE、WORKER_CHUNK_SIZE、WORKER_MAX_RETRY)。已確認 calculation_worker 用到的 config 名字「零個是 UI 常數」,且 UI 層完全沒碰 E24_BASE / get_resistor_list。
  - config.py 目前把領域常數與 WINDOWS_SIZE / FONTSIZE / UI_COLORS / SHEET_COLUMN_WIDTHS 混在同一檔,需一併切開。

  **(3) 訊息格式與輸入契約(動靜最大,建議最後做)**
  - worker 的 status 訊息自帶顏色字串 `("status", (text, "blue"/"orange"/"purple"))`,顏色是 UI 決策卻由運算層決定;`calculation_worker.py:60` 有純視覺用途的 `time.sleep(0.1)`。搬到 Web/API 都必須丟掉。
  - `params` 14 個 key 在 `main.py:422` 手工組裝,無 schema/dataclass/預設值;驗證邏輯留在 UI 層(`main.py:360` `validate_input` 直接寫回 `tk_var`,與 widget 綁死);且 `limit`(顯示筆數上限)會反過來驅動 `calculation_worker.py:142-160` 收緊容差,等於展示需求控制了演算法行為。
  - 回報格式 `("status"|"error"|"update_tol"|"success", data)` 是隱含形狀的 tuple,換 WebWorker postMessage / SSE 時無 schema 可複用。
- 下一個 agent 該做什麼: 本筆為純文件記錄,未改動任何程式碼,不需審閱。若使用者指示動手,建議從 (1) 開始 — 它是 bug 不是重構,範圍小且有實測復現步驟。
- 地雷警告: 無

### 2026-07-26 23:05 [build] 審閱結論 / 審閱者: 使用者本人

- 審閱對象: 上一筆(22:55)的 `divider_math.py` 公式抽離,分支 `refactor/divider-math-core` commit 9c8aae5。
- 結論: **通過**。使用者自行實際執行程式驗證,輸出與重構前版本一致,判定審閱通過。
- 備註: 本筆由使用者裁示,非 agent 互審(§2.1 的「禁止左手審右手」以使用者親自驗證滿足)。另外兩筆待審項目(CircuitCanvas 排版改動、tag 發版 workflow)未在本次裁示範圍內明確涵蓋,但 workflow 已由 v26.0726.1 的實際 Actions 執行成功佐證,CircuitCanvas 則已由使用者在對話中逐輪目視確認。
- 下一個 agent 該做什麼: 無。分支已可合併,合併與 push 時機待使用者指示。

### 2026-07-26 22:55 [build] 使用工具: Claude Opus 5 (Claude Code)

- 分支: `refactor/divider-math-core`(未推遠端,使用者未指示 push)
- 完成了什麼: 先做了一次「運算與 UI 解耦」現況審查,結論是單向依賴成立(calculation_worker 沒有 import tkinter),但有四處沒切乾淨:(1) 分壓公式在 UI 層有第二份實作 — `ui_components.CompactSolverFrame.calculate()` 內有四條反解;(2) 表示層概念滲入運算核心 — worker 的 status 訊息自帶顏色字串、`calculation_worker.py:60` 有純視覺用途的 `time.sleep(0.1)`;(3) 輸入契約隱性 — `params` 14 個 key 在 `main.py:422` 手工組裝、驗證留在 UI 層,且 `limit`(顯示筆數)會反過來驅動演算法收緊容差;(4) `config.py` / `utils.py` 領域邏輯與 UI 顏色、視窗尺寸混雜。
  本次只處理第 (1) 點(其餘三點屬「放錯位置」但不會算錯,留待日後):新增零依賴模組 `divider_math.py`(不 import 任何東西,純量與 numpy 陣列皆可運算,便於日後搬到 Web/API),提供 `calc_v_out()`(正解本體,不做除零檢查,供向量化熱路徑使用)與四個帶保護的單點反解 `solve_v_out / solve_r_high / solve_r_low / solve_v_ref`(無解回傳 0.0,與原 Quick Solver 行為一致)。`ui_components.py` 的四條行內公式與 `calculation_worker.py:105` 的 `v_ref * (1 + hi_tot / rlow_all)` 均改為呼叫此模組,全庫已無第二份公式(grep 確認)。
- 驗證紀錄: (a) 等價性測試:以重構前的原始行內邏輯為對照組,200,008 組隨機值 + 邊界值(各參數為 0、vout==vfb 使 ratio 為 0、極端量級)x 4 種求解目標 = 800,032 次比對,不一致 0 次;向量化正解以 50 萬元素陣列比對,與原式「逐位元相同」(np.array_equal 為 True)。(b) 端對端:xvfb 啟動實際 App,Quick Solver 四種目標互解 3.3V/100Ω/2382.42Ω/81.92V 皆回到原值,R_Low=0 時顯示 0 且不拋例外;完整 worker 搜尋跑通(結果 2 筆,最佳解誤差 0.097656%),並用 divider_math 手動覆算 Vout 相符。
- 下一個 agent 該做什麼: 本次改動需要審閱:(1) `divider_math.solve_*` 的除零/無解防護是否與重構前的 guard 條件完全等價(特別是 `solve_r_low` 在 v_ref==0 時的短路行為,原本靠 `and` 短路避免 ZeroDivisionError);(2) `calc_v_out` 刻意不做除零保護,需確認 `calculation_worker.py:24` 的 `r_low_rng[r_low_rng > 0]` 過濾確實是唯一入口、不會有 0 值漏進向量化路徑;(3) `divider_math.py` 的「零依賴」性質是否值得寫成硬規則(目前只在 docstring 註明),避免日後有人 import config 破壞可移植性。
- 地雷警告: 無

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
