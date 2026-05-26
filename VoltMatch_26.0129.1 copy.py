# -*- coding: utf-8 -*-
# TO AI : Please do not remove any header comment sections 檔頭備註： 請不要刪除任何表頭註解部分
# 這個算法目的是算除所有可能性，而不是找最佳解，故在大範圍下可能運算時間較長。
# 這個算法目的是算除所有可能性，而不是找最佳解，故排除算法更進一步的優化，例如二分搜尋等，是此程式憲法等級的限制。
# 若我要求 幫忙設計審查，先列出可優化的項目 我們逐項討論。
# CREDITS.txt 這專案資料夾有 打包時請一併放入


import os # 匯入 os 模組，用於操作系統路徑與環境變數處理
import sys # 匯入 sys 模組，用於取得系統參數與執行環境資訊
import tkinter as tk # 匯入 tkinter 模組並別名為 tk，用於建立 GUI 圖形介面
from tkinter import ttk # 從 tkinter 匯入 ttk 模組，提供更現代化的介面元件
from tkinter import messagebox # 從 tkinter 匯入 messagebox，用於顯示訊息視窗
from tkinter import filedialog # 從 tkinter 匯入 filedialog，用於檔案選取對話框
import csv # 匯入 csv 模組，用於讀寫 CSV 檔案
import numpy as np # 匯入 numpy 模組並別名為 np，用於高效能數值運算
from tksheet import Sheet # 從 tksheet 匯入 Sheet，用於顯示試算表格式資料
import platform # 匯入 platform 模組，用於偵測作業系統資訊
import math # 匯入 math 模組，用於數學運算 (如 log, floor 等)
import traceback # 匯入 traceback 模組，用於捕捉並列印錯誤堆疊資訊
import threading # 匯入 threading 模組，用於多執行緒處理 (避免介面卡死)
import queue # 匯入 queue 模組，用於執行緒間的訊息傳遞
import time # 匯入 time 模組，用於時間延遲與計時

# ==============================================================================
def get_resource_path(relative_path):# ======= """ 取得資源檔案的絕對路徑，相容開發與打包環境 """ # 定義函數：取得資源檔案的絕對路徑
    if getattr(sys, 'frozen', False) or "__compiled__" in globals(): # 檢查是否為 Nuitka 打包後的執行環境
        # Nuitka 編譯後的環境，檔案通常與執行檔同級或在封裝內 # 註解：說明 Nuitka 環境下的路徑處理
        base_path = os.path.dirname(os.path.abspath(sys.argv[0])) # 取得執行檔所在的目錄路徑
    else: # 若為一般 Python 開發環境
        # 一般開發環境 # 註解：說明開發環境下的路徑處理
        base_path = os.path.dirname(os.path.abspath(__file__)) # 取得目前腳本檔案所在的目錄路徑
    
    return os.path.join(base_path, relative_path) # 回傳組合後的完整絕對路徑

# 測試讀取
credits_file = get_resource_path("CREDITS.txt") # 取得 CREDITS.txt 的絕對路徑
if os.path.exists(credits_file): # 檢查該檔案是否存在
    print(f"✅ OK : {credits_file}")  # 請確保此行引號與括號完全閉合 # 若存在則印出成功訊息
# ==============================================================================

# 顏色常數 (背景色)
c_green = "#C0FFC0"     # Light Green # 定義淺綠色代碼
c_yellow = "#FFFFC0"    # Light Yellow # 定義淺黃色代碼
c_red = "#FFC0C0"       # Light Red # 定義淺紅色代碼
c_purple = "#FFC0FF"    # Light Purple # 定義淺紫色代碼
fontsize = 12             # 預設字型大小 # 定義全域預設字型大小

# 全域常數
PRECISION_DIGITS = 4    # [NEW] 精度設定：用於浮點數比對的位數，忽略極小誤差 # 設定數值運算的精度位數

H_title = "VoltMatch - Voltage Divider Optimizer - by lee18.in - Ver. 26.0129.1" # Update Ver YY.MMDD.x # 設定視窗標題字串
MAX_TOLERANCE = 5       # 最大容差限制 % # 設定最大允許容差百分比
MIN_TOLERANCE = 0.00001  # 最小容差限制 % # 設定最小允許容差百分比
Windows_Size = "1100x720" # 主視窗 # 設定主視窗的預設尺寸

# 標準電阻表
E96_BASE = [ # 定義 E96 系列標準電阻基值列表
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 
    1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 
    1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 
    2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 
    3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 
    5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76, 0
]
E24_BASE = [ # 定義 E24 系列標準電阻基值列表
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1, 0
]


# ==============================================================================
def configure_system_settings(root):    # """ 系統相容性設定  根據作業系統設定字型與樣式 """ # 定義函數：設定系統相容性與字型
    system_os = platform.system()   # 獲取作業系統類型 # 取得目前的作業系統名稱
    default_font = ("Helvetica", fontsize, "normal")    # 預設字型 # 設定預設字型為 Helvetica

    if system_os == "Windows":  # Windows 特殊處理 DPI 問題 # 如果是 Windows 系統
        try: # 嘗試執行
            from ctypes import windll   # 引入 windll 模組 # 匯入 windll 以呼叫 Windows API
            windll.shcore.SetProcessDpiAwareness(1) # 設定 DPI 覺察 # 設定程式感知 DPI，避免在高解析度螢幕模糊
            default_font = ("Microsoft JhengHei", fontsize, "normal")   # 微軟正黑體 # 設定 Windows 下的預設字型為微軟正黑體
        except Exception: # 捕捉例外
            print("DPI Awareness set failed, utilizing default settings.")  # 錯誤處理 # 若設定失敗則印出訊息
    elif system_os == "Darwin": # macOS 特殊字型設定 # 如果是 macOS 系統
        default_font = ("PingFang TC", fontsize, "normal") # 蘋方體 # 設定 macOS 下的預設字型為蘋方體
    elif system_os == "Linux":  # Linux 嘗試多種字型 # 如果是 Linux 系統
        fonts = ["WenQuanYi Micro Hei", "Noto Sans CJK TC", "Droid Sans Fallback"]  # 常見中文字型 # 定義 Linux 常見中文字型列表
        default_font = (fonts[0], fontsize, "normal")   # 預設為第一個 # 設定 Linux 下的預設字型

    style = ttk.Style()  # 設定樣式 # 建立 ttk 樣式物件
    style.theme_use('clam') # 使用 clam 主題以獲得更好外觀 # 設定主題為 'clam'
    style.configure("TEntry", font=(default_font[0], fontsize, "bold")) # 輸入框字型 # 設定輸入框樣式
    style.configure("Treeview.Heading", font=(default_font[0], fontsize, "bold"))   # 樹狀標題字型 # 設定樹狀圖標題樣式
    style.configure("TLabel", font=default_font)    # 標籤字型 # 設定標籤樣式
    style.configure("TButton", font=default_font)   # 按鈕字型 # 設定按鈕樣式
    style.configure("TLabelframe.Label", font=(default_font[0], fontsize, "bold"))  # 標籤框標題字型 # 設定標籤框標題樣式
    style.configure("TRadiobutton", font=default_font)  # 單選按鈕字型 # 設定單選按鈕樣式
    style.configure("Big.TCheckbutton", font=(default_font[0], fontsize, "normal")) # 複選按鈕字型 # 設定複選按鈕樣式
    
    return default_font # 回傳設定好的字型 # 回傳字型設定

