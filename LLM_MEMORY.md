# LLM_MEMORY.md — 工作記憶(agent 讀寫;規則見 AGENTS.md,勿在此重複)

## A. 目前狀態(每次交接必更新)

- 目前階段: plan(2026-07-26 23:30 由使用者宣告,自 build 切入)
- 最後更新: 2026-07-27 23:05 / 當時階段: plan
- 最新 commit: 見 git log(已發版 tag: v26.0726.1;目前工作分支 `refactor/divider-math-core`,已推遠端同名分支,未合併 main)
- 進行中任務: 逐項裁示 B1 的架構決策。**D1a(`0` 的領域語意)已定案**;D1 本體、D2、D3 仍為〈草稿〉。
- 待使用者裁示: (1) D1 本體(領域知識單一來源)、D2(core/app/ui 三層)、D3(core 最小依賴,agent 建議分 Tier 0/Tier 1 兩級) 是否定案;(2) `WORKER_CHUNK_SIZE` 該歸 core 還是 app(其註解理由「避免 UI 卡頓」與 core 定位矛盾);(3) B2 的 E24_Count bug 走 A 還是 B 路線(使用者已表示延後再議)。
- 阻塞點: 除 D1a 外,B 區其餘內容仍標記〈草稿〉,**未定案前 build 階段不得依此改動程式碼**(AGENTS.md §1)。
- 待辦(已定案但尚未落地): D1a 的禁止移除 `0` 規則需寫成 `config.py` / `utils.py` 的程式碼註解 —— **屬程式碼改動,須待使用者宣告 [build] 階段才能執行**。

## B. 規劃(規劃階段 [plan] 專屬區;狀態: 草稿 | 已定案)

> 本區 2026-07-26 23:30 新增的 D1~D3 與 B2/B3 條目狀態一律為〈草稿〉,依 AGENTS.md §1,未標記〈已定案〉前禁止依此改動程式碼。

### B1. 架構決策(已定案後鎖定,建置/維運階段不得改)

| # | 決策 | 理由 | 狀態 |
|---|------|------|------|
| D1 | 領域知識單一來源:分壓公式、E 系列標準值判定等領域規則,全庫只能有一份實作,UI 層一律呼叫共用模組,不得自行寫第二份 | 已實際出事兩次:分壓公式曾同時存在於 `calculation_worker` 與 Quick Solver(已修);E 系列判定至今仍有兩份且結果不一致,造成單電阻模式 E24_Count 錯誤 | 草稿 |
| **D1a** | **`0` 的領域語意:`0` 是合法的電路組態(不裝件/短路),但不是 E 系列標準值。電阻表中的 `0` 一律保留,禁止移除;E 系列判定則不得把 `0` 算成標準值** | 見下方〈D1a 定案條文〉,含實測數據 | **已定案(2026-07-27 使用者裁示)** |
| D2 | 分層為 core / app / ui 三層:core 零 UI 依賴、零執行緒依賴(進度以 callback 或 generator 回報);app 負責輸入驗證、契約定義與結果格式化;ui 只處理 tkinter、顏色與版面 | 為 B3 的 API 化與日後 Web 前端鋪路;現況 core 邊界已可精確畫出(`divider_math` + `get_resistor_list` + 7 個領域常數),拆分屬機械工 | 草稿 |
| D3 | core 層模組維持最小依賴,`divider_math.py` 維持零 import(不得 import config/numpy/UI) | 確保運算核心可原封不動移植到其他前端(Web/API/CLI) | 草稿 |

#### D1a 定案條文(2026-07-27 使用者裁示,已定案,不得擅改)

**規則**

1. **禁止把 `0` 移出電阻表**。具體禁止事項:不得刪除 `config.E24_BASE` / `config.E96_BASE` 末尾的 `0`;不得把 `utils.get_resistor_list()` 的 `include_zero` 預設值改為 `False`,也不得在呼叫端傳 `include_zero=False`。
2. **`0` 不是 E 系列標準值**。E 系列判定/分類不得把 `0` 算成 E24 或 E96,`E24_Count` 不得計入 `0`。UI 顏色維持現狀(`val <= 0` → `C_RED`)。

**理由(實測數據,2026-07-27 以唯讀腳本查證)**

- `0` 在高側代表「不裝件 / 短路直通」,是合法的電路組態,不是髒資料。
- 移除 `0` 會失去兩類解:
  - (A) 32 個「一顆湊得出、兩顆非零湊不出」的 R_Hi 總和,全落在 1.0Ω~1.96Ω(最小非零電阻 1.0Ω,兩顆最小和 2.0Ω,故 <2Ω 只能靠一顆+0)。此類在預設 R_Low 範圍(≥1000Ω)下實際搜不到,影響有限。
  - (B) **`hi_tot = 0`(R_Hi1=R_Hi2=0,直通不分壓)。實測 `V_Ref=3.3 / V_Target=3.3` 時,343 組 0% 誤差解「全部」依賴 `0`;移除後一組都搜不到,程式會一路放寬容差最後回報 No solution found。** 這是真正的要害。
