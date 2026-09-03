# COMPONENT_MAP.md — 專案知識庫（不衰減層）

> **這份檔案存放「程式碼裡沒有、而且不會隨時間失效」的知識**，目的是讓任何 LLM 換手後能快速進入狀況、不重複踩已經踩過的坑。
>
> 與 `LLM_MEMORY.md` 的分工：
> - `LLM_MEMORY.md` = **會衰減的**（現在做到哪、下一步、交接流水帳）。內容隨時間失效，日誌滿 20 筆會被壓縮封存。
> - 本檔 = **不衰減的**（專案長怎樣、為什麼這樣決定、驗證過什麼、環境有什麼隱性條件）。兩年後依然有效。
>
> ⚠️ **萃取規則（防失憶的關鍵，不做這步就會丟知識）**：封存任何一筆交接日誌之前，先問「這筆裡有沒有以後還會用到的事實？」——決策理由、否決過的方案、環境特性、驗證結果——有就先搬進本檔對應章節，**再**封存日誌。日誌會過期，本檔不會。
>
> 本檔無 git hook 強制連動，**內容與程式碼不符時一律以程式碼為準**。每個主張都附 `file:line`，是為了讓你能幾秒內抽查，而不必重讀全部。

---

## 1. 六十秒進入狀況

**VoltMatch** — 分壓電阻組合最佳化工具，Tkinter 桌面 app。核心理念不是給「唯一最佳解」，而是**窮舉容差範圍內所有可行的電阻組合**，讓工程師依庫存／成本自行挑選。

| | |
|---|---|
| 執行 | `python main.py`（無測試指令，見 §8） |
| 打包 | `pyinstaller VoltMatch.spec` |
| 依賴 | `numpy`、`tksheet`（`requirements.txt` 全部內容） |
| 進入點 | `main.py` 底部 `if __name__ == "__main__"` → `RVDSApp(tk.Tk())` |
| 發佈 | 推 `v*` tag 觸發 GitHub Actions 建 Windows exe + Linux AppImage 並開 Release |

五個原始碼檔（共 1417 行，全部讀完約 25k token，讀得起）：

| 檔案 | 行數 | 職責 |
|---|---|---|
| `main.py` | 694 | `RVDSApp` 應用程式主體：UI 組裝、表格排序／篩選、執行緒調度 |
| `ui_components.py` | 402 | 4 個 Tkinter 元件 + 1 個系統設定函式 |
| `calculation_worker.py` | 174 | 背景執行緒的窮舉運算（全專案唯一的計算邏輯） |
| `utils.py` | 75 | 6 個純函式（電阻表展開、BS 1852 格式化、上色） |
| `config.py` | 72 | 純常數，無 import、無 def |

**最該先知道的三件事**：

1. `main.py` ↔ `calculation_worker.py` 之間是 **dict-in / queue-out**，沒有直接回傳值（§3）——全專案最容易改壞的地方。
2. **沒有自動化測試**，所有驗證都是手動的，而且**只在 Linux 做過**（§8）。
3. 底部的 Quick Solver 面板與主計算引擎**完全沒有資料交換**（§4），這點很多人會猜錯。

---

## 2. 模組關聯圖

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

---

## 3. 唯一的執行緒邊界（改壞機率最高處）

`main.py` 與 `calculation_worker.py` **沒有直接的函式回傳值**，全靠 dict-in / queue-out。以下都是讀簽章看不出來的約束：