# ==============================================================================
def get_resistor_list(base_values, include_zero=True): # """  核心運算邏輯  產生完整電阻值清單 """ # 定義函數：根據基值產生完整電阻列表
    multipliers = [1, 10, 100, 1000, 10000, 100000, 1000000]    # 1Ω 到 1MΩ # 定義倍率列表
    vals = [b * m for m in multipliers for b in base_values]    # 產生所有組合 # 計算所有可能的電阻值
    if include_zero: vals.append(0.0)                               # 包含 0Ω # 如果需要，加入 0 歐姆
    arr = np.array(vals, dtype=float)                               # 轉為 numpy 陣列 # 將列表轉換為 NumPy 陣列
    arr = np.round(arr, PRECISION_DIGITS)                           # 四捨五入以避免浮點誤差 # 對數值進行四捨五入
    return np.unique(arr)                                           # 移除重複值並回傳排序後的陣列 # 回傳去重並排序後的陣列


def generate_sig_figs(base_list): # """ 產生標準電阻的有效數字集合 (乘以100後取整數) """ # 定義函數：產生有效數字集合
    return set(int(round(x * 100)) for x in base_list)  # 乘以100取整數並轉為集合 # 回傳處理後的有效數字集合

E24_SIGS = generate_sig_figs(E24_BASE)  # 標準 E24 有效數字集合 # 產生 E24 的有效數字集合
E96_SIGS = generate_sig_figs(E96_BASE)  # 標準 E96 有效數字集合 # 產生 E96 的有效數字集合


def fmt_rkm(val):  #       """ 將數值格式化為 R/K/M (BS 1852) """ # 定義函數：將數值格式化為 R/K/M 格式
    if val is None: return ""   # 若值為 None 則回傳空字串
    try: # 嘗試轉換
        val = float(val) # 將輸入轉為浮點數
        if val == 0: return "0R" # 若為 0 則回傳 "0R"
    except (ValueError, TypeError): # 若轉換失敗
        return str(val) # 直接回傳字串形式
    try: # 嘗試格式化
        if val >= 1_000_000: unit, num = 'M', val / 1_000_000 # 若大於 1M，單位設為 M
        elif val >= 1_000:   unit, num = 'K', val / 1_000 # 若大於 1K，單位設為 K
        else:                unit, num = 'R', val # 否則單位設為 R

        s = f"{float(f'{num:.4g}')}" # 格式化數值，保留 4 位有效數字
        if s.endswith(".0"): return s[:-2] + unit # 若以 .0 結尾，移除並加上單位
        elif "." in s: return s.replace(".", unit) # 若有小數點，將小數點替換為單位
        else: return s + unit # 否則直接加上單位
    except Exception: # 若發生其他錯誤
        return str(val) # 回傳原始數值的字串形式


# ==============================================================================
# 🔍 篩選視窗
# ==============================================================================
class FilterWindow(tk.Toplevel): # 定義篩選視窗類別，繼承自 Toplevel
    def __init__(self, parent, col_name, unique_values, current_filter, callback, font_style): # 初始化函數
        super().__init__(parent) # 呼叫父類別初始化
        self.title(f"Filter: {col_name}") # 設定視窗標題
        
        screen_height = self.winfo_screenheight() # 取得螢幕高度
        win_height = min(600, int(screen_height * 0.8)) # 計算視窗高度，不超過螢幕 80%
        self.geometry(f"250x{win_height}") # 設定視窗大小
        
        self.callback = callback # 儲存回調函數
        self.result = current_filter if current_filter is not None else set(unique_values) # 設定目前的篩選結果
        self.font_style = font_style # 儲存字型樣式
        
        display_limit = 1000 # [FIX] 定義顯示限制，避免未定義變數錯誤
        if len(unique_values) > display_limit: # 檢查是否超過顯示限制 (注意：display_limit 在此處未定義，可能會報錯，除非是全域變數)
            messagebox.showwarning("Display Limit", f"[{col_name}] Too much data; only the first {display_limit} records are displayed.") # 顯示警告
            unique_values = unique_values[:display_limit] # 截斷資料

        try: # 嘗試排序
            def sort_key(x): # 定義排序鍵值函數
                s = str(x).upper() # 轉為大寫字串
                mult = 1 # 初始化倍率
                if 'M' in s: mult = 1_000_000; s = s.replace('M','') # 處理 M 單位
                elif 'K' in s: mult = 1_000; s = s.replace('K','') # 處理 K 單位
                elif 'R' in s: mult = 1; s = s.replace('R','') # 處理 R 單位
                try: return float(s) * mult # 嘗試轉為浮點數並乘上倍率
                except (ValueError, TypeError): return s # 若失敗則回傳原字串
            self.all_values = sorted(list(unique_values), key=sort_key) # 進行排序
        except Exception: # 若排序失敗
            self.all_values = sorted(list(unique_values), key=lambda x: str(x)) # 改用字串排序
        
        main_frame = ttk.Frame(self, padding=10) # 建立主框架
        main_frame.pack(fill=tk.BOTH, expand=True) # 放置主框架

        ttk.Label(main_frame, text=f"Select Items ({len(self.all_values)}):", font=(self.font_style[0], fontsize, "bold")).pack(anchor="w", pady=2) # 顯示標籤

        btn_frame = ttk.Frame(main_frame) # 建立按鈕框架
        btn_frame.pack(fill=tk.X, pady=2) # 放置按鈕框架
        ttk.Button(btn_frame, text="All", width=8, command=self.select_all).pack(side=tk.LEFT, padx=2) # 建立全選按鈕
        ttk.Button(btn_frame, text="None", width=8, command=self.deselect_all).pack(side=tk.LEFT, padx=2) # 建立全不選按鈕

        list_frame = ttk.Frame(main_frame) # 建立列表框架
        list_frame.pack(fill=tk.BOTH, expand=True) # 放置列表框架
        
        canvas = tk.Canvas(list_frame, bg="white") # 建立畫布
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview) # 建立捲軸
        self.scrollable_frame = ttk.Frame(canvas) # 建立可捲動框架

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))) # 綁定配置事件以更新捲動區域
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw") # 在畫布上建立視窗
        canvas.configure(yscrollcommand=scrollbar.set) # 設定畫布的捲軸指令

        scrollbar.pack(side="right", fill="y") # 放置捲軸
        canvas.pack(side="left", fill="both", expand=True) # 放置畫布

        self.vars = {} # 初始化變數字典
        for val in self.all_values: # 遍歷所有值
            var = tk.BooleanVar(value=(val in self.result)) # 建立布林變數
            self.vars[val] = var # 儲存變數
            ttk.Checkbutton( # 建立複選按鈕
                self.scrollable_frame, # 父容器
                text=str(val), # 按鈕文字
                variable=var, # 綁定變數
                style="Big.TCheckbutton" # 設定樣式
            ).pack(anchor="w", padx=5, pady=2) # 放置按鈕

        action_frame = ttk.Frame(main_frame) # 建立動作框架
        action_frame.pack(fill=tk.X, pady=(10, 0)) # 放置動作框架
        ttk.Button(action_frame, text="Apply", command=self.apply).pack(side=tk.LEFT, padx=5) # 建立套用按鈕

    def select_all(self): # 全選函數
        for v in self.vars.values(): v.set(True) # 將所有變數設為 True
    def deselect_all(self): # 全不選函數
        for v in self.vars.values(): v.set(False) # 將所有變數設為 False
    def apply(self): # 套用函數
        selected = {val for val, var in self.vars.items() if var.get()} # 收集被選取的項目
        self.callback(selected) # 呼叫回調函數
        self.destroy() # 關閉視窗
