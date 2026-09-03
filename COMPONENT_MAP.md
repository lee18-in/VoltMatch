# COMPONENT_MAP.md — 物件地圖（輸入 / 輸出 / 關聯 / 驗證狀態）

> 狀態：**草稿**（2026-09-03 建立）。與 `LLM_MEMORY.md` 分工不同：`LLM_MEMORY.md` 記「專案現在進行到哪」（交接狀態），本檔記「程式碼介面長什麼樣」（物件的輸入/輸出/關聯/是否驗證過）。

## 如何使用與維護本檔

- **給 agent 的用途**：改動程式碼前，先查這裡搞懂「這個物件吃什麼、吐什麼、被誰呼叫、有沒有驗證過」，避免只憑函式名稱猜介面。
- **更新時機**：只在物件的輸入/輸出/關聯**實際改變**時才需要同步更新本檔對應區塊（不像 `LLM_MEMORY.md` 每次交接都要動）。目前**沒有** git hook 強制連動本檔（對照 `scripts/hooks/pre-commit` 強制 `LLM_MEMORY.md` 同步的做法），全靠 agent 自律，請小心本檔內容跟程式碼脫鉤。
- **驗證狀態圖例**：
  - ✅ 已驗證 — 有明確驗證方式與時間可查（對應 `LLM_MEMORY.md` §C 交接日誌）
  - ⚠️ 部分驗證 — 驗證過但範圍有限（例如只在單一作業系統測過）
  - ❌ 未驗證 — 專案目前**無自動化測試**（無 `tests/` 目錄，`requirements.txt` 只列 `numpy`、`tksheet`，未含 pytest 等測試框架），僅靠手動走查，且多數物件連手動驗證紀錄都沒有留在交接日誌裡
- **本檔涵蓋範圍（草稿階段）**：優先收錄跨模組資料流與核心邏輯物件；`main.py` 裡單純轉發 UI 事件的次要方法先分類列清單、不逐一展開輸入輸出（見 §3），需要時再補。

---

## 0. 模組關聯圖（資料流）

```
config.py  (純常數，無函式，無副作用)
   ↑ import
   ├── utils.py               (純函式，無狀態，無 tkinter 依賴)
   ├── calculation_worker.py  (背景執行緒運算)
   ├── ui_components.py       (Tkinter 元件)
   └── main.py                (應用程式進入點 / orchestrator)

utils.py ← import ── calculation_worker.py
utils.py ← import ── main.py

main.py: class RVDSApp
   │ 建立並持有
   ├─→ ui_components.CompactSolverFrame   （獨立分壓反算元件，見 §2）
   ├─→ ui_components.CircuitCanvas        （電路圖繪製元件，見 §2）
   ├─→ ui_components.NotesFrame           （筆記元件，見 §2）
   ├─→ ui_components.FilterWindow         （表格欄位篩選彈窗，動態建立，見 §2）
   └─→ threading.Thread
            → calculation_worker.worker_calculation(params, msg_queue)
                    │
                    ▼ queue.Queue（跨執行緒訊息，唯一溝通管道）
            main.py: RVDSApp.check_queue() 輪詢（root.after 迴圈）
                    → 寫入 self.data_rows
                    → preprocess_display_data()（呼叫 utils 三個格式化/上色函式）
                    → update_sheet_display()（寫入 tksheet.Sheet）
```

**關鍵耦合點**：`main.py` 與 `calculation_worker.py` 之間**沒有直接函式呼叫回傳值**，全靠 `params: dict`（14 個 key，見 §1）當輸入、`msg_queue` 當輸出通道。這個 dict-in / queue-out 的隱性介面就是 `LLM_MEMORY.md` §B3「核心計算邏輯 API 化」想要重構的對象——重構時本檔 §1 第一列要跟著同步更新。

---

## 1. 核心資料流物件（優先讀這裡）

