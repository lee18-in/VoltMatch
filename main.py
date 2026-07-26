

# === 1. 作業系統與系統環境相關 (OS / System) ===
import os          # 匯入 os 模組，用於操作系統路徑與環境變數處理

# === 2. Python 內建標準函式庫 (Standard Library) ===
import csv         # 匯入 csv 模組，用於讀寫 CSV 檔案
import traceback   # 匯入 traceback 模組，用於捕捉並列印錯誤堆疊資訊
import threading   # 匯入 threading 模組，用於多執行緒處理 (避免介面卡死)
import queue       # 匯入 queue 模組，用於執行緒間的訊息傳遞

# === 3. Python 內建 GUI 函式庫 (Tkinter) ===
import tkinter as tk               # 匯入 tkinter 模組並別名為 tk，用於建立 GUI 圖形介面
from tkinter import ttk            # 從 tkinter 匯入 ttk 模組，提供更現代化的介面元件
from tkinter import messagebox     # 從 tkinter 匯入 messagebox，用於顯示訊息視窗
from tkinter import filedialog     # 從 tkinter 匯入 filedialog，用於檔案選取對話框

# === 4. 第三方外部套件 (Third-Party Packages, 需 pip install) ===
from tksheet import Sheet          # 從 tksheet 匯入 Sheet，用於顯示試算表格式資料

# =================== [MODULARIZATION] =====================
import config               # 匯入 config 模組，包含常數與設定
import utils                # 匯入 utils 模組，包含工具函數
import ui_components        # 匯入 ui_components 模組，包含自訂的 UI 元件
import calculation_worker   # 匯入 calculation_worker 模組，包含背景計算邏輯
# ==========================================================

# 測試讀取
credits_file = utils.get_resource_path("CREDITS.txt") # 取得 CREDITS.txt 的絕對路徑
if os.path.exists(credits_file): # 檢查該檔案是否存在
    print(f"✅ OK : {credits_file}")  # 請確保此行引號與括號完全閉合 # 若存在則印出成功訊息
# ==============================================================================

