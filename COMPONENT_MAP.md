# COMPONENT_MAP.md — 跨模組介面地圖

> 本檔只記「讀單一檔案還原不出來的跨檔案事實」。單一函式的輸入輸出請直接讀原始碼——全專案只有 5 檔 1417 行，讀檔比讀二手表格便宜，而且不會過期。
> 分工：`LLM_MEMORY.md` 記「現在做到哪」，本檔記「模組之間怎麼接」。

## 0. 何時讀、何時更新

- **讀**：要動 `main.py` ↔ `calculation_worker.py` 的參數／佇列契約、`config.py` 常數、或 UI 元件的 callback 簽章時。純 UI 排版調整、文件修改不必讀。
- **更新**：只在上述介面**實際改變**時（不像 `LLM_MEMORY.md` 每次交接都要動）。本檔**沒有** git hook 強制連動（對照 `scripts/hooks/pre-commit` 對 `LLM_MEMORY.md` 的強制檢查），全靠自律。**內容與程式碼不符時一律以程式碼為準。**
- 最後對照原始碼核實：2026-09-03。

## 1. 模組關聯圖

```
config.py  (純常數，無 import、無 def、無副作用)
   ↑ 被 import
   ├── utils.py               (純函式，無狀態，無 tkinter 依賴)
   ├── calculation_worker.py  (背景執行緒運算)
   ├── ui_components.py       (Tkinter 元件)
   └── main.py                (進入點 / orchestrator)

utils.py ← 被 import ── calculation_worker.py、main.py

main.py: class RVDSApp
   ├─→ 持有 ui_components 的 CompactSolverFrame / CircuitCanvas / NotesFrame
   ├─→ 動態建立 ui_components.FilterWindow
   └─→ threading.Thread → calculation_worker.worker_calculation(params, msg_queue)
                                   │
                                   ▼ queue.Queue（跨執行緒唯一溝通管道）
                          RVDSApp.check_queue()（root.after 輪詢）
```

## 2. 唯一的跨執行緒契約（本專案最容易踩雷處）

`main.py` 與 `calculation_worker.py` **沒有直接的函式回傳值**，全靠 dict-in / queue-out：

**輸入** — `params: dict`，14 個 key，由 [main.py:422](main.py#L422) 組成，於 [main.py:439](main.py#L439) 以 daemon thread 傳給 [calculation_worker.py:8](calculation_worker.py#L8) 的 `worker_calculation(p, msg_queue)`（全專案唯一呼叫點）：

```
v_ref  v_target  tol  limit
r_low_mode  r_low_lock  r_low_min  r_low_max  r_low_e24
r_hi_mode   r_hi_min    r_hi_max   r_hi1_e24  r_hi2_e24
```

worker 內一律以 `p['key']` 直接取值、無預設值保護，少一個 key 就是 `KeyError`。

**輸出** — 無 return，全部經 `msg_queue.put()` 送出 4 種 `(type, data)` tuple；唯一消費者是 [main.py:450](main.py#L450) `check_queue()`（`root.after` 輪詢，首次 100ms、之後每 20ms）：

| type | data | check_queue 的處理 |
|---|---|---|
| `status` | `(文字, 顏色)` | 更新狀態列 |
| `update_tol` | `float` | 回寫容差滑桿（worker 自動放寬／收緊時會連續送出） |
| `error` | `str` | 彈 messagebox、解鎖按鈕，**停止輪詢** |
| `success` | `(rows: list[dict], 最終容差: float)` | 寫入 `self.data_rows` → `preprocess_display_data()` → `reset_all_view()`，**停止輪詢** |

`rows` 每筆 dict 的 key 為 `R_Low` / `R_Hi1` / `R_Hi2` / `Vout` / `V_Dev` / `E24_Count`（[calculation_worker.py:135](calculation_worker.py#L135) 產生）。
[main.py:491](main.py#L491) `preprocess_display_data()` 會**原地**再塞入 `*_Str` 顯示字串與 `Color_*` 顏色欄位（也是 `utils` 三個格式化／上色函式的唯一呼叫點），`update_sheet_display()` 才讀得到這些欄位。

> ⚠️ `LLM_MEMORY.md` §B3「核心計算邏輯 API 化」要重構的就是本節。若把 dict／queue 換成 dataclass／TypedDict，本節必須同步改寫，否則會誤導後續 agent。

## 3. config.py：純常數，被所有模組 import

無 import、無 def、無副作用。改任一值等於同時改掉所有模組的預設行為，其中**直接影響計算結果與效能**的是：

- `PRECISION_DIGITS`(4) — 電阻值與容差的四捨五入位數
- `WORKER_MAX_RETRY`(40) / `WORKER_CHUNK_SIZE`(500) — 收緊迴圈次數上限、R_Low 分塊大小
- `MAX_TOLERANCE`(5) / `MIN_TOLERANCE`(0.00001) — worker 自動放寬的天花板與階梯級距
- `E24_BASE` / `E96_BASE` — 電阻表本體，經 `utils.get_resistor_list()` 展開 7 個倍率

另有一個**不在 config 裡**的寫死上限：`len(r_hi1_rng) * len(r_hi2_rng) > 50_000_000` 直接回 error（[calculation_worker.py:41](calculation_worker.py#L41)）。

## 4. 容易猜錯的關聯（否定性事實，自己查很貴）

- **`CompactSolverFrame`（Quick Solver）與計算引擎沒有資料交換。** 它是獨立的分壓公式反算器，只在 [main.py:390-401](main.py#L390-L401) 被 `run_calculation_trigger` **單向寫入** `target_mode` 與 V_Target／V_Ref／R_Low 鎖定值；它算出的結果不會回流進 `params`。
- **`CircuitCanvas.draw_circuit()`（[ui_components.py:261](ui_components.py#L261)）只在 [main.py:253](main.py#L253) 被直接呼叫一次做初繪**，之後全由 [main.py:89](main.py#L89) 對 `r_hi_mode` 的 `trace_add` 與自身 `<Configure>` 綁定觸發。改 `r_hi_mode` 的賦值方式會連帶影響重繪時機。
- **`FilterWindow` 用 callback 回傳結果、不是 return。** [main.py:614](main.py#L614) 以 `lambda res: self.set_filter(col_idx, res)` 建立，關窗時才觸發表格重繪。
- **會寫檔的只有兩個方法**：`save_notes_as`（[main.py:287](main.py#L287)，可存 .csv／.txt）與 `export_csv`（[main.py:631](main.py#L631)）。另 `show_about`（[main.py:671](main.py#L671)）會**讀** `CREDITS.txt`，路徑經 `utils.get_resource_path()` 解析，開發環境與 PyInstaller 打包後不同。

## 5. 現況

**全專案無自動化測試**：沒有 `tests/` 目錄，`requirements.txt` 只列 `numpy`、`tksheet`。所有驗證紀錄一律看 `LLM_MEMORY.md` §C 交接日誌（例如 `CircuitCanvas` 與 `configure_system_settings` 目前只在 Linux + xvfb 驗證過，Windows／macOS 未實機驗證）——本檔**不重複記錄驗證狀態**，避免與交接日誌雙軌腐爛。

若要開始補測試，最好下手的順序：`utils.py`（6 個純函式、零 UI 依賴）→ `worker_calculation`（塞假 `queue.Queue` 斷言訊息序列）→ UI 元件（需 headless X）。