# ========================================================================================================================

# ==============================================================================
# 🧩 緊湊型求解器 (Compact Solver) - 整合自獨立測試模組
# ==============================================================================
class CompactSolverFrame(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self._is_calculating = False # [FIX] 防止遞迴觸發的旗標
        
        # [緊湊化] 字型縮小至 9pt (標準 UI 大小)
        self.f_norm = ("Microsoft JhengHei", fontsize)
        self.f_bold = ("Microsoft JhengHei", fontsize, "bold")
        
        # 變數定義
        self.sv_low = tk.StringVar(value="100")
        self.sv_vfb = tk.StringVar(value="3.3")
        self.sv_hi  = tk.StringVar(value="2382.42")
        self.sv_vout= tk.StringVar(value="81.92")
        self.target_mode = tk.StringVar(value="hi") 
        
        # 綁定事件
        for sv in [self.sv_low, self.sv_vfb, self.sv_hi, self.sv_vout]:
            sv.trace_add("write", lambda *args: self.on_input_change())

        self.create_widgets()
        self.update_ui_state()

    def create_widgets(self):
        # [緊湊化] 使用 LabelFrame 直接做為容器，自帶標題
        self.main_frame = ttk.LabelFrame(self, text="⚡ Reverse Calc", padding=2)
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # [緊湊化] 欄位設定
        rows_config = [
            ("V_Out", self.sv_vout, "vout", self.colors["target"]),
            ("R_high", self.sv_hi,   "hi",   self.colors["hi"]),
            ("V_Ref", self.sv_vfb,  "vfb",  self.colors["ref"]),
            ("R_Low", self.sv_low,  "low",  self.colors["low"])
        ]
        
        self.entries = {}
        
        # [緊湊化] 簡易表頭 (Row 0)
        ttk.Label(self.main_frame, text="⚡", font=(self.f_norm[0], fontsize)).grid(row=0, column=0, pady=1)
        ttk.Label(self.main_frame, text="Param", font=(self.f_norm[0], fontsize)).grid(row=0, column=1, pady=1)
        ttk.Label(self.main_frame, text="Value", font=(self.f_norm[0], fontsize)).grid(row=0, column=2, pady=1)

        for idx, (label_text, var, mode_key, color) in enumerate(rows_config):
            r = idx + 1
            
            # 1. RadioButton (緊湊版)
            rb = ttk.Radiobutton(
                self.main_frame, 
                variable=self.target_mode, 
                value=mode_key,
                command=self.update_ui_state
            )
            rb.grid(row=r, column=0, padx=1, pady=1)
            
            # 2. Label (緊湊版)
            lbl = ttk.Label(self.main_frame, text=label_text, font=self.f_bold, foreground=color, anchor="center")
            lbl.grid(row=r, column=1, padx=2, pady=1, sticky="ew")
            
            # 3. Entry (緊湊版)
            entry = tk.Entry(self.main_frame, textvariable=var, font=self.f_norm, width=10, justify="center")
            entry.grid(row=r, column=2, padx=2, pady=1, sticky="ew")
            self.entries[mode_key] = entry
            
        self.main_frame.columnconfigure(2, weight=1)
        # [UI優化] Row 0 (表頭) 不參與拉伸 (weight=0)，保持最小高度
        self.main_frame.rowconfigure(0, weight=0)
        # [UI優化] Row 1~4 (資料列) 平均分配剩餘垂直空間 (weight=1)
        for i in range(1, len(rows_config) + 1):
            self.main_frame.rowconfigure(i, weight=1)

    def update_ui_state(self):
        target = self.target_mode.get()
        COLOR_LOCKED = "#FFC0C0" 
        COLOR_EDIT = "white"
        
        for key, entry in self.entries.items():
            if key == target:
                entry.config(bg=COLOR_LOCKED, readonlybackground=COLOR_LOCKED, fg="black", state="readonly", relief="flat") 
            else:
                entry.config(bg=COLOR_EDIT, fg="black", state="normal", relief="sunken")
        self.calculate()

    def on_input_change(self):
        # 如果正在計算中，則忽略這次由 .set() 觸發的事件
        if self._is_calculating:
            return
        self.calculate()

    def calculate(self):
        target = self.target_mode.get()
        
        # 設定旗標，表示開始計算，阻擋後續的連鎖觸發
        self._is_calculating = True
        
        try:
            def get(v): s = v.get(); return float(s) if s else 0.0
            
            r2, vfb, r1, vout = get(self.sv_low), get(self.sv_vfb), get(self.sv_hi), get(self.sv_vout)

            res = 0.0
            if target == "vout":
                if r2 != 0: res = vfb * (1 + r1 / r2)
                self.sv_vout.set(f"{res:.6g}") 
            elif target == "hi":
                if vfb != 0: res = r2 * (vout / vfb - 1)
                self.sv_hi.set(f"{res:.6g}")
            elif target == "low":
                if vfb != 0 and (vout/vfb - 1) != 0: res = r1 / (vout / vfb - 1)
                self.sv_low.set(f"{res:.6g}")
            elif target == "vfb":
                if r2 != 0 and (1 + r1/r2) != 0: res = vout / (1 + r1 / r2)
                self.sv_vfb.set(f"{res:.6g}")
        except: 
            pass
        finally:
            # 計算結束，無論成功或失敗，都必須清除旗標
            self._is_calculating = False
# ========================================================================================================================
# ==============================================================================
# 🖥️ 主程式
# ==============================================================================
class RVDSApp: # 定義主應用程式類別
    def __init__(self, root): # 初始化函數
        self.root = root # 儲存 root 視窗物件
        self.root.title(H_title) # 設定視窗標題
        self.root.geometry(Windows_Size) # 設定視窗大小
        
        self.app_font = configure_system_settings(root) # 設定系統字型
        
        # [Threading] 初始化 Queue
        self.msg_queue = queue.Queue() # 建立訊息佇列

        self.v_ref = tk.DoubleVar(value=3.3) # 初始化參考電壓變數
        self.v_target = tk.DoubleVar(value=81.92) # 初始化目標電壓變數
        self.tolerance = tk.StringVar(value="0.5") # 初始化容差變數
        
        # [Non-Linear Scale] 建立滑桿專用的虛擬變數 (0.0 ~ 1.0)
        self.tol_slider_var = tk.DoubleVar() # 初始化滑桿變數
        # 初始化滑桿位置 (反向映射)
        init_s = ((0.5 - MIN_TOLERANCE) / (MAX_TOLERANCE - MIN_TOLERANCE)) ** (1/5) # 計算初始滑桿位置
        self.tol_slider_var.set(init_s) # 設定滑桿位置

        self.var_display_limit = tk.IntVar(value=100) # 初始化顯示數量限制變數
        
        self.r_low_mode = tk.StringVar(value="Unlock") # 初始化 R_Low 模式變數
        self.r_low_lock_val = tk.DoubleVar(value=10000) # 初始化 R_Low 鎖定值
        self.r_low_min = tk.DoubleVar(value=1000) # 初始化 R_Low 最小值
        self.r_low_max = tk.DoubleVar(value=1000000) # 初始化 R_Low 最大值
        self.r_low_e24_only = tk.BooleanVar(value=False) # 初始化 R_Low E24 限制變數

        self.r_hi_mode = tk.StringVar(value="Unlock") # 初始化 R_Hi 模式變數
        self.r_hi_lock_val = tk.DoubleVar(value=0) # 初始化 R_Hi 鎖定值
        self.r_hi_min = tk.DoubleVar(value=0) # 初始化 R_Hi 最小值
        self.r_hi_max = tk.DoubleVar(value=1000000) # 初始化 R_Hi 最大值
        self.r_hi1_e24_only = tk.BooleanVar(value=False) # 初始化 R_Hi1 E24 限制變數
        self.r_hi2_e24_only = tk.BooleanVar(value=False) # 初始化 R_Hi2 E24 限制變數

        # [NoPandas] Change DataFrame to List
        self.data_rows = [] # 初始化資料列列表
        
        self.active_filters = {} # 初始化篩選器狀態
        self.sort_state = {} # 初始化排序狀態
        self.base_headers = ["R_Low", "R_Hi1", "R_Hi2", "V_Out", "Error %", "E24 Count"] # 定義表格標題

        # 監聽數值變動，確保手動輸入或程式自動放寬時，滑桿也會跟著動
        self.tolerance.trace_add("write", self._sync_slider_from_val) # 綁定容差變動事件
        self.r_hi_mode.trace_add("write", lambda *args: self.draw_circuit()) # 監聽模式切換以重繪電路圖 # 綁定 R_Hi 模式變動事件

        # [UI Colors] 定義區塊配色方案
        self.ui_colors = { # 定義 UI 顏色字典
            "target": "#AD00AD",  # Red (Target Voltage) # 目標電壓顏色
            "hi":     "#FF0000",  # Orange (High Side) # 高側電阻顏色
            "ref":    "#2F00FF",  # Blue (V_Ref) # 參考電壓顏色
            "low":    "#008000",  # Green (Low Side) # 低側電阻顏色
            "line":   "#000000"   # Dark Gray (Default Line) # 線條顏色
        }
        self.create_widgets() # 建立介面元件

    def create_widgets(self): # 建立介面元件函數
        left_frame = ttk.Frame(self.root, padding="5") # 建立左側框架
        left_frame.pack(side=tk.LEFT, fill=tk.Y) # 放置左側框架
        right_frame = ttk.Frame(self.root, padding="0") # 建立右側框架
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True) # 放置右側框架

        # ======================   左側：參數區域   ======================
        # 1. Target Voltage (Red)
        lbl_1 = ttk.Label(left_frame, text="1. Target Voltage", font=(self.app_font[0], fontsize, "bold"), foreground=self.ui_colors["target"]) # 建立標題標籤
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

        def on_slider_move(val): # 滑桿移動回調函數
            try: # 嘗試處理
                f_val = float(val) # 轉為浮點數
                snapped_val = int(round(f_val / 10) * 10) # 取整到最近的 10
                if self.var_display_limit.get() != snapped_val: # 若值改變
                    self.var_display_limit.set(snapped_val) # 更新變數
            except: pass # 忽略錯誤

        limit_scale = ttk.Scale( # 建立限制滑桿
            lim_frame, # 父容器
            from_= 10, # 最小值
            to= 1000 , # 最大值
            orient='horizontal', # 水平方向
            command=on_slider_move # 綁定回調函數
        )
        limit_scale.set(100) # 設定預設值
        limit_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2) # 放置滑桿
        
        ttk.Label(lim_frame, textvariable=self.var_display_limit, width=5, font=self.app_font, anchor="center", foreground=self.ui_colors["target"]).pack(side=tk.LEFT) # 顯示目前限制值
        
        # ==============
        # 2. High Side Resistor (Orange)
        lbl_2 = ttk.Label(left_frame, text="2. High Side Resistor", font=(self.app_font[0], fontsize, "bold"), foreground=self.ui_colors["hi"]) # 建立高側電阻標題
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
        lbl_4 = ttk.Label(left_frame, text="4. Low Side Resistor", font=(self.app_font[0], fontsize, "bold"), foreground=self.ui_colors["low"]) # 建立低側電阻標題
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

        self.btn_reset = ttk.Button(left_frame, text="Reset View", command=self.reset_all_view) # 建立重置視圖按鈕
        self.btn_reset.pack(fill=tk.X, ipady=2, pady=5) # 放置按鈕
        
        btn_export = ttk.Button(left_frame, text="Export CSV", command=self.export_csv) # 建立匯出 CSV 按鈕
        btn_export.pack(fill=tk.X, ipady=2, pady=5) # 放置按鈕
        
        btn_about = ttk.Button(left_frame, text="About", command=self.show_about) # 建立關於按鈕
        btn_about.pack(side=tk.BOTTOM, fill=tk.X, pady=10) # 放置按鈕
        
        # ======================   右側區域 (上下分割)   ======================
        table_container = ttk.Frame(right_frame) # 建立表格容器
        table_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True) # 放置容器

        self.sheet = Sheet(table_container, headers=self.base_headers) # 建立試算表物件
        self.sheet.pack(fill="both", expand=True) # 放置試算表
        self.sheet.font(newfont=self.app_font) # 設定字型
        self.sheet.header_font(newfont=(self.app_font[0], fontsize, "bold")) # 設定標題字型
        self.sheet.enable_bindings(("single_select", "drag_select", "column_select", "row_select", "column_width_resize", "arrowkeys", "right_click_popup_menu", "rc_select", "copy")) # 啟用綁定
        self.sheet.extra_bindings([("rc_header", self.on_header_right_click)]) # 額外綁定右鍵選單
        self.sheet.popup_menu_add_command("Sort Ascending", self.sort_asc_from_cell) # 新增排序指令
        self.sheet.popup_menu_add_command("Sort Descending", self.sort_desc_from_cell) # 新增排序指令
        self.sheet.popup_menu_add_command("Filter", self.filter_from_cell) # 新增篩選指令
        self.sheet.popup_menu_add_command("Clear Filter", self.clear_filter_from_cell) # 新增清除篩選指令

        # ======================   底部區域：電路圖 + 筆記   ======================
        bottom_area = ttk.Frame(right_frame) # 建立底部區域框架
        bottom_area.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5) # 放置框架

        # 1. Circuit (Left)
        circuit_frame = ttk.LabelFrame(bottom_area, text="Circuit", padding=2) # 建立電路圖框架
        circuit_frame.pack(side=tk.LEFT, padx=(0, 5)) # 放置框架
        self.circuit_canvas = tk.Canvas(circuit_frame, width=80, height=210, bg="white", highlightthickness=0) # 建立畫布
        self.circuit_canvas.pack() # 放置畫布
        self.draw_circuit() # 初始繪製 # 呼叫繪製電路圖函數

        # 1.5 Compact Solver (Middle) - 固定寬度，不隨視窗拉伸
        self.compact_solver = CompactSolverFrame(bottom_area, self.ui_colors)
        self.compact_solver.pack(side=tk.LEFT, padx=(0, 5), fill="y", expand=False)

        # 2. Notes (Right)
        notepad_frame = ttk.LabelFrame(bottom_area, text="📝 Notes", padding=5) # 建立筆記框架
        notepad_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # 放置框架
        
        note_scroll = ttk.Scrollbar(notepad_frame) # 建立捲軸
        note_scroll.pack(side=tk.RIGHT, fill=tk.Y) # 放置捲軸

        self.notepad = tk.Text(notepad_frame, height=10, font=self.app_font, undo=True) # 建立文字區域
        self.notepad.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # 放置文字區域
        
        # [UI] 預填表格標題至筆記區
        self.notepad.insert("1.0", "R_Low	R_Hi1	R_Hi2	V_Out" + "		%      E24" + "\n")
        
        self.notepad.config(yscrollcommand=note_scroll.set) # 設定捲軸指令
        note_scroll.config(command=self.notepad.yview) # 設定捲軸控制
        self.notepad.bind("<Button-3>", self.on_notepad_right_click) # 綁定右鍵點擊事件

    def draw_circuit(self): # 繪製電路圖函數
        """ 繪製動態電路圖 (ANSI Zigzag Style) """ # 函數說明
        self.circuit_canvas.delete("all") # 清除畫布
        w = 60  # 設定寬度 # 設定寬度變數
        cx = w // 2 # 計算中心 x 座標
        line_width = 2 # 設定線條寬度
        default_color = self.ui_colors["line"] # 設定預設顏色
        
        def draw_resistor(x, y, h, label, color): # 內部函數：繪製電阻
            # 繪製鋸齒狀電路符號 # 註解
            seg = h / 6 # 計算區段高度
            ww = 8 # 鋸齒寬度 # 設定鋸齒寬度
            coords = [ # 定義座標點列表
                x, y, # 起點
                x, y,          # Start # 起點
                x+ww, y+seg*1, # Right # 右側點
                x-ww, y+seg*2, # Left # 左側點
                x+ww, y+seg*3, # Right # 右側點
                x-ww, y+seg*4, # Left # 左側點
                x+ww, y+seg*5, # Right # 右側點
                x, y+seg*6,    # Back to center # 回到中心
                x, y+h         # End # 終點
            ]
            self.circuit_canvas.create_line(coords, width=line_width, fill=color, capstyle=tk.ROUND, joinstyle=tk.ROUND) # 繪製線條
            self.circuit_canvas.create_text(x+10, y+h/2+10, text=label, anchor="w", font=(self.app_font[0], 9, "bold"), fill=color) # 繪製標籤文字

        # 1. Top Node (V_Target)
        self.circuit_canvas.create_text(cx, 15, text="V_Target", font=(self.app_font[0], 10, "bold"), fill=self.ui_colors["target"]) # 繪製 V_Target 文字
        self.circuit_canvas.create_line(cx, 25, cx, 40, width=line_width, fill=self.ui_colors["target"]) # 繪製連接線
        self.circuit_canvas.create_line(cx-20, 25, cx+ 20, 25, width=line_width, fill=self.ui_colors["target"]) # 在這裡幫我加一個正電的 BAR 符號 # 繪製電源符號橫線

        # 2. R_Hi Section
        mode = self.r_hi_mode.get() # 取得 R_Hi 模式
        if mode == "Disable": # Single Mode # 若為單電阻模式
            draw_resistor(cx, 40, 40, "R_Hi1", self.ui_colors["hi"]) # 繪製 R_Hi1
            current_y = 80 # 更新目前 y 座標
        else: # Dual Mode # 若為雙電阻模式
            draw_resistor(cx, 40, 30, "R_Hi1", self.ui_colors["hi"]) # 繪製 R_Hi1
            self.circuit_canvas.create_line(cx, 70, cx, 80, width=line_width, fill=self.ui_colors["hi"]) # Series connection wire # 繪製串聯線
            draw_resistor(cx, 80, 30, "R_Hi2", self.ui_colors["hi"]) # 繪製 R_Hi2
            current_y = 110 # 更新目前 y 座標

        # 3. Middle Node (V_Ref) & R_Low
        self.circuit_canvas.create_line(cx, current_y, cx, current_y+20, width=line_width, fill=self.ui_colors["ref"]) # Wire to R_Low # 繪製連接線
        self.circuit_canvas.create_line(cx, current_y+10, cx+40, current_y+10, width=line_width, fill=self.ui_colors["ref"]) # Tap wire # 繪製分壓點引出線
        self.circuit_canvas.create_text(cx+10, current_y+18, text="V_Ref", anchor="w", font=(self.app_font[0], 10, "bold"), fill=self.ui_colors["ref"]) # 繪製 V_Ref 文字
        
        draw_resistor(cx, current_y+20, 40, "R_Low", self.ui_colors["low"]) # 繪製 R_Low
        
        # 4. GND
        gy = current_y + 60 # 計算 GND y 座標
        self.circuit_canvas.create_line(cx, gy, cx, gy+10, width=line_width, fill=default_color) # Wire to GND # 繪製連接線
        # GND Symbol
        self.circuit_canvas.create_line(cx-15, gy+10, cx+15, gy+10, width=line_width, fill=default_color) # 繪製 GND 符號橫線 1
        self.circuit_canvas.create_line(cx-10, gy+14, cx+10, gy+14, width=line_width, fill=default_color) # 繪製 GND 符號橫線 2
        self.circuit_canvas.create_line(cx-5, gy+18, cx+5, gy+18, width=line_width, fill=default_color) # 繪製 GND 符號橫線 3

    def on_notepad_right_click(self, event): # 筆記區右鍵點擊事件處理
        """ Notes 區域右鍵直接貼上 """ # 函數說明
        try: # 嘗試執行
            self.notepad.focus_set() # 設定焦點
            # 移動游標到滑鼠點擊的位置
            self.notepad.mark_set("insert", f"@{event.x},{event.y}") # 移動插入點
            # 執行貼上
            self.notepad.event_generate("<<Paste>>") # 觸發貼上事件
            return "break" # 阻止預設行為
        except: pass # 忽略錯誤

    def _sync_val_from_slider(self, val): # 滑桿同步數值函數
        """ 當滑桿移動時：使用 5 次方映射計算實際容差 (極度放大左側解析度) """ # 函數說明
        try: # 嘗試執行
            s = float(val) # 轉為浮點數
            # 公式：Val = Min + (Max - Min) * s^5
            new_tol = MIN_TOLERANCE + (MAX_TOLERANCE - MIN_TOLERANCE) * (s ** 5) # 計算新的容差值
            
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
            val = max(MIN_TOLERANCE, min(MAX_TOLERANCE, val)) # 限制範圍
            # 反公式：s = ((Val - Min) / (Max - Min))^(1/5)
            new_s = ((val - MIN_TOLERANCE) / (MAX_TOLERANCE - MIN_TOLERANCE)) ** (1/5) # 計算新的滑桿位置
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

    def _calc_gradient_hex(self, ratio): # 計算漸層顏色函數
        """ 計算 綠 -> 黃 -> 紅 -> 紫 的漸層 HEX """ # 函數說明
        ratio = max(0.0, min(1.0, ratio)) # 限制比例在 0 到 1 之間
        if ratio <= 0.33: # 第一階段
            r = ratio / 0.33 # 計算比例
            s, e = (192, 255, 192), (255, 255, 192) # Green -> Yellow # 設定起始與結束顏色
        elif ratio <= 0.66: # 第二階段
            r = (ratio - 0.33) / 0.33 # 計算比例
            s, e = (255, 255, 192), (255, 192, 192) # Yellow -> Red # 設定起始與結束顏色
        else: # 第三階段
            r = (ratio - 0.66) / 0.34 # 計算比例
            s, e = (255, 192, 192), (255, 192, 255) # Red -> Purple # 設定起始與結束顏色
            
        rgb = tuple(int(s[i] + (e[i] - s[i]) * r) for i in range(3)) # 計算插值後的 RGB
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}" # 回傳 HEX 顏色字串

    def _determine_r_color(self, val):    # ===       """ 判斷電阻值的顏色 (E24/E96) """ # 判斷電阻顏色函數
        if val <= 0: return c_red # 若值小於等於 0 回傳紅色
        try: # 嘗試執行
            exponent = math.floor(math.log10(val)) # 計算指數
            mantissa = round(val / (10 ** exponent), 2) # 計算尾數
            mantissa_int = int(round(mantissa * 100)) # 轉為整數
            if mantissa_int in E24_SIGS: return c_green # 若在 E24 中回傳綠色
            elif mantissa_int in E96_SIGS: return c_yellow # 若在 E96 中回傳黃色
            else: return c_red # 否則回傳紅色
        except Exception: return c_red # 若發生錯誤回傳紅色

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
            
            current_tol = self.validate_input(self.tolerance, MIN_TOLERANCE, MAX_TOLERANCE) # 驗證並取得容差
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
                'r_hi_lock': self.r_hi_lock_val.get(), # R_Hi 鎖定值
                'r_hi_min': self.r_hi_min.get(), # R_Hi 最小值
                'r_hi_max': self.r_hi_max.get(), # R_Hi 最大值
                'r_hi1_e24': self.r_hi1_e24_only.get(), # R_Hi1 E24 限制
                'r_hi2_e24': self.r_hi2_e24_only.get() # R_Hi2 E24 限制
            }
            
            t = threading.Thread(target=self.worker_calculation, args=(params,)) # 建立執行緒
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

    def worker_calculation(self, p): # 背景計算函數
        """ 子執行緒：Numpy 運算與原生 Python 資料處理 """ # 函數說明
        try: # 嘗試執行
            self.msg_queue.put(("status", ("Initializing resistor database...", "blue"))) # 發送狀態訊息
            
            # --- 準備電阻庫 (保持不變) ---
            r_all = np.unique(np.concatenate((get_resistor_list(E96_BASE), get_resistor_list(E24_BASE)))) # 產生所有電阻值
            r_all = np.round(r_all, PRECISION_DIGITS) # 四捨五入
            e24_full_list = np.round(get_resistor_list(E24_BASE), PRECISION_DIGITS) # 產生 E24 電阻值列表
            
            if p['r_low_mode'] == "Locked": # 若 R_Low 為鎖定模式
                r_low_rng = np.array([p['r_low_lock']]) # 設定為鎖定值
            else: # 若為掃描模式
                r_low_rng = r_all[(r_all >= p['r_low_min']) & (r_all <= p['r_low_max'])] # 篩選範圍內的電阻
                if p['r_low_e24']: # 若限制 E24
                     r_low_rng = r_low_rng[np.isin(r_low_rng, e24_full_list)] # 篩選 E24 電阻
            r_low_rng = r_low_rng[r_low_rng > 0] # 移除 0 或負值
            
            if len(r_low_rng) == 0: # 若無有效 R_Low
                self.msg_queue.put(("error", "No valid R_Low found in the specified range.")) # 發送錯誤訊息
                return # 結束函數

            r_hi1_rng = r_all[(r_all >= p['r_hi_min']) & (r_all <= p['r_hi_max'])] # 篩選 R_Hi1 範圍
            if p['r_hi1_e24']: # 若限制 E24
                r_hi1_rng = r_hi1_rng[np.isin(r_hi1_rng, e24_full_list)] # 篩選 E24 電阻
            
            if p['r_hi_mode'] == "Disable": # 若 R_Hi2 停用
                r_hi2_rng = np.array([0.0]) # 設定為 0
            elif p['r_hi_mode'] == "Locked": # 若 R_Hi2 鎖定
                r_hi2_rng = np.array([p['r_hi_lock']]) # 設定為鎖定值
            else: # 若為掃描模式
                r_hi2_rng = r_all[(r_all >= p['r_hi_min']) & (r_all <= p['r_hi_max'])] # 篩選 R_Hi2 範圍
                if p['r_hi2_e24']: # 若限制 E24
                    r_hi2_rng = r_hi2_rng[np.isin(r_hi2_rng, e24_full_list)] # 篩選 E24 電阻

            if len(r_hi1_rng) * len(r_hi2_rng) > 50_000_000: # 若搜尋空間過大
                self.msg_queue.put(("error", "Search space too large (>50M). Please reduce range.")) # 發送錯誤訊息
                return # 結束函數

            self.msg_queue.put(("status", ("Generating combination matrix...", "blue"))) # 發送狀態訊息
            
            current_tol = p['tol'] # 取得目前容差
            MAX_RETRY_LIMIT = 40 # 設定最大重試次數
            retry_count = 0 # 初始化重試計數
            
            while retry_count < MAX_RETRY_LIMIT: # 迴圈重試
                
                # [ROMANCE] 每次迴圈開始，更新介面滑塊位置
                # 這樣你可以看到滑塊跳到新的位置，準備開始掃描
                self.msg_queue.put(("update_tol", current_tol)) # 發送更新容差訊息
                
                # [ROMANCE] 這裡加一點點延遲，讓你的肉眼能捕捉到滑塊到位
                # 如果沒有這個延遲，電腦運算太快，滑塊會瞬移，看起來就沒那麼「機械感」
                if retry_count > 0: # 若非第一次執行
                    time.sleep(0.1) # 延遲 0.1 秒

                # --- 矩陣運算 (保持不變) ---
                mat = r_hi1_rng[:, None] + r_hi2_rng[None, :] # 計算 R_Hi 總和矩陣
                flat = mat.flatten() # 展平矩陣

                valid_idx, valid_rlow = [], [] # 初始化有效索引與 R_Low 列表
                tol_dec = current_tol / 100.0 # 計算容差小數
                k_min = ((p['v_target'] * (1 - tol_dec)) / p['v_ref']) - 1 # 計算最小比率
                k_max = ((p['v_target'] * (1 + tol_dec)) / p['v_ref']) - 1 # 計算最大比率
                
                chunk_size = 500 # 設定區塊大小
                
                for i in range(0, len(r_low_rng), chunk_size): # 分塊處理 R_Low
                    if i % (chunk_size * 10) == 0: # 每 10 個區塊更新一次狀態
                        # 狀態列顯示正在掃描，配合滑塊位置，很有感覺
                        self.msg_queue.put(("status", (f"Scanning... {current_tol:.4f}% (Attempt {retry_count})", "orange"))) # 發送狀態訊息
                    
                    chunk = r_low_rng[i:i+chunk_size] # 取得目前區塊
                    for rl in chunk: # 遍歷區塊內的 R_Low
                        t_min, t_max = rl * k_min, rl * k_max # 計算目標範圍
                        mask = (flat >= t_min) & (flat <= t_max) # 建立遮罩
                        if np.any(mask): # 若有符合的組合
                            idxs = np.where(mask)[0] # 取得索引
                            valid_idx.append(idxs) # 加入有效索引列表
                            valid_rlow.append(np.full(len(idxs), rl)) # 加入對應的 R_Low
                
                # --- 無解處理 (放寬 - 滑塊會往右跳) ---
                is_no_solution = False # 初始化無解旗標
                if isinstance(valid_idx, list): # 若為列表
                    if not valid_idx: is_no_solution = True # 若為空則設為無解
                elif isinstance(valid_idx, np.ndarray): # 若為陣列
                    if valid_idx.size == 0: is_no_solution = True # 若大小為 0 則設為無解

                if is_no_solution:  # 進入無解處理邏輯：當前容差範圍內找不到任何組合 # 若無解
                    if current_tol >= MAX_TOLERANCE: # 檢查是否已達到系統設定的最大容差上限 (例如 3%) # 若已達最大容差
                        self.msg_queue.put(("error", f"No solution found within max tolerance ({MAX_TOLERANCE}%).")) # 回報錯誤給主介面並終止 # 發送錯誤訊息
                        return # 結束函數
                    
                    new_tol = (current_tol + (MIN_TOLERANCE*100 )) * 10  # 自動放寬演算法：採用階梯式倍增，確保能快速跳出死胡同 # 計算新容差
                    current_tol = round(new_tol, PRECISION_DIGITS)  # 四捨五入以保持滑塊數值整潔，避免浮點數細微誤差 # 更新目前容差
                    
                    self.msg_queue.put(("status", (f"Relaxing tolerance... -> {current_tol:.4f}%", "purple")))  # 更新狀態列顏色為紫色，提示使用者正在放寬條件 # 發送狀態訊息
                    # 滑塊將在下一次迴圈開頭更新
                    continue # 繼續下一次迴圈

                self.msg_queue.put(("status", ("Processing results...", "blue"))) # 發送狀態訊息
                
                idx_all = np.concatenate(valid_idx) # 合併所有索引
                rlow_all = np.concatenate(valid_rlow) # 合併所有 R_Low
                hi_tot = flat[idx_all] # 取得對應的 R_Hi 總和
                
                vouts = p['v_ref'] * (1 + hi_tot / rlow_all) # 計算輸出電壓
                errs = np.abs((vouts - p['v_target']) / p['v_target']) * 100 # 計算誤差百分比
                
                # [Optimization] 使用 NumPy 進行向量化去重與計算
                hi1_raw, hi2_raw = np.unravel_index(idx_all, mat.shape) # 還原 R_Hi1 與 R_Hi2 的索引
                r_hi1_vals = r_hi1_rng[hi1_raw] # 取得 R_Hi1 值
                r_hi2_vals = r_hi2_rng[hi2_raw] # 取得 R_Hi2 值
                
                # 向量化排序 R_Hi1, R_Hi2
                r_hi_max = np.maximum(r_hi1_vals, r_hi2_vals) # 取得較大的 R_Hi
                r_hi_min = np.minimum(r_hi1_vals, r_hi2_vals) # 取得較小的 R_Hi
                
                # 向量化去重 (利用 np.unique 的 axis 功能)
                combined = np.stack([rlow_all, r_hi_max, r_hi_min], axis=1) # 堆疊陣列
                _, unique_indices = np.unique(combined, axis=0, return_index=True) # 去重並取得索引
                
                rlow_all = rlow_all[unique_indices] # 更新 R_Low
                r_hi_max = r_hi_max[unique_indices] # 更新 R_Hi_Max
                r_hi_min = r_hi_min[unique_indices] # 更新 R_Hi_Min
                vouts = vouts[unique_indices] # 更新輸出電壓
                errs = errs[unique_indices] # 更新誤差
                
                # 向量化計算 E24 數量
                e24_mask_l = np.isin(rlow_all, e24_full_list) # 檢查 R_Low 是否為 E24
                e24_mask_h1 = np.isin(r_hi_max, e24_full_list) # 檢查 R_Hi_Max 是否為 E24
                e24_mask_h2 = np.isin(r_hi_min, e24_full_list) # 檢查 R_Hi_Min 是否為 E24
                e24_counts = e24_mask_l.astype(int) + e24_mask_h1.astype(int) + e24_mask_h2.astype(int) # 計算 E24 總數
                
                # 快速建立字典列表 (使用 zip 效率最高)
                final_rows = [ # 建立結果列表
                    {"R_Low": rl, "R_Hi1": rh1, "R_Hi2": rh2, "Vout": vo, "V_Dev": er, "E24_Count": ec} # 建立字典
                    for rl, rh1, rh2, vo, er, ec in zip(rlow_all, r_hi_max, r_hi_min, vouts, errs, e24_counts) # 遍歷所有資料
                ]
                
                total_n = len(final_rows) # 計算總結果數
                # --- 結果過多處理 (縮緊 - 滑塊會往左跳) ---

                if total_n > p['limit']: # 若結果數超過限制
                     # [Optimized] 動態衰減邏輯
                     limit = p['limit'] # 取得限制值
                     ratio = total_n / limit # 計算比例
                     if ratio > 32: factor = 0.3 # 設定衰減因子
                     elif ratio > 16: factor = 0.4 # 設定衰減因子
                     elif ratio > 8: factor = 0.5 # 設定衰減因子
                     elif ratio > 4: factor = 0.6 # 設定衰減因子
                     elif ratio > 2: factor = 0.7 # 設定衰減因子
                     elif ratio > 1.4: factor = 0.8 # 設定衰減因子
                     elif ratio > 1.19: factor = 0.9 # 設定衰減因子
                     elif ratio > 1.01: factor = 0.95 # 設定衰減因子
                     else: factor = 0.99 # 設定衰減因子
                     new_shrink_tol = current_tol * factor # 計算新容差
                     self.msg_queue.put(("status", (f"Optimizing... {current_tol:.4f}% -> {new_shrink_tol:.4f}% ({total_n} found)", "purple"))) # 發送狀態訊息
                     current_tol = new_shrink_tol # 更新目前容差
                     retry_count += 1 # 增加重試計數
                     # 滑塊將在下一次迴圈開頭更新
                     continue # 繼續下一次迴圈
                else: # 若結果數未超過限制
                    final_rows.sort(key=lambda x: x['V_Dev']) # 依誤差排序
                    self.msg_queue.put(("success", (final_rows, current_tol))) # 發送成功訊息
                    return # 結束函數

            # Retry 次數用盡
            final_rows.sort(key=lambda x: x['V_Dev']) # 依誤差排序
            if len(final_rows) > p['limit']: # 若結果數超過限制
                 final_rows = final_rows[:p['limit']] # 截斷結果
            self.msg_queue.put(("success", (final_rows, current_tol))) # 發送成功訊息
            
        except Exception as e: # 捕捉例外
            traceback.print_exc() # 印出堆疊
            self.msg_queue.put(("error", str(e))) # 發送錯誤訊息

    def preprocess_display_data(self, limit_val): # 預處理顯示資料函數
        # Add display strings and colors to the list of dicts
        if not self.data_rows: return # 若無資料則返回
        
        def _cnt_color(c): # 內部函數：決定 E24 計數顏色
            return c_green if c==3 else (c_yellow if c==2 else (c_red if c==1 else c_purple)) # 根據數量回傳顏色

        for row in self.data_rows: # 遍歷所有資料列
            row['R_Low_Str'] = fmt_rkm(row['R_Low']) # 格式化 R_Low
            row['R_Hi1_Str'] = fmt_rkm(row['R_Hi1']) # 格式化 R_Hi1
            row['R_Hi2_Str'] = fmt_rkm(row['R_Hi2']) # 格式化 R_Hi2
            row['Vout_Str'] = f"{row['Vout']:.6f}V  " # 格式化輸出電壓
            row['V_Dev_Str'] = f"{row['V_Dev']:.6f}%  " # 格式化誤差
            row['E24_Count_Str'] = str(row['E24_Count']) # 格式化 E24 計數
            
            row['Color_R_Low'] = self._determine_r_color(row['R_Low']) # 決定 R_Low 顏色
            row['Color_R_Hi1'] = self._determine_r_color(row['R_Hi1']) # 決定 R_Hi1 顏色
            row['Color_R_Hi2'] = self._determine_r_color(row['R_Hi2']) # 決定 R_Hi2 顏色
            row['Color_E24'] = _cnt_color(row['E24_Count']) # 決定 E24 計數顏色
            
            ratio = row['V_Dev'] / limit_val if limit_val != 0 else 0 # 計算誤差比例
            row['Color_V_Dev'] = self._calc_gradient_hex(ratio) # 計算誤差顏色

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

    # 右鍵選單相關功能
    def on_header_right_click(self, event): # 標題右鍵點擊事件處理
        try: # 嘗試執行
            if isinstance(event, int): col_idx = event # 若事件為整數 (索引)
            elif isinstance(event, (list, tuple)): col_idx = event[0] # 若事件為列表或元組
            else: return # 否則返回
            self.open_header_menu(col_idx) # 開啟標題選單
        except Exception: # 忽略錯誤
            pass # 不做任何事

    def open_header_menu(self, col_idx): # 開啟標題選單函數
        if not self.data_rows: return # 若無資料則返回
        col_name = self.base_headers[col_idx] # 取得欄位名稱
        
        menu = tk.Menu(self.root, tearoff=0) # 建立選單
        menu.add_command(label=f"【{col_name}】", state="disabled") # 加入標題標籤
        menu.add_separator() # 加入分隔線
        menu.add_command(label="Sort Ascending", command=lambda: self.manual_sort(col_idx, 'asc')) # 加入升冪排序指令
        menu.add_command(label="Sort Descending", command=lambda: self.manual_sort(col_idx, 'desc')) # 加入降冪排序指令
        
        if col_name not in ["V_Out", "Error %"]: # 若非輸出電壓或誤差欄位
            menu.add_separator() # 加入分隔線
            menu.add_command(label="Filter", command=lambda: self.open_filter_popup(col_idx)) # 加入篩選指令
            menu.add_command(label="Clear Filter", command=lambda: self.clear_filter(col_idx)) # 加入清除篩選指令
            
        x, y = self.root.winfo_pointerxy() # 取得滑鼠座標
        menu.post(x, y) # 顯示選單

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
            if col_name in ["V_Out", "Error %"]: return # 若為不可篩選欄位則返回
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
        FilterWindow(self.root, col_name, unique_vals, current, lambda res: self.set_filter(col_idx, res), self.app_font) # 開啟篩選視窗

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
            credits_path = get_resource_path("CREDITS.txt") # 取得 CREDITS.txt 路徑
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