# ==============================================================================
# 🖥️ 主程式
# ==============================================================================
class RVDSApp: # 定義主應用程式類別
    def __init__(self, root): # 初始化函數
        self.root = root # 儲存 root 視窗物件
        self.root.title(config.H_TITLE) # 設定視窗標題
        self.root.geometry(config.WINDOWS_SIZE) # 設定視窗大小
        self.root.minsize(*config.MIN_WINDOW_SIZE) # 限制最小視窗大小，避免縮太小時左欄與底部區塊被裁切

        self.app_font = ui_components.configure_system_settings(root) # 設定系統字型
        
        # [Threading] 初始化 Queue
        self.msg_queue = queue.Queue() # 建立訊息佇列

        self.v_ref = tk.DoubleVar(value=config.DEFAULT_V_REF) # 初始化參考電壓變數
        self.v_target = tk.DoubleVar(value=config.DEFAULT_V_TARGET) # 初始化目標電壓變數
        self.tolerance = tk.StringVar(value=config.DEFAULT_TOLERANCE) # 初始化容差變數
        
        # [Non-Linear Scale] 建立滑桿專用的虛擬變數 (0.0 ~ 1.0)
        self.tol_slider_var = tk.DoubleVar() # 初始化滑桿變數
        # 初始化滑桿位置 (反向映射)
        init_s = ((0.5 - config.MIN_TOLERANCE) / (config.MAX_TOLERANCE - config.MIN_TOLERANCE)) ** (1/5) # 計算初始滑桿位置
        self.tol_slider_var.set(init_s) # 設定滑桿位置

        self.var_display_limit = tk.IntVar(value=config.DEFAULT_DISPLAY_LIMIT) # 初始化顯示數量限制變數
        
        # [Non-Linear Scale] 建立顯示限制滑桿專用的虛擬變數 (0.0 ~ 1.0)
        self.limit_slider_var = tk.DoubleVar() # 初始化限制滑桿變數
        init_lim_s = ((config.DEFAULT_DISPLAY_LIMIT - config.DEFAULT_LIMIT_MIN) / (config.DEFAULT_LIMIT_MAX - config.DEFAULT_LIMIT_MIN)) ** (1/5) # 計算初始限制滑桿位置
        self.limit_slider_var.set(init_lim_s) # 設定滑桿位置
        
        self.r_low_mode = tk.StringVar(value=config.DEFAULT_R_LOW_MODE) # 初始化 R_Low 模式變數
        self.r_low_lock_val = tk.DoubleVar(value=config.DEFAULT_R_LOW_LOCK_VAL) # 初始化 R_Low 鎖定值
        self.r_low_min = tk.DoubleVar(value=config.DEFAULT_R_LOW_MIN) # 初始化 R_Low 最小值
        self.r_low_max = tk.DoubleVar(value=config.DEFAULT_R_LOW_MAX) # 初始化 R_Low 最大值
        self.r_low_e24_only = tk.BooleanVar(value=False) # 初始化 R_Low E24 限制變數

        self.r_hi_mode = tk.StringVar(value=config.DEFAULT_R_HI_MODE) # 初始化 R_Hi 模式變數
        self.r_hi_min = tk.DoubleVar(value=config.DEFAULT_R_HI_MIN) # 初始化 R_Hi 最小值
        self.r_hi_max = tk.DoubleVar(value=config.DEFAULT_R_HI_MAX) # 初始化 R_Hi 最大值
        self.r_hi1_e24_only = tk.BooleanVar(value=False) # 初始化 R_Hi1 E24 限制變數
        self.r_hi2_e24_only = tk.BooleanVar(value=False) # 初始化 R_Hi2 E24 限制變數

        # [NoPandas] Change DataFrame to List
        self.data_rows = [] # 初始化資料列列表
        
        self.active_filters = {} # 初始化篩選器狀態
        self.sort_state = {} # 初始化排序狀態
        self.base_headers = config.SHEET_BASE_HEADERS # 定義表格標題
        self.sheet_column_widths = config.SHEET_COLUMN_WIDTHS # 定義緊湊欄寬，避免底部水平捲軸
        self.sheet_index_width = config.SHEET_INDEX_WIDTH # 定義左側行號欄寬

        # 監聽數值變動，確保手動輸入或程式自動放寬時，滑桿也會跟著動
        self.tolerance.trace_add("write", self._sync_slider_from_val) # 綁定容差變動事件
        self.r_hi_mode.trace_add("write", lambda *args: self.circuit_canvas.draw_circuit(self.r_hi_mode.get())) # 監聽模式切換以重繪電路圖 # 綁定 R_Hi 模式變動事件

        # 從 config 載入區塊配色方案
        self.ui_colors = config.UI_COLORS
        self.create_widgets() # 建立介面元件

    def create_widgets(self): # 建立介面元件函數
        left_frame = ttk.Frame(self.root, padding="5") # 建立左側框架
        left_frame.pack(side=tk.LEFT, fill=tk.Y) # 放置左側框架
        right_frame = ttk.Frame(self.root, padding="0") # 建立右側框架
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True) # 放置右側框架

        # ======================   左側：參數區域   ======================
        # 1. Target Voltage (Red)
        lbl_1 = ttk.Label(left_frame, text="1. Target Voltage", font=(self.app_font[0], config.FONTSIZE, "bold"), foreground=self.ui_colors["target"]) # 建立標題標籤
        p_frame = ttk.LabelFrame(left_frame, labelwidget=lbl_1, padding="5") # 建立標籤框架
        p_frame.pack(fill=tk.X, pady=2) # 放置框架
        
        tol_row1 = ttk.Frame(p_frame) # 建立容差列框架
        tol_row1.pack(fill=tk.X, pady=(2, 0)) # 放置框架
        ttk.Label(tol_row1, text="Tolerance (%):", foreground=self.ui_colors["target"]).pack(side=tk.LEFT) # 建立容差標籤
        ttk.Entry(tol_row1, textvariable=self.tolerance, width=1, font=self.app_font).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0)) # 建立容差輸入框
        
        tol_row2 = ttk.Frame(p_frame) # 建立容差滑桿列框架
        tol_row2.pack(fill=tk.X, pady=(2, 5)) # 放置框架

        tol_scale = ttk.Scale( # 建立容差滑桿
            tol_row2, # 父容器
            from_=0.0, # 最小值
            to=1.0, # 最大值
            variable=self.tol_slider_var, # 綁定變數
            orient='horizontal', # 水平方向
            command=self._sync_val_from_slider # 綁定回調函數
        )
        tol_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)) # 放置滑桿
        
        self.create_entry(p_frame, "Target Voltage (V):", self.v_target, text_color=self.ui_colors["target"]) # 建立目標電壓輸入框
        
        # --- Display Limit UI Layout ---
        lim_frame = ttk.Frame(p_frame) # 建立限制列框架
        lim_frame.pack(fill=tk.X, pady=2) # 放置框架
        ttk.Label(lim_frame, text="Max Results:", foreground=self.ui_colors["target"]).pack(side=tk.LEFT) # 建立最大結果標籤

        def on_limit_slider_move(val): # 滑桿移動回調函數 (非線性)
            try: # 嘗試處理
                s = float(val) # 轉為 0.0 ~ 1.0 的浮點數
                raw_val = config.DEFAULT_LIMIT_MIN + (config.DEFAULT_LIMIT_MAX - config.DEFAULT_LIMIT_MIN) * (s ** 5) # 5次方非線性映射
                
                # 根據數量級動態調整刻度 (Snap)
                if raw_val <= 100: snapped_val = int(round(raw_val / 10) * 10)
                elif raw_val <= 1000: snapped_val = int(round(raw_val / 50) * 50)
                elif raw_val <= 10000: snapped_val = int(round(raw_val / 500) * 500)
                else: snapped_val = int(round(raw_val / 5000) * 5000)
                    
                snapped_val = max(config.DEFAULT_LIMIT_MIN, min(config.DEFAULT_LIMIT_MAX, snapped_val))
                if self.var_display_limit.get() != snapped_val: # 若值改變
                    self.var_display_limit.set(snapped_val) # 更新變數
            except: pass # 忽略錯誤

        limit_scale = ttk.Scale( # 建立限制滑桿
            lim_frame, # 父容器
            from_=0.0, # 最小值
            to=1.0, # 最大值
            variable=self.limit_slider_var, # 綁定虛擬變數
            orient='horizontal', # 水平方向
            command=on_limit_slider_move # 綁定回調函數
        )
        limit_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2) # 放置滑桿
        
        ttk.Label(lim_frame, textvariable=self.var_display_limit, width=4, font=self.app_font, anchor="center", foreground=self.ui_colors["target"]).pack(side=tk.LEFT) # 顯示目前限制值
        
        # ==============
        # 2. High Side Resistor (Orange)
        lbl_2 = ttk.Label(left_frame, text="2. High Side Resistor", font=(self.app_font[0], config.FONTSIZE, "bold"), foreground=self.ui_colors["hi"]) # 建立高側電阻標題
        f1_frame = ttk.LabelFrame(left_frame, labelwidget=lbl_2, padding="5") # 建立標籤框架
        f1_frame.pack(fill=tk.X, pady=2) # 放置框架
        
        style = ttk.Style()
        style.configure("Hi.TRadiobutton", foreground=self.ui_colors["hi"])
        style.configure("Hi.TCheckbutton", foreground=self.ui_colors["hi"])

        row_single = ttk.Frame(f1_frame) # 建立單電阻模式列
        row_single.pack(fill=tk.X, anchor="w") # 放置框架
        ttk.Radiobutton(row_single, text="Single (Only R1)", variable=self.r_hi_mode, value="Disable", style="Hi.TRadiobutton").pack(side=tk.LEFT) # 建立單選按鈕
        ttk.Checkbutton(row_single, text="R1: E24 Only", variable=self.r_hi1_e24_only, style="Hi.TCheckbutton").pack(side=tk.LEFT, padx=10) # 建立複選按鈕


        row_dual = ttk.Frame(f1_frame) # 建立雙電阻模式列
        row_dual.pack(fill=tk.X, anchor="w") # 放置框架
        ttk.Radiobutton(row_dual, text="Dual ( R1 + R2 ) ", variable=self.r_hi_mode, value="Unlock", style="Hi.TRadiobutton").pack(side=tk.LEFT) # 建立單選按鈕
        ttk.Checkbutton(row_dual, text="R2: E24 Only", variable=self.r_hi2_e24_only, style="Hi.TCheckbutton").pack(side=tk.LEFT, padx=10) # 建立複選按鈕

        ttk.Separator(f1_frame, orient='horizontal').pack(fill='x', pady=2) # 建立分隔線
        # ==============
        f2_frame = ttk.Frame(left_frame) # 建立參考電壓框架
        f2_frame.pack(fill=tk.X, pady=2) # 放置框架

        # 3. Reference Voltage (Blue)
        ttk.Label(f2_frame, text="3. Reference Voltage (V):", font=(self.app_font[0], self.app_font[1], "bold"), foreground=self.ui_colors["ref"]).pack(side=tk.LEFT) # 建立標籤
        ttk.Entry(f2_frame, textvariable=self.v_ref, width=1, font=self.app_font).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5) # 建立輸入框
        
        # ==============
        # 4. Low Side Resistor (Green)
        lbl_4 = ttk.Label(left_frame, text="4. Low Side Resistor", font=(self.app_font[0], config.FONTSIZE, "bold"), foreground=self.ui_colors["low"]) # 建立低側電阻標題
        f3_frame = ttk.LabelFrame(left_frame, labelwidget=lbl_4, padding="5") # 建立標籤框架
        f3_frame.pack(fill=tk.X, pady=2) # 放置框架
        
        style.configure("Low.TRadiobutton", foreground=self.ui_colors["low"])
        style.configure("Low.TCheckbutton", foreground=self.ui_colors["low"])

        low_sweep_frame = ttk.Frame(f3_frame) # 建立掃描模式列
        low_sweep_frame.pack(fill=tk.X, anchor="w") # 放置框架
        ttk.Radiobutton(low_sweep_frame, text="Sweep", variable=self.r_low_mode, value="Unlock", style="Low.TRadiobutton").pack(side=tk.LEFT) # 建立單選按鈕
        ttk.Checkbutton(low_sweep_frame, text="E24 Only", variable=self.r_low_e24_only, style="Low.TCheckbutton").pack(side=tk.LEFT, padx=10) # 建立複選按鈕
        
        ttk.Separator(f3_frame, orient='horizontal').pack(fill='x', pady=2) # 建立分隔線
        row_locked = ttk.Frame(f3_frame) # 建立固定值模式列
        row_locked.pack(fill=tk.X, anchor="w", pady=2) # 放置框架
        ttk.Radiobutton(row_locked, text="Fixed Value (Ω)", variable=self.r_low_mode, value="Locked", style="Low.TRadiobutton").pack(side=tk.LEFT) # 建立單選按鈕
        ttk.Entry(row_locked, textvariable=self.r_low_lock_val, width=1, font=self.app_font).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5) # 建立輸入框
        # ==============
        
        self.btn_calc = ttk.Button(left_frame, text="5. Calculate", command=self.run_calculation_trigger) # 建立計算按鈕
        self.btn_calc.pack(fill=tk.X, ipady=2, pady=5) # 放置按鈕


        
        self.status_label = ttk.Label(left_frame, text="Ready", foreground="blue", wraplength=200) # 建立狀態標籤
        self.status_label.pack(anchor="w", pady=(10, 0)) # 放置標籤

        self.btn_reset = ttk.Button(left_frame, text="🔄 Reset View", command=self.reset_all_view) # 建立重置視圖按鈕
        self.btn_reset.pack(fill=tk.X, ipady=2, pady=5) # 放置按鈕
        
        btn_export = ttk.Button(left_frame, text="💾 Export CSV", command=self.export_csv) # 建立匯出 CSV 按鈕
        btn_export.pack(fill=tk.X, ipady=2, pady=5) # 放置按鈕
        
        btn_about = ttk.Button(left_frame, text="ℹ️ About", command=self.show_about) # 建立關於按鈕
        btn_about.pack(side=tk.BOTTOM, fill=tk.X, pady=10) # 放置按鈕
        
        # ======================   右側區域 (上下分割)   ======================
        table_container = ttk.Frame(right_frame) # 建立表格容器
        table_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True) # 放置容器

        self.sheet = Sheet(table_container, headers=self.base_headers) # 建立試算表物件
        self.sheet.pack(fill="both", expand=True) # 放置試算表
        self.sheet.font(newfont=self.app_font) # 設定字型
        self.sheet.header_font(newfont=(self.app_font[0], config.FONTSIZE, "bold")) # 設定標題字型
        self.sheet.enable_bindings("single_select", "drag_select", "column_select", "row_select", "column_width_resize", "arrowkeys", "right_click_popup_menu", "rc_select", "copy") # 啟用綁定
        self.sheet.extra_bindings("row_select", self.copy_selected_display_row) # 左鍵點擊行號時複製該列
        self.apply_sheet_column_layout() # 套用緊湊欄寬
        self.sheet.popup_menu_add_command("A>Z Sort Ascending", self.sort_asc_from_cell) # 新增排序指令
        self.sheet.popup_menu_add_command("Z>A Sort Descending", self.sort_desc_from_cell) # 新增排序指令
        self.sheet.popup_menu_add_command("Filter", self.filter_from_cell) # 新增篩選指令
        self.sheet.popup_menu_add_command("Clear Filter", self.clear_filter_from_cell) # 新增清除篩選指令

        # ======================   底部區域：電路圖 + 筆記   ======================
        bottom_area = ttk.Frame(right_frame) # 建立底部區域框架
        bottom_area.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5) # 放置框架

        # 1. Circuit (Left)
        circuit_frame = ttk.LabelFrame(bottom_area, text="Circuit", padding=2) # 建立電路圖框架
        circuit_frame.pack(side=tk.LEFT, padx=(0, 5), anchor="n") # 放置框架 (向上對齊，與 Solver / Notes 齊頭)
        self.circuit_canvas = ui_components.CircuitCanvas(circuit_frame, self.ui_colors, self.app_font, bg="white", highlightthickness=0) # 建立畫布 (尺寸由 draw_circuit 依字型度量自動決定)
        self.circuit_canvas.pack() # 放置畫布
        self.circuit_canvas.draw_circuit(self.r_hi_mode.get()) # 初始繪製 # 呼叫繪製電路圖函數

        # 1.5 Compact Solver (Middle) - 固定寬度，不隨視窗拉伸
        self.compact_solver = ui_components.CompactSolverFrame(bottom_area, self.ui_colors)
        self.compact_solver.pack(side=tk.LEFT, padx=(0, 5), fill="y", expand=False)

        # 2. Notes (Right)
        self.notes_frame = ui_components.NotesFrame(bottom_area, self.app_font, self.save_notes_as)
        self.notes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.notepad = self.notes_frame.text_widget # 保留參照供其他功能使用

    def copy_selected_display_row(self, event=None): # 點擊左側行號時複製該列
        self.root.after_idle(self.sheet.copy) # 使用 tksheet 內建複製，保持與右鍵 Copy 相同格式

    def apply_sheet_column_layout(self): # 套用結果表緊湊欄寬
        try:
            self.sheet.set_options(auto_resize_columns=52) # 視窗變動時保持欄寬貼合，降低水平捲軸機率
        except Exception:
            pass

        try:
            self.sheet.set_index_width(self.sheet_index_width, redraw=False) # 縮小左側行號欄
        except Exception:
            pass

        try:
            self.sheet.set_column_widths(iter(self.sheet_column_widths)) # 設定各欄固定寬度
        except Exception:
            for col_idx, width in enumerate(self.sheet_column_widths):
                try:
                    self.sheet.column_width(column=col_idx, width=int(width))
                except Exception:
                    pass

    def save_notes_as(self): # 另存 Notes 內容
        content = self.notepad.get("1.0", "end-1c") # 取得筆記內容
        if not content.strip(): # 若無內容
            messagebox.showinfo("Info", "No notes to save.") # 顯示訊息
            return # 返回

        file_type_var = tk.StringVar(value="Text Files") # 追蹤另存對話框選擇的檔案類型
        filename = filedialog.asksaveasfilename( # 開啟另存對話框
            defaultextension="", # 由下方檔案類型決定副檔名，避免切換 CSV 時欄位仍顯示 .txt
            initialfile="VoltMatch_Notes", # 預設檔名不預先帶副檔名
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")], # 檔案類型
            typevariable=file_type_var, # 取得使用者選擇的檔案類型
            title="Save Notes" # 標題
        )

        if not filename: return # 若取消則返回

        try:
            selected_type = file_type_var.get().lower() # 取得選擇的檔案類型
            ext = os.path.splitext(filename)[1].lower() # 取得副檔名
            if "csv" in selected_type and ext != ".csv": # 若選 CSV 但檔名仍是 .txt 或沒有副檔名
                filename = os.path.splitext(filename)[0] + ".csv" # 自動改成 .csv
            elif ext == "" and ("text" in selected_type or "txt" in selected_type): # 若選 TXT 且沒有副檔名
                filename += ".txt" # 自動補 .txt

            ext = os.path.splitext(filename)[1].lower() # 取得副檔名
            if ext == ".csv": # 若選擇 CSV
                with open(filename, "w", newline="", encoding="utf-8-sig") as f: # 開啟 CSV 檔案
                    writer = csv.writer(f) # 建立 CSV 寫入器
                    for line in content.splitlines(): # 逐行處理
                        writer.writerow(line.split("\t")) # 將 tab 分隔內容轉成 CSV 欄位
            else:
                with open(filename, "w", encoding="utf-8") as f: # 開啟文字檔
                    f.write(content) # 寫入原始文字

            messagebox.showinfo("Success", f"Saved to {filename}") # 顯示成功訊息
        except Exception as e:
            messagebox.showerror("Save Error", str(e)) # 顯示錯誤訊息

    def _sync_val_from_slider(self, val): # 滑桿同步數值函數
        """ 當滑桿移動時：使用 5 次方映射計算實際容差 (極度放大左側解析度) """ # 函數說明
        try: # 嘗試執行
            s = float(val) # 轉為浮點數
            # 公式：Val = Min + (Max - Min) * s^5
            new_tol = config.MIN_TOLERANCE + (config.MAX_TOLERANCE - config.MIN_TOLERANCE) * (s ** 5) # 計算新的容差值
            
            try: current_val = float(self.tolerance.get()) # 嘗試取得目前容差值
            except: current_val = 0.0 # 若失敗則設為 0
            
            if abs(current_val - new_tol) > 1e-7: # 若差異夠大
                # [Format] 強制格式化為小數點字串，避免科學記號 (1e-05)
                self.tolerance.set(f"{new_tol:.6f}".rstrip('0').rstrip('.')) # 更新容差變數
        except: pass # 忽略錯誤

    def _sync_slider_from_val(self, *args): # 數值同步滑桿函數
        """ 當數值變動時 (手動輸入或程式調整)：反向更新滑桿位置 """ # 函數說明
        try: # 嘗試執行
            val = float(self.tolerance.get()) # 取得目前容差值
            val = max(config.MIN_TOLERANCE, min(config.MAX_TOLERANCE, val)) # 限制範圍
            # 反公式：s = ((Val - Min) / (Max - Min))^(1/5)
            new_s = ((val - config.MIN_TOLERANCE) / (config.MAX_TOLERANCE - config.MIN_TOLERANCE)) ** (1/5) # 計算新的滑桿位置
            if abs(self.tol_slider_var.get() - new_s) > 1e-4: # 若差異夠大
                self.tol_slider_var.set(new_s) # 更新滑桿變數
        except: pass # 忽略錯誤

    def create_entry(self, parent, label_text, variable, text_color=None): # 建立輸入框輔助函數
        f = ttk.Frame(parent) # 建立框架
        f.pack(fill=tk.X, pady=2) # 放置框架
        lbl = ttk.Label(f, text=label_text) # 建立標籤
        if text_color: lbl.configure(foreground=text_color) # 設定顏色
        lbl.pack(side=tk.LEFT) # 放置標籤
        ttk.Entry(f, textvariable=variable, width=1, font=self.app_font).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5) # 建立輸入框

    def validate_input(self, tk_var, min_val, max_val): # 輸入驗證函數
        try: # 嘗試執行
            val = float(tk_var.get()) # 轉為浮點數
            if val < min_val: # 若小於最小值
                tk_var.set(f"{min_val:.6f}".rstrip('0').rstrip('.')) # 設定為最小值
                return min_val # 回傳最小值
            elif val > max_val: # 若大於最大值
                tk_var.set(f"{max_val:.6f}".rstrip('0').rstrip('.')) # 設定為最大值
                return max_val # 回傳最大值
            return val # 回傳數值
        except (ValueError, TypeError): # 若轉換失敗
            tk_var.set(f"{min_val:.6f}".rstrip('0').rstrip('.')) # 設定為最小值
            return min_val # 回傳最小值

    # ==============================================================================
    # 🚀 計算主流程 (Threading Enabled + No Pandas)
    # ==============================================================================
    def run_calculation_trigger(self): # 觸發計算函數
        """ 主執行緒：收集參數、鎖定 UI、啟動子執行緒 """ # 函數說明
        
        # [NEW] Sync main inputs to Reverse Calc panel
        try:
            v_target_val = self.v_target.get()
            v_ref_val = self.v_ref.get()
            
            # 檢查 R_Low 是否為固定模式
            is_r_low_locked = (self.r_low_mode.get() == "Locked")

            # 1. 判斷是否需要切換鎖定目標到 R_Hi
            # 條件：目前鎖定的是電壓 (V_Out, V_Ref) 或者 (R_Low 且 R_Low 在主介面被固定)
            current_target = self.compact_solver.target_mode.get()
            if current_target in ["vout", "vfb"] or (is_r_low_locked and current_target == "low"):
                self.compact_solver.target_mode.set("hi")
                self.compact_solver.update_ui_state() # 更新 UI 鎖定狀態
            
            # 2. 將主介面的電壓值填入 Reverse Calc 工具中
            self.compact_solver.sv_vout.set(f"{v_target_val:.6g}")
            self.compact_solver.sv_vfb.set(f"{v_ref_val:.6g}")
            
            # 3. 如果 R_Low 是固定值，也同步填入
            if is_r_low_locked:
                self.compact_solver.sv_low.set(f"{self.r_low_lock_val.get():.6g}")
        except Exception:
            pass # 若同步失敗，不影響主計算流程
        
        self.btn_calc.configure(state="disabled") # 停用計算按鈕
        self.btn_reset.configure(state="disabled") # 停用重置按鈕
        self.status_label.config(text="Calculating...", foreground="blue") # 更新狀態標籤
        
        try: # 嘗試執行
            display_limit = self.var_display_limit.get() # 取得顯示限制
            
            current_tol = self.validate_input(self.tolerance, config.MIN_TOLERANCE, config.MAX_TOLERANCE) # 驗證並取得容差
            self.validate_input(self.r_low_min, 1, 1e7) # 驗證 R_Low 最小值
            self.validate_input(self.r_low_max, 1, 1e7) # 驗證 R_Low 最大值
            
            v_ref = self.v_ref.get() # 取得參考電壓
            v_target = self.v_target.get() # 取得目標電壓
            
            if v_target < v_ref: # 若目標電壓小於參考電壓
                raise ValueError("Target Voltage must be greater than or equal to V_Ref.") # 拋出錯誤

            params = { # 建立參數字典
                'v_ref': v_ref, # 參考電壓
                'v_target': v_target, # 目標電壓
                'tol': current_tol, # 容差
                'limit': display_limit, # 顯示限制
                'r_low_mode': self.r_low_mode.get(), # R_Low 模式
                'r_low_lock': self.r_low_lock_val.get(), # R_Low 鎖定值
                'r_low_min': self.r_low_min.get(), # R_Low 最小值
                'r_low_max': self.r_low_max.get(), # R_Low 最大值
                'r_low_e24': self.r_low_e24_only.get(), # R_Low E24 限制
                'r_hi_mode': self.r_hi_mode.get(), # R_Hi 模式
                'r_hi_min': self.r_hi_min.get(), # R_Hi 最小值
                'r_hi_max': self.r_hi_max.get(), # R_Hi 最大值
                'r_hi1_e24': self.r_hi1_e24_only.get(), # R_Hi1 E24 限制
                'r_hi2_e24': self.r_hi2_e24_only.get() # R_Hi2 E24 限制
            }
            
            t = threading.Thread(target=calculation_worker.worker_calculation, args=(params, self.msg_queue)) # 建立執行緒
            t.daemon = True # 設定為守護執行緒
            t.start() # 啟動執行緒
            
            self.root.after(100, self.check_queue) # 設定定時檢查佇列
            
        except Exception as e: # 捕捉例外
            self.btn_calc.configure(state="normal") # 啟用計算按鈕
            self.btn_reset.configure(state="normal") # 啟用重置按鈕
            messagebox.showerror("Input Error", str(e)) # 顯示錯誤訊息

    def check_queue(self): # 檢查佇列函數
        """ 主執行緒：監聽 Queue 並更新 UI (含滑塊動畫) """ # 函數說明
        try: # 嘗試執行
            while True: # 迴圈檢查
                msg_type, data = self.msg_queue.get_nowait() # 取得訊息
                
                if msg_type == "status": # 若為狀態訊息
                    self.status_label.config(text=data[0], foreground=data[1]) # 更新狀態標籤
                
                elif msg_type == "update_tol": # [ROMANCE] 接收核心指令，移動滑塊 # 若為更新容差訊息
                    self.tolerance.set(f"{data:.6f}".rstrip('0').rstrip('.'))   # 這行代碼會讓滑塊在螢幕上跳動 # 更新容差變數
                
                elif msg_type == "error": # 若為錯誤訊息
                    messagebox.showerror("Error", data) # 顯示錯誤視窗
                    self.btn_calc.configure(state="normal") # 啟用計算按鈕
                    self.btn_reset.configure(state="normal") # 啟用重置按鈕
                    return # 結束函數
                
                elif msg_type == "success": # 若為成功訊息
                    self.data_rows = data[0] # 儲存資料列
                    final_tol = data[1] # 儲存最終容差
                    
                    # 確保最後顯示的數值與滑塊一致
                    try: current_val = float(self.tolerance.get()) # 嘗試取得目前容差
                    except: current_val = 0.0 # 若失敗則設為 0
                    
                    if abs(final_tol - current_val) > 1e-7: # 若差異夠大
                        self.tolerance.set(f"{final_tol:.6f}".rstrip('0').rstrip('.')) # 更新容差變數
                    
                    self.preprocess_display_data(final_tol) # 預處理顯示資料
                    self.reset_all_view() # 重置視圖
                    
                    self.status_label.config(text=f"Calculation complete. Found {len(self.data_rows)} results.", foreground="green") # 更新狀態標籤
                    self.btn_calc.configure(state="normal") # 啟用計算按鈕
                    self.btn_reset.configure(state="normal") # 啟用重置按鈕
                    return # 結束函數

        except queue.Empty: # 若佇列為空
            # 頻率設為 20ms，讓滑塊的移動看起來更即時、更滑順
            self.root.after(20, self.check_queue) # 設定 20ms 後再次檢查

    def preprocess_display_data(self, limit_val): # 預處理顯示資料函數
        # Add display strings and colors to the list of dicts
        if not self.data_rows: return # 若無資料則返回
        
        def _cnt_color(c): # 內部函數：決定 E24 計數顏色
            return config.C_GREEN if c==3 else (config.C_YELLOW if c==2 else (config.C_RED if c==1 else config.C_PURPLE)) # 根據數量回傳顏色

        for row in self.data_rows: # 遍歷所有資料列
            row['R_Low_Str'] = utils.fmt_rkm(row['R_Low']) # 格式化 R_Low
            row['R_Hi1_Str'] = utils.fmt_rkm(row['R_Hi1']) # 格式化 R_Hi1
            row['R_Hi2_Str'] = utils.fmt_rkm(row['R_Hi2']) # 格式化 R_Hi2
            row['Vout_Str'] = f"{row['Vout']:.6f}V  " # 格式化輸出電壓
            row['V_Dev_Str'] = f"{row['V_Dev']:.6f}%  " # 格式化誤差
            row['E24_Count_Str'] = str(row['E24_Count']) # 格式化 E24 計數
            
            row['Color_R_Low'] = utils.determine_r_color(row['R_Low']) # 決定 R_Low 顏色
            row['Color_R_Hi1'] = utils.determine_r_color(row['R_Hi1']) # 決定 R_Hi1 顏色
            row['Color_R_Hi2'] = utils.determine_r_color(row['R_Hi2']) # 決定 R_Hi2 顏色
            row['Color_E24'] = _cnt_color(row['E24_Count']) # 決定 E24 計數顏色
            
            ratio = row['V_Dev'] / limit_val if limit_val != 0 else 0 # 計算誤差比例
            row['Color_V_Dev'] = utils.calc_gradient_hex(ratio) # 計算誤差顏色

    def update_sheet_display(self): # 更新表格顯示函數
        if not self.data_rows: # 若無資料
            self.sheet.set_sheet_data([]) # 清空表格
            return # 返回
        
        # Filter Logic (List Comprehension)
        col_map = {0: 'R_Low_Str', 1: 'R_Hi1_Str', 2: 'R_Hi2_Str', 3: 'Vout_Str', 4: 'V_Dev_Str', 5: 'E24_Count_Str'} # 定義欄位映射
        
        filtered_rows = self.data_rows # 取得原始資料
        for col_idx, allowed in self.active_filters.items(): # 遍歷篩選器
            if col_idx in col_map: # 若欄位在映射中
                col_key = col_map[col_idx] # 取得鍵值
                filtered_rows = [r for r in filtered_rows if r[col_key] in allowed] # 篩選資料
        
        limit = self.var_display_limit.get() # 取得顯示限制
        display_rows = filtered_rows[:limit] # 截斷資料

        # Extract data for sheet
        data = [[r['R_Low_Str'], r['R_Hi1_Str'], r['R_Hi2_Str'], r['Vout_Str'], r['V_Dev_Str'], r['E24_Count_Str']] for r in display_rows] # 提取顯示資料
        self.sheet.set_sheet_data(data) # 設定表格資料
        self.apply_sheet_column_layout() # 重新套用緊湊欄寬
        self.sheet.dehighlight_all() # 清除所有高亮

        # Apply Highlighting
        for i, r in enumerate(display_rows): # 遍歷顯示資料
            self.sheet.highlight_cells(row=i, column=0, bg=r['Color_R_Low'], redraw=False) # 高亮 R_Low
            self.sheet.highlight_cells(row=i, column=1, bg=r['Color_R_Hi1'], redraw=False) # 高亮 R_Hi1
            self.sheet.highlight_cells(row=i, column=2, bg=r['Color_R_Hi2'], redraw=False) # 高亮 R_Hi2
            
            c_v = r['Color_V_Dev'] # 取得誤差顏色
            self.sheet.highlight_cells(row=i, column=3, bg=c_v, redraw=False) # 高亮輸出電壓
            self.sheet.highlight_cells(row=i, column=4, bg=c_v, redraw=False) # 高亮誤差
            
            self.sheet.highlight_cells(row=i, column=5, bg=r['Color_E24'], redraw=False) # 高亮 E24 計數

        self.update_headers_visual() # 更新標題視覺效果
        self.sheet.redraw() # 重繪表格

    def update_headers_visual(self): # 更新標題視覺效果函數
        new_headers = [] # 初始化新標題列表
        for i, h in enumerate(self.base_headers): # 遍歷基礎標題
            final_text = h # 初始文字
            if i in self.active_filters: final_text += " 🌪️" # 若有篩選則加入圖示
            if i in self.sort_state: # 若有排序
                arrow = "▼" if self.sort_state[i] == 'desc' else "▲" # 決定箭頭方向
                final_text += f" {arrow}" # 加入箭頭
            new_headers.append(final_text) # 加入新標題
        self.sheet.headers(new_headers) # 設定表格標題

    def perform_sort(self, col_idx): # 執行排序函數
        col_map_real = {0: 'R_Low', 1: 'R_Hi1', 2: 'R_Hi2', 3: 'Vout', 4: 'V_Dev', 5: 'E24_Count'} # 定義欄位映射
        if col_idx not in col_map_real: return # 若欄位無效則返回

        col_name = col_map_real[col_idx] # 取得欄位名稱
        current_order = self.sort_state.get(col_idx, None) # 取得目前排序狀態
        new_order = 'asc' if current_order != 'asc' else 'desc' # 切換排序順序
        self.sort_state = {col_idx: new_order} # 更新排序狀態
        
        # Sort List of Dicts
        is_reverse = (new_order == 'desc') # 決定是否反向
        self.data_rows.sort(key=lambda x: x[col_name], reverse=is_reverse) # 排序資料
        
        self.update_sheet_display() # 更新表格顯示

    def manual_sort(self, col_idx, order): # 手動排序函數
        self.sort_state[col_idx] = 'desc' if order == 'asc' else 'asc' # 更新排序狀態
        self.perform_sort(col_idx) # 執行排序

    def get_selected_col(self): # 取得選取欄位函數
        selection = self.sheet.get_currently_selected() # 取得目前選取
        if selection: return selection[1] # 回傳欄位索引
        return None # 若無選取則回傳 None

    def filter_from_cell(self, *args): # 從儲存格篩選函數
        col_idx = self.get_selected_col() # 取得選取欄位
        if col_idx is not None: # 若有選取
            col_name = self.base_headers[col_idx] # 取得欄位名稱
            if col_name in ["V_Out", "Dev %"]: return # 若為不可篩選欄位則返回
            self.open_filter_popup(col_idx) # 開啟篩選視窗
    def sort_asc_from_cell(self, *args): # 從儲存格升冪排序函數
        col_idx = self.get_selected_col() # 取得選取欄位
        if col_idx is not None: self.manual_sort(col_idx, 'asc') # 執行排序
    def sort_desc_from_cell(self, *args): # 從儲存格降冪排序函數
        col_idx = self.get_selected_col() # 取得選取欄位
        if col_idx is not None: self.manual_sort(col_idx, 'desc') # 執行排序
    def clear_filter_from_cell(self, *args): # 從儲存格清除篩選函數
        col_idx = self.get_selected_col() # 取得選取欄位
        if col_idx is not None: self.clear_filter(col_idx) # 清除篩選

    def open_filter_popup(self, col_idx): # 開啟篩選視窗函數
        col_map = {0: 'R_Low_Str', 1: 'R_Hi1_Str', 2: 'R_Hi2_Str', 3: 'Vout_Str', 4: 'V_Dev_Str', 5: 'E24_Count_Str'} # 定義欄位映射
        if col_idx not in col_map: return # 若欄位無效則返回
        
        col_key = col_map[col_idx] # 取得鍵值
        col_name = self.base_headers[col_idx] # 取得欄位名稱
        
        # Get Unique Values from List of Dicts # 註解
        unique_vals = list(set(r[col_key] for r in self.data_rows)) # 取得唯一值列表
        
        current = self.active_filters.get(col_idx, None) # 取得目前篩選狀態
        ui_components.FilterWindow(self.root, col_name, unique_vals, current, lambda res: self.set_filter(col_idx, res), self.app_font) # 開啟篩選視窗

    def set_filter(self, col_idx, vals): # 設定篩選函數
        self.active_filters[col_idx] = vals # 更新篩選狀態
        self.update_sheet_display() # 更新表格顯示

    def clear_filter(self, col_idx): # 清除篩選函數
        if col_idx in self.active_filters: del self.active_filters[col_idx] # 移除篩選狀態
        self.update_sheet_display() # 更新表格顯示

    def reset_all_view(self): # 重置所有視圖函數
        self.active_filters = {} # 清空篩選狀態
        self.sort_state = {4: 'asc'} # 重置排序狀態
        if self.data_rows: # 若有資料
            self.data_rows.sort(key=lambda x: x['V_Dev']) # 依誤差排序
        self.update_sheet_display() # 更新表格顯示

    def export_csv(self): # 匯出 CSV 函數
        if not self.data_rows: # 若無資料
            messagebox.showinfo("Info", "No data to export.") # 顯示訊息
            return # 返回
        
        # 產生具備描述性的預設檔名 (例如: VoltMatch_Target_81.92V_Tol_0.5.csv)
        try: # 嘗試執行
            v_t = self.v_target.get() # 取得目標電壓
            v_f = self.v_ref.get() # 取得參考電壓
            tol = self.tolerance.get() # 取得容差
            n_len = len(self.data_rows) # 取得資料筆數
            default_name = f"Vo={v_t}_Vfb={v_f}_n={n_len}_Tol={tol}.csv" # 產生檔名
        except: # 若發生錯誤
            default_name = "VoltMatch_Result.csv" # 使用預設檔名

        filename = filedialog.asksaveasfilename( # 開啟存檔對話框
            defaultextension=".csv", # 預設副檔名
            initialfile=default_name, # 預設檔名
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")], # 檔案類型
            title="Export Results" # 標題
        )
        
        if not filename: return # 若取消則返回
        
        try: # 嘗試寫入
            # 定義要匯出的欄位 (使用原始數值而非格式化後的字串，方便後續分析)
            fields = ["R_Low", "R_Hi1", "R_Hi2", "Vout", "V_Dev", "E24_Count"] # 定義欄位
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f: # 開啟檔案
                writer = csv.DictWriter(f, fieldnames=fields) # 建立寫入物件
                writer.writeheader() # 寫入標題
                for row in self.data_rows: # 遍歷資料
                    # 過濾出需要的欄位
                    export_row = {k: row[k] for k in fields if k in row} # 建立匯出列
                    writer.writerow(export_row) # 寫入列
            
            messagebox.showinfo("Success", f"Saved to {filename}") # 顯示成功訊息
        except Exception as e: # 捕捉例外
            messagebox.showerror("Export Error", str(e)) # 顯示錯誤訊息

    def show_about(self): # 顯示關於視窗函數
        try: # 嘗試執行
            credits_path = utils.get_resource_path("CREDITS.txt") # 取得 CREDITS.txt 路徑
            if os.path.exists(credits_path): # 若檔案存在
                with open(credits_path, "r", encoding="utf-8") as f: content = f.read() # 讀取內容
            else: content = "CREDITS.txt not found." # 否則顯示未找到
        except: content = "Error reading credits." # 若發生錯誤顯示讀取錯誤
        
        top = tk.Toplevel(self.root) # 建立頂層視窗
        top.title("About / Credits") # 設定標題
        top.geometry("600x500") # 設定大小
        txt = tk.Text(top, wrap="word", font=("Consolas", 10)) # 建立文字區域
        txt.pack(fill="both", expand=True) # 放置文字區域
        txt.insert("1.0", content) # 插入內容
        txt.config(state="disabled") # 設定為唯讀

if __name__ == "__main__": # 程式進入點
    try: # 嘗試執行
        root = tk.Tk() # 建立主視窗ㄇ
        app = RVDSApp(root) # 建立應用程式物件
        root.mainloop() # 進入主迴圈
    except Exception as e: # 捕捉例外
        traceback.print_exc() # 印出堆疊
        print(f"Critical Error: {e}") # 印出嚴重錯誤