| 物件 | 輸入 | 輸出 | 關聯 | 驗證狀態 |
|---|---|---|---|---|
| `calculation_worker.worker_calculation(p, msg_queue)`<br>[calculation_worker.py:8](calculation_worker.py#L8) | `p: dict`（14 key：`v_ref`,`v_target`,`tol`,`limit`,`r_low_mode`,`r_low_lock`,`r_low_min`,`r_low_max`,`r_low_e24`,`r_hi_mode`,`r_hi_min`,`r_hi_max`,`r_hi1_e24`,`r_hi2_e24`，由 `main.py:422` 組成）；`msg_queue: queue.Queue` | 無 return 值；透過 `msg_queue.put()` 送出 5 種 tuple 訊息：`"status"`(文字,顏色)、`"update_tol"`(float)、`"error"`(str)、`"success"`((rows:list[dict], 最終容差:float)) | 上游：`main.py:439` 以 `threading.Thread` 呼叫（唯一呼叫點）；內部依賴 `utils.get_resistor_list`、`config.E24_BASE/E96_BASE/PRECISION_DIGITS/WORKER_MAX_RETRY/WORKER_CHUNK_SIZE`；下游消費者：`main.py:450 check_queue()` | ❌ 未驗證 — 交接日誌中找不到針對此函式（組合搜尋、自動放寬/收緊容差邏輯）的驗證紀錄，無單元測試 |
| `main.py: RVDSApp.run_calculation_trigger()`<br>[main.py:377](main.py#L377) | 讀取 `self.v_ref/v_target/tolerance/r_low_*/r_hi_*` 等 tk.Variable | 組成 `params dict`、啟動背景執行緒；不直接 return（例外時彈 `messagebox`） | `calculation_worker.worker_calculation` 的唯一呼叫點；副作用：同步一份數值到 `CompactSolverFrame` | ❌ 未驗證 |
| `main.py: RVDSApp.check_queue()`<br>[main.py:450](main.py#L450) | `self.msg_queue` | 更新 `self.data_rows`、`self.status_label`；觸發 `preprocess_display_data()` / `reset_all_view()` | `msg_queue` 的唯一消費者；與 `worker_calculation` 透過佇列間接耦合（非直接呼叫） | ❌ 未驗證 |
| `main.py: RVDSApp.preprocess_display_data(limit_val)`<br>[main.py:491](main.py#L491) | `self.data_rows`（worker 產出的 dict list）、`limit_val: float`（目前容差） | 原地修改 `self.data_rows`：新增 `*_Str` 顯示字串欄位、`Color_*` 顏色欄位 | 呼叫 `utils.fmt_rkm` / `utils.determine_r_color` / `utils.calc_gradient_hex`；被 `check_queue` 呼叫；輸出供 `update_sheet_display` 使用 | ❌ 未驗證 |

### utils.py（純函式，無 UI 依賴 — 全專案最適合優先補單元測試的一層）

| 函式 | 輸入 | 輸出 | 備註 | 驗證狀態 |
|---|---|---|---|---|
| `get_resource_path(relative_path)` [utils.py:8](utils.py#L8) | `str`（相對路徑） | `str`（絕對路徑，依 `sys.frozen` 判斷開發/打包環境） | 被 `main.py:29` 用於定位 `CREDITS.txt` | ❌ 未驗證 |
| `get_resistor_list(base_values, include_zero=True)` [utils.py:16](utils.py#L16) | `list[float]`（基值）、`bool` | `np.ndarray`（去重排序後的完整電阻值，展開 7 個倍率 1~1e6） | 被 `calculation_worker.py:14` 用於展開 E24/E96 電阻表 | ❌ 未驗證 |
| `generate_sig_figs(base_list)` [utils.py:25](utils.py#L25) | `list[float]` | `set[int]`（乘 100 取整） | 模組載入時算出全域常數 `E24_SIGS`/`E96_SIGS` | ❌ 未驗證 |
| `fmt_rkm(val)` [utils.py:32](utils.py#L32) | `float` 或 `None` | `str`（BS 1852 格式，如 `"2K2"`、`"100R"`） | 被 `preprocess_display_data` 用於顯示欄位 | ❌ 未驗證 |
| `determine_r_color(val)` [utils.py:51](utils.py#L51) | `float` | `str`（hex 色碼；依屬於 E24/E96/皆非分三色） | 依賴模組載入時算好的 `E24_SIGS`/`E96_SIGS` | ❌ 未驗證 |
| `calc_gradient_hex(ratio)` [utils.py:63](utils.py#L63) | `float`（建議 0.0~1.0，超界會被夾住） | `str`（hex 色碼；綠→黃→紅→紫三段線性插值） | 被誤差顯示欄位上色使用 | ❌ 未驗證 |

---

## 2. UI 元件（ui_components.py）

| 物件 | 輸入 | 輸出 | 關聯 | 驗證狀態 |
|---|---|---|---|---|
| `configure_system_settings(root)` [ui_components.py:8](ui_components.py#L8) | `tk` root | `default_font: tuple`；副作用：直接改寫 `ttk.Style` 全域樣式表 | 依 `platform.system()` 切換字型/DPI；被 `main.py:44` 在 `RVDSApp.__init__` 呼叫一次 | ⚠️ 部分驗證 — 僅 Linux 分支有交接日誌驗證紀錄（見 §5），Windows/macOS 分支未見驗證紀錄 |
| `FilterWindow(parent, col_name, unique_values, current_filter, callback, font_style)` [ui_components.py:41](ui_components.py#L41) | 見參數；`callback: Callable[[set], None]` | 不 return；透過 `callback(selected_set)` 回呼 | 由 `main.py:614 open_filter_popup` 動態建立（`lambda res: self.set_filter(col_idx, res)` 當 callback）；關閉時觸發 `main.py:616 set_filter` → `update_sheet_display` | ❌ 未驗證 |
| `CompactSolverFrame(parent, colors)` / `.calculate()` [ui_components.py:123](ui_components.py#L123) | `parent`, `colors: dict`；內部 4 個 `tk.StringVar`（`sv_low`/`sv_vfb`/`sv_hi`/`sv_vout`）雙向繫結 4 個 Entry | 不 return；直接改寫自己的 `StringVar` 顯示反算結果 | 獨立的分壓公式反算元件（`V = Vref*(1+Rhi/Rlow)`），**與 `calculation_worker` 主計算引擎無資料交換**；只在 `main.py:390 run_calculation_trigger` 被動同步 V_target/V_ref/R_Low 鎖定值 | ❌ 未驗證（含防遞迴旗標 `_is_calculating`，邏輯有一定複雜度但無測試） |
| `CircuitCanvas(parent, ui_colors, app_font)` / `.draw_circuit(r_hi_mode)` [ui_components.py:243](ui_components.py#L243) | `r_hi_mode: str`（`"Disable"` = 單電阻 / 其他 = 雙電阻） | 不 return；直接在畫布繪圖，並呼叫 `self.configure(width=,height=)` 回報所需尺寸 | 被 `main.py:89` 對 `r_hi_mode` 的 `trace_add` 自動觸發重繪；依賴 `config.FONTSIZE` | ⚠️ 部分驗證 — 2026-07-26 交接日誌：以 `xvfb-run` 實際啟動、4 組字型量測 `fits=True`，PostScript 轉圖目視確認無裁切；**但同一筆日誌明載 Windows/macOS 實機未驗證，且該筆本身仍列在 `LLM_MEMORY.md` §A 阻塞點的待審閱堆疊中**，正式驗證結論尚未定案 |
| `NotesFrame(parent, app_font, save_callback)` [ui_components.py:370](ui_components.py#L370) | `save_callback: Callable[[], None]` | 不 return | `save_callback` 由 `main.py:287 save_notes_as` 提供 | ❌ 未驗證 |

---

## 3. main.py: RVDSApp — 其餘方法（次要 UI glue，草稿階段先分類列清單）

| 分類 | 方法 | 關聯 |
|---|---|---|
| 排序 / 篩選 | `perform_sort`, `manual_sort`, `get_selected_col`, `filter_from_cell`, `sort_asc_from_cell`, `sort_desc_from_cell`, `clear_filter_from_cell`, `open_filter_popup`, `set_filter`, `clear_filter`, `reset_all_view` | 皆操作 `self.active_filters` / `self.sort_state`，最終呼叫 `update_sheet_display()` 重繪 `tksheet` |
| 輸入輔助 | `create_entry`, `validate_input`, `_sync_val_from_slider`, `_sync_slider_from_val` | 操作 `tk.Variable` 與滑桿的非線性映射，被 `create_widgets()` 內的 UI 綁定呼叫 |
| 其他 | `copy_selected_display_row`, `apply_sheet_column_layout`, `save_notes_as`, `export_csv`, `show_about` | 個別對應單一 UI 功能；`export_csv`/`save_notes_as` 會寫檔至使用者選擇的路徑（唯二有檔案系統副作用的方法） |

全數 ❌ 未驗證（無自動化測試）。草稿階段暫不逐一展開輸入輸出；若要重構這塊（例如拆出獨立的 SheetController）再回來補。

---

## 4. config.py

純常數模組，無函式、無副作用；被本專案**所有**其他模組 import。內容含顏色/字型/精度/視窗尺寸/UI 預設值/E24·E96 標準電阻表。

⚠️ 改動本檔任何值都會影響上述所有物件的預設行為，尤其 `PRECISION_DIGITS`、`WORKER_MAX_RETRY`、`WORKER_CHUNK_SIZE` 直接影響 `calculation_worker.py` 的計算結果正確性與效能，改動後應視同改動了 §1 那一整排物件。

驗證狀態：不適用（純資料，無邏輯可測）。

---

## 5. 已知落差 / 後續建議

- **全專案無自動化測試**：無 `tests/` 目錄、無 pytest，`requirements.txt` 只列 `numpy`、`tksheet`。若要開始補測試，建議優先順序：
  1. `utils.py`（純函式、零 UI 依賴，最好測，見 §1 表格）
  2. `calculation_worker.worker_calculation`（純邏輯但吃 `dict`/吐 `queue`，可用假 `queue.Queue` 斷言訊息序列）
  3. `ui_components.py`（需要 tkinter headless / Xvfb，比照 2026-07-26 交接日誌那次手動驗證的做法）
- **§B3 中期目標關聯**：`LLM_MEMORY.md` §B3「核心計算邏輯 API 化」若真的把 `worker_calculation` 的 dict-in / queue-out 介面改成 dataclass/TypedDict，本檔 §1 第一列（連同「關鍵耦合點」段落）要同步改寫，否則本檔會誤導後續 agent。
- **`CircuitCanvas` 與 `configure_system_settings` 的驗證結論尚未定案**：兩者都只在 Linux 環境驗證過，且前者對應的交接日誌條目本身還卡在 `LLM_MEMORY.md` §A 阻塞點的待審閱堆疊裡（§2.1 Review Loop），本檔標記的 ⚠️ 會隨審閱結果變動，審閱通過/不通過後記得回來更新這兩列。
- **§3 尚未逐一展開**：`main.py` 的次要 UI glue 方法目前只分類列清單，沒有個別寫輸入輸出，這是本檔草稿階段最大的覆蓋缺口。