- 危險性:此 regression 不會有人特地去測「目標電壓等於參考電壓」,可以躺很久不被發現。故立為硬規則並寫進程式碼註解。

**驗收條件(修 E 系列判定時必須同時滿足)**

- (a) 單電阻(Disable)模式下 `E24_Count` 與畫面綠色格子數一致。
- (b) **回歸測試**:`V_Ref=3.3, V_Target=3.3` 仍能搜到 R_Hi 總和為 `0` 的 0% 誤差解。

### B2. 短期目標(本週)

- [ ] 跨作業系統 UI/UX 相容性優化：針對不同作業系統（Windows / Linux 等）進行畫面顯示與字體排版調整，確保視覺體驗一致。
  - 進度：Circuit 電路圖區塊已改為依字型度量排版並填滿版面（已完成）；`MIN_WINDOW_SIZE` 已導入。**尚未在 Windows / macOS 實機驗證**。
- [ ] 【Bug・待排程】修正 E24_Count 判定不一致：`calculation_worker.py:128-131` 用 `np.isin(值, e24_full_list)`、`utils.py:51` `determine_r_color()` 用有效數字比對，兩法對 `0` 的判定相反。
  - **`0` 的處置已由 D1a 定案：電阻表原封不動,只修「判定」。切勿去動 `E24_BASE` 末尾的 `0` 或 `include_zero`(會炸掉 V_Target≈V_Ref 的情境,詳見 D1a)。**
  - 使用者可見後果(2026-07-27 補查):(1) 單電阻(Disable)模式下 `r_hi2_rng = [0.0]`,每列 `E24_Count` 比畫面綠色格子多 1;(2) **`main.py:496` `_cnt_color` 是 `3→綠 2→黃 1→紅 0→紫`,單電阻模式只有兩顆實體電阻本來到不了 3,因多算 1 導致「實際 2 顆 E24」顯示成綠色、實際 1 顆顯示黃色 —— E24 欄底色語意整體位移一級**;(3) CSV 匯出(`main.py:657`)帶著同樣錯的數字。
  - 不受影響(已確認):R_Low / R_Hi1 / R_Hi2 / Vout / Dev% 全部正確;排序也不受影響(單電阻模式每列同時 +1,相對順序不變)。
  - 另有語意瑕疵(次要):勾「R1: E24 Only」時 `0` 因在 `e24_full_list` 內而被當成 E24 保留,故 R_Hi1 仍可能是 `0`。R_Low 側有 `r_low_rng > 0` 擋著不受影響。
  - 驗收條件:抽出「回傳 E 系列分類、不回傳顏色」的共用函式供兩邊使用,顏色映射留在 UI。須同時滿足 D1a 的 (a)(b) 兩條。
  - 復現：`r_hi_mode='Disable'`、R_Low 鎖 10000、V_Ref 3.3、V_Target 81.92 → R_Hi1=240000/R_Hi2=0 該列 worker 算 E24_Count=3，畫面綠格只有 2。
  - **排程未定**:agent 曾提兩條路線 —— A(現在單獨修)/ B(併入 B3 步驟 3 一起做,因修法同為「抽出共用判定函式」)。2026-07-27 使用者表示兩案都可能被漏算,**暫不選定,延後再議**。動工前須先向使用者確認走哪條。

### B3. 中期目標(本月)

- [ ] 核心計算邏輯 API 化：重構計算模組，定義標準化的輸入變數與輸出格式介面，將運算邏輯與 UI 介面解耦。拆解為四步，依序執行：
  - [x] **步驟 1（已完成，使用者審閱通過）** 分壓公式抽離至零依賴的 `divider_math.py`，`calculation_worker` 與 Quick Solver 共用同一份。
  - [ ] **步驟 2【草稿】** 統一 E 系列判定（即 B2 的 bug 項），完成後領域知識即無第二份實作。
  - [ ] **步驟 3【草稿】** 拆分 `utils.py` / `config.py` 的職責。已查明呼叫者零重疊，可機械拆分：`get_resistor_list` → core；`fmt_rkm` / `determine_r_color` / `calc_gradient_hex` → presentation；`get_resource_path` → packaging。`config.py` 需將領域常數（E24_BASE、E96_BASE、PRECISION_DIGITS、MAX_TOLERANCE、MIN_TOLERANCE、WORKER_CHUNK_SIZE、WORKER_MAX_RETRY）與 UI 常數（WINDOWS_SIZE、FONTSIZE、UI_COLORS、SHEET_COLUMN_WIDTHS 等）切開。
  - [ ] **步驟 4【草稿】** 訊息格式與輸入契約（動靜最大，最後做）：(a) 移除運算層的表示層概念 —— status 訊息自帶的顏色字串、`calculation_worker.py:60` 純視覺用途的 `time.sleep(0.1)`；(b) `params` 14 個 key 改為顯式契約（dataclass/schema），驗證邏輯自 `main.py:360` `validate_input` 移出 UI（現況直接寫回 `tk_var`，與 widget 綁死）；(c) 檢討 `limit`（顯示筆數上限）反向驅動 `calculation_worker.py:142-160` 收緊容差的設計 —— 展示需求不應控制演算法行為；(d) 回報格式 `("status"|"error"|"update_tol"|"success", data)` 改為有明確 schema 的形式，便於換成 WebWorker postMessage / SSE。

