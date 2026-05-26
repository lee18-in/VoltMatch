# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import config

def configure_system_settings(root):
    """ 系統相容性設定  根據作業系統設定字型與樣式 """
    system_os = platform.system()
    default_font = ("Helvetica", config.FONTSIZE, "normal")

    if system_os == "Windows":
        try:
            from ctypes import windll # type: ignore
            windll.shcore.SetProcessDpiAwareness(1) # type: ignore
            default_font = ("Microsoft JhengHei", config.FONTSIZE, "normal")
        except Exception:
            print("DPI Awareness set failed, utilizing default settings.")
    elif system_os == "Darwin":
        default_font = ("PingFang TC", config.FONTSIZE, "normal")
    elif system_os == "Linux":
        fonts = ["WenQuanYi Micro Hei", "Noto Sans CJK TC", "Droid Sans Fallback"]
        default_font = (fonts[0], config.FONTSIZE, "normal")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TEntry", font=(default_font[0], config.FONTSIZE, "bold"))
    style.configure("Treeview.Heading", font=(default_font[0], config.FONTSIZE, "bold"))
    style.configure("TLabel", font=default_font)
    style.configure("TButton", font=default_font)
    style.configure("TLabelframe.Label", font=(default_font[0], config.FONTSIZE, "bold"))
    style.configure("TRadiobutton", font=default_font)
    style.configure("Big.TCheckbutton", font=(default_font[0], config.FONTSIZE, "normal"))
    
    return default_font

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

        ttk.Label(main_frame, text=f"Select Items ({len(self.all_values)}):", font=(self.font_style[0], config.FONTSIZE, "bold")).pack(anchor="w", pady=2) # 顯示標籤

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
        self.f_norm = ("Microsoft JhengHei", config.FONTSIZE)
        self.f_bold = ("Microsoft JhengHei", config.FONTSIZE, "bold")
        
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
        ttk.Label(self.main_frame, text="⚡", font=(self.f_norm[0], config.FONTSIZE)).grid(row=0, column=0, pady=1)
        ttk.Label(self.main_frame, text="Param", font=(self.f_norm[0], config.FONTSIZE)).grid(row=0, column=1, pady=1)
        ttk.Label(self.main_frame, text="Value", font=(self.f_norm[0], config.FONTSIZE)).grid(row=0, column=2, pady=1)

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
# 🎨 電路圖繪製畫布 (Circuit Canvas)
# ==============================================================================
class CircuitCanvas(tk.Canvas):
    def __init__(self, parent, ui_colors, app_font, **kwargs):
        super().__init__(parent, **kwargs)
        self.ui_colors = ui_colors
        self.app_font = app_font

    def draw_circuit(self, r_hi_mode):
        """ 繪製動態電路圖 (ANSI Zigzag Style) """
        self.delete("all") # 清除畫布
        w = 60  # 設定寬度變數
        cx = w // 2 # 計算中心 x 座標
        line_width = 2 # 設定線條寬度
        default_color = self.ui_colors["line"] # 設定預設顏色
        
        def draw_resistor(x, y, h, label, color): # 內部函數：繪製電阻
            seg = h / 6 # 計算區段高度
            ww = 8 # 設定鋸齒寬度
            coords = [
                x, y, x, y, x+ww, y+seg*1, x-ww, y+seg*2, x+ww, y+seg*3,
                x-ww, y+seg*4, x+ww, y+seg*5, x, y+seg*6, x, y+h
            ]
            self.create_line(coords, width=line_width, fill=color, capstyle=tk.ROUND, joinstyle=tk.ROUND)
            self.create_text(x+10, y+h/2+10, text=label, anchor="w", font=(self.app_font[0], 9, "bold"), fill=color)

        # 1. Top Node (V_Target)
        self.create_text(cx, 15, text="V_Target", font=(self.app_font[0], 10, "bold"), fill=self.ui_colors["target"])
        self.create_line(cx, 25, cx, 40, width=line_width, fill=self.ui_colors["target"])
        self.create_line(cx-20, 25, cx+ 20, 25, width=line_width, fill=self.ui_colors["target"])

        # 2. R_Hi Section
        if r_hi_mode == "Disable": # 若為單電阻模式
            draw_resistor(cx, 40, 40, "R_Hi1", self.ui_colors["hi"])
            current_y = 80
        else: # 若為雙電阻模式
            draw_resistor(cx, 40, 30, "R_Hi1", self.ui_colors["hi"])
            self.create_line(cx, 70, cx, 80, width=line_width, fill=self.ui_colors["hi"])
            draw_resistor(cx, 80, 30, "R_Hi2", self.ui_colors["hi"])
            current_y = 110

        # 3. Middle Node (V_Ref) & R_Low
        self.create_line(cx, current_y, cx, current_y+20, width=line_width, fill=self.ui_colors["ref"])
        self.create_line(cx, current_y+10, cx+40, current_y+10, width=line_width, fill=self.ui_colors["ref"])
        self.create_text(cx+10, current_y+18, text="V_Ref", anchor="w", font=(self.app_font[0], 10, "bold"), fill=self.ui_colors["ref"])
        draw_resistor(cx, current_y+20, 40, "R_Low", self.ui_colors["low"])
        
        # 4. GND
        gy = current_y + 60
        self.create_line(cx, gy, cx, gy+10, width=line_width, fill=default_color)
        self.create_line(cx-15, gy+10, cx+15, gy+10, width=line_width, fill=default_color)
        self.create_line(cx-10, gy+14, cx+10, gy+14, width=line_width, fill=default_color)
        self.create_line(cx-5, gy+18, cx+5, gy+18, width=line_width, fill=default_color)