**輸入** — `params: dict`，14 個 key，由 [main.py:422](main.py#L422) 組成，於 [main.py:439](main.py#L439) 以 daemon thread 傳給 [calculation_worker.py:8](calculation_worker.py#L8) 的 `worker_calculation(p, msg_queue)`（全專案唯一呼叫點）：

```
v_ref  v_target  tol  limit
r_low_mode  r_low_lock  r_low_min  r_low_max  r_low_e24
r_hi_mode   r_hi_min    r_hi_max   r_hi1_e24  r_hi2_e24
```

worker 內一律 `p['key']` 直接取值、**無預設值保護，少一個 key 就是 `KeyError`**。

**輸出** — 無 return，全部經 `msg_queue.put()` 送出 **4 種** `(type, data)` tuple；唯一消費者是 [main.py:450](main.py#L450) `check_queue()`（`root.after` 輪詢，首次 100ms、之後每 20ms）：

| type | data | check_queue 的處理 |
|---|---|---|
| `status` | `(文字, 顏色)` | 更新狀態列 |
| `update_tol` | `float` | 回寫容差滑桿（worker 自動放寬／收緊時會連續送出） |
| `error` | `str` | 彈 messagebox、解鎖按鈕，**停止輪詢** |
| `success` | `(rows: list[dict], 最終容差: float)` | 寫入 `self.data_rows` → `preprocess_display_data()` → `reset_all_view()`，**停止輪詢** |

`rows` 每筆 dict 的 key：`R_Low` / `R_Hi1` / `R_Hi2` / `Vout` / `V_Dev` / `E24_Count`（[calculation_worker.py:135](calculation_worker.py#L135) 產生）。

[main.py:491](main.py#L491) `preprocess_display_data()` 會**原地**再塞入 `*_Str` 顯示字串與 `Color_*` 顏色欄位（也是 `utils` 三個格式化／上色函式的唯一呼叫點），`update_sheet_display()` 才讀得到這些欄位。

---

## 4. 容易猜錯的關聯（否定性事實，自己查很貴）

- **`CompactSolverFrame`（Quick Solver）與計算引擎沒有資料交換。** 它是獨立的分壓公式反算器，只在 [main.py:390-401](main.py#L390-L401) 被 `run_calculation_trigger` **單向寫入** `target_mode` 與 V_Target／V_Ref／R_Low 鎖定值；它算出的結果不會回流進 `params`。
- **`CircuitCanvas.draw_circuit()`（[ui_components.py:261](ui_components.py#L261)）只在 [main.py:253](main.py#L253) 被直接呼叫一次做初繪**，之後全由 [main.py:89](main.py#L89) 對 `r_hi_mode` 的 `trace_add` 與自身 `<Configure>` 綁定觸發。
- **`FilterWindow` 用 callback 回傳結果、不是 return。** [main.py:614](main.py#L614) 以 `lambda res: self.set_filter(col_idx, res)` 建立，關窗時才觸發表格重繪。
- **會寫檔的只有兩個方法**：`save_notes_as`（[main.py:287](main.py#L287)，可存 .csv／.txt）與 `export_csv`（[main.py:631](main.py#L631)）。另 `show_about`（[main.py:671](main.py#L671)）會**讀** `CREDITS.txt`，路徑經 `utils.get_resource_path()` 解析，開發環境與 PyInstaller 打包後不同。

---

## 5. config.py 影響面

純常數，被所有模組 import。改任一值等於同時改掉所有模組的預設行為，其中**直接影響計算結果與效能**的是：

- `PRECISION_DIGITS`(4) — 電阻值與容差的四捨五入位數
- `WORKER_MAX_RETRY`(40) / `WORKER_CHUNK_SIZE`(500) — 收緊迴圈次數上限、R_Low 分塊大小
- `MAX_TOLERANCE`(5) / `MIN_TOLERANCE`(0.00001) — worker 自動放寬的天花板與階梯級距
- `E24_BASE` / `E96_BASE` — 電阻表本體，經 `utils.get_resistor_list()` 展開 7 個倍率

另有一個**不在 config 裡**的寫死上限：`len(r_hi1_rng) * len(r_hi2_rng) > 50_000_000` 直接回 error（[calculation_worker.py:41](calculation_worker.py#L41)）。

---

## 6. 決策與否決紀錄（為什麼是這樣 — 別「順手改回去」）

> LLM 換手失憶最貴的兩種知識：**決策的理由**、**試過但不行的方案**。沒有這節，下一個 agent 會重新提出已經被否決的做法。

| # | 決策 | 理由 ／ 試過不行的替代方案 | 出處 |
|---|---|---|---|
| 1 | Release 用 runner 內建的 `gh release create --generate-notes`，**刻意不用第三方 GitHub Action** | 降低供應鏈風險 | 2026-07-26 §C |
| 2 | `CircuitCanvas._fit_to_content()` 回報的請求高度**一律用「雙電阻模式的自然高度」，不回報拉伸後的高度** | 回報拉伸後高度會讓外層被越撐越大，形成無限重繪迴圈。這是實測踩過的坑；改動此處務必重測重繪次數 | 2026-07-26 §C |
| 3 | `MIN_WINDOW_SIZE` 是**實測寫死值**，不是計算得出 | 左欄控制項自然高度實測 648px，低於此值 About 按鈕會被裁掉。使用者後續依自己環境調為 1680x1000 | 2026-07-26 §C |
| 4 | `.gitignore` 用 `.venv*/` 而非 `.venv/` | 要一併涵蓋 VSCode Python Envs 擴充建立失敗時留下的 `.venv2/`、`.venv-1/` 變體目錄 | 2026-07-29 §C |
| 5 | `bin/VoltMatch.exe`(24MB) 已移出版控，但**沒有 rewrite history** | 檔案仍留在 git 歷史中，只是未來 commit 不再帶它。真正瘦身要 rewrite history，屬架構級決定，**須使用者裁示，目前未執行** | 2026-07-29／2026-08-27 §C |
| 6 | worker 維持 dict-in / queue-out，尚未改成 dataclass／TypedDict | 這是 `LLM_MEMORY.md` §B3 中期目標要重構的對象，**尚未定案**。若動手，本檔 §3 整節必須同步改寫 | §B3 |
| 7 | 本檔不設「每個物件一個 ✅／❌」的驗證欄，改用 §8 台帳 | 物件層級的 ✅ 會給出假的安全感（`fmt_rkm` 測過 `2K2`，不代表 `None`／負數／邊界也測過）。驗證的單位是**行為 × 環境**，不是物件 | 2026-09-03 §C |

---

## 7. 環境現場知識（隱性條件，換機器／換人就會忘）

- **使用者的顯示環境 tk scaling ≈ 2.0**，同一份程式在他機器上左欄自然高度約 792px（而非開發實測的 648px）。任何寫死像素的排版都要考慮這點。
- 使用者已手動調整 `config.py`：`FONTSIZE` 12→10、`WINDOWS_SIZE`／`MIN_WINDOW_SIZE` → 1680x1000。**這些是使用者的偏好值，不要「優化」回去。**
- Git hooks 走 `git config core.hooksPath scripts/hooks`（不是 `.git/hooks`），`.gitattributes` 含 `scripts/hooks/* text eol=lf`。hook 會擋：commit 訊息格式、未同步 `LLM_MEMORY.md`。**不得用 `--no-verify` 繞過。**
- 專案在 Linux 與 Windows 兩種環境下都被開發過；`LLM_MEMORY.md` 是 CRLF，`scripts/hooks/*` 強制 LF。
- Linux 開發機的已知環境事實（2026-07-29 診斷）：`/usr/bin/python3: No module named pip` 是 Ubuntu 拆包 + PEP 668 的**預期行為，不是故障**；VSCode Python Envs 擴充每次會先探測 `uv --version`，沒裝 uv 會退回較慢的 `python -m venv` + pip 路徑（該機已裝 uv 0.12.0 於 `~/.local/bin`）。

---

## 8. 驗證台帳

**全專案無自動化測試**：沒有 `tests/` 目錄，`requirements.txt` 只有 `numpy`、`tksheet`。所有驗證都是手動的。

**未列於本表者一律視為未驗證。** 驗證的單位是「行為 × 環境」，不是物件——所以本表沒有「哪個函式測過了」這種列。

| 驗證了什麼行為 | 環境 | 方法 | 日期／出處 |
|---|---|---|---|
| `RVDSApp` 可正常啟動；重繪收斂（啟動後重繪 2 次，閒置與視窗縮放皆 0 次，無無限迴圈） | Linux + Xvfb | 實際執行 `main.py` | 2026-07-26 §C |
| `CircuitCanvas` 單／雙電阻模式互切後畫布皆 88x200、bbox 完全落在畫布內、底部剩餘 7~9px 無溢出 | Linux + Xvfb | bbox 斷言 + canvas 轉 PostScript 目視 | 2026-07-26 §C |
| `CircuitCanvas` 標籤不被裁切（`fits=True`） | Linux + Xvfb，4 組字型：WenQuanYi 12／Noto Sans CJK TC 16／Helvetica 9／DejaVu Sans 20 | 字型度量斷言 | 2026-07-26 §C |
| `configure_system_settings` 的 Linux 分支（字型／DPI 設定） | Linux + Xvfb | 隨 `RVDSApp` 啟動連帶執行 | 2026-07-26 §C |
| `pre-commit` 能擋下未含 `LLM_MEMORY.md` 的 commit；`commit-msg` 能擋下不符格式的訊息 | Windows／Git Bash | 實際觸發被擋 | 2026-07-06 §C |
| `.github/workflows/package.yml` 語法有效、job 與 artifact 路徑對應正確 | — | PyYAML 解析 + 路徑核對（**非實際執行 Actions**） | 2026-07-26 §C |

### 缺口

- **Windows／macOS 實機：零驗證紀錄。** 所有 UI 驗證都只在 Linux + Xvfb 做過，而 `CircuitCanvas` 與 `configure_system_settings` 正是依作業系統分支的程式碼。這是 `LLM_MEMORY.md` §B2「跨作業系統 UI/UX 相容」的主要風險。
- **`calculation_worker.worker_calculation` 從未被任何形式驗證過** — 包含組合搜尋、自動放寬（階梯倍增）與自動收緊（動態衰減因子）三段核心邏輯。它是全專案唯一的計算來源，卻是驗證覆蓋最薄的地方。
- `utils.py` 六個純函式無任何驗證。

### 若要開始補測試的建議順序

1. `utils.py` — 純函式、零 UI 依賴、最好測
2. `worker_calculation` — 純邏輯，塞一個假 `queue.Queue` 斷言訊息序列即可，不需要 UI
3. UI 元件 — 需要 headless X（比照 2026-07-26 那次 `xvfb-run` 的做法）