### B4. 長期目標

- [ ]

## C. 交接日誌(只追加,不刪改;最新在最上,每筆一個小節)

### 2026-07-27 23:05 [plan] 使用工具: Claude Opus 5 (Claude Code)

- 完成了什麼:
  1. **應使用者要求把 D1~D3 從一句話展開成詳細條文**(含各層 import 白名單、現況檔案→目標層的完整映射表、可驗收判準)。過程中實際讀碼查出一條先前未記錄的隱性汙染鏈:`calculation_worker → utils → config`,而 `config` 內含 `C_GREEN`/`UI_COLORS`/`WINDOWS_SIZE`,**運算層目前是間接依賴 UI 常數的**,此為 D2 的實證。
  2. **修正 B2 對 E24 bug 根因的記載(原記載不完整,只修會無效)**:原寫「根因是 `E24_BASE` 末尾有 `0`」,但 `utils.get_resistor_list()` 簽名為 `include_zero=True`,`calculation_worker.py:14-16` 三處呼叫皆走預設值,`0` 有「基值末尾」與「include_zero」**兩個獨立來源**,只砍其一等於沒改。
  3. **使用者提問「雙電阻模式下會不會有依賴 `0` 的優良解,移除後就消失」,已實測查證,答案是會,且比預期嚴重**:寫唯讀腳本(置於 scratchpad,未進版控)分析 799 個電阻值,結論見 D1a 條文 —— `V_Ref=3.3/V_Target=3.3` 時 343 組 0% 誤差解「全部」依賴 `0`,移除後全滅。
  4. **使用者裁示 D1a 定案**:`0` 是合法組態但非 E 系列標準值,電阻表原封不動、禁止移除,只修判定。已寫入 B1(新增 D1a 列 + 〈D1a 定案條文〉小節,含實測數據與 (a)(b) 兩條驗收)。
  5. 補查 E24_Count 的實際影響面並寫入 B2:除數字多 1 外,**`main.py:496` `_cnt_color` 的顏色語意在單電阻模式整體位移一級**(實際 2 顆 E24 會顯示成「三顆全中」的綠色),此點原日誌未記載;另確認排序與所有電阻/電壓/誤差數值均不受影響。
- 驗證紀錄: 兩支唯讀分析腳本以專案 `.venv` 實際執行(`PYTHONPATH` 指向專案根目錄),未修改專案任何檔案。輸出重點:電阻表 799 個值(非零 798、含 0);兩顆非零可湊出 216,776 個相異總和;移除 `0` 失去 32 個 <2Ω 的單顆總和(預設 R_Low≥1000Ω 下實際不可達)與 `hi_tot=0` 全部解;`V_Target=3.3` → 343 組 0% 解全部依賴 `0`,對照組 `V_Target=3.3396` → 272 組 0% 解、0 組依賴 `0`。
- 本次未改動任何程式碼(僅本檔),不需審閱。
- 下一個 agent 該做什麼:
  1. **先問使用者是否宣告 [build]**。有一項已定案但尚未落地的程式碼改動:把 D1a 的「禁止移除 `0`」規則寫成 `config.py`(`E24_BASE`/`E96_BASE` 上方)與 `utils.py`(`get_resistor_list` 的 `include_zero` 參數處)的註解。使用者 2026-07-27 已明確要求要有這段註解,但當時階段為 plan,依 AGENTS.md §1 未執行。**內容照抄 D1a 條文,不得自行改寫語意。**
  2. 其餘待裁示項目見〈A. 目前狀態〉的「待使用者裁示」三點。D2/D3 的詳細條文已在本次對話中口頭產出但**尚未寫入本檔**(因使用者未裁示定案),若使用者要求可重新展開;要點已記於 B1 表格與 B3 步驟 3。
  3. E24_Count bug 的 A/B 路線使用者表示延後再議,**不要自行選定開工**。
- 地雷警告: **絕對不要為了修 E24_Count 而把 `0` 移出電阻表**(刪 `E24_BASE` 末尾的 `0`、或把 `include_zero` 改 `False` 皆屬之)。這會讓 `V_Target ≈ V_Ref` 的使用情境從 343 組完美解變成搜不到任何解,且不會有人特地去測這個情境,可以躺很久不被發現。詳見 B1〈D1a 定案條文〉。

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
