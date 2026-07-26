# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import platform
import config
import divider_math

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
        
        if len(unique_values) > config.FILTER_DISPLAY_LIMIT: # 檢查是否超過顯示限制
            messagebox.showwarning("Display Limit", f"[{col_name}] Too much data; only the first {config.FILTER_DISPLAY_LIMIT} records are displayed.") # 顯示警告
            unique_values = unique_values[:config.FILTER_DISPLAY_LIMIT] # 截斷資料

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
class CompactSolverFrame(ttk.LabelFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, text="⚡ Quick Solver", padding=2)
        self.colors = colors
        self._is_calculating = False # [FIX] 防止遞迴觸發的旗標
        
        # [緊湊化] 字型縮小至 9pt (標準 UI 大小)
        self.f_norm = ("Microsoft JhengHei", config.FONTSIZE)
        self.f_bold = ("Microsoft JhengHei", config.FONTSIZE, "bold")
        
        # 變數定義
        self.sv_low = tk.StringVar(value=config.DEFAULT_SOLVER_LOW)
        self.sv_vfb = tk.StringVar(value=str(config.DEFAULT_V_REF))
        self.sv_hi  = tk.StringVar(value=config.DEFAULT_SOLVER_HI)
        self.sv_vout= tk.StringVar(value=str(config.DEFAULT_V_TARGET))
        self.target_mode = tk.StringVar(value=config.DEFAULT_SOLVER_TARGET) 
        
        # 綁定事件
        for sv in [self.sv_low, self.sv_vfb, self.sv_hi, self.sv_vout]:
            sv.trace_add("write", lambda *args: self.on_input_change())

        self.create_widgets()
        self.update_ui_state()

    def create_widgets(self):
        # [緊湊化] 欄位設定
        rows_config = [
            ("V_Out", self.sv_vout, "vout", self.colors["target"]),
            ("R_high", self.sv_hi,   "hi",   self.colors["hi"]),
            ("V_Ref", self.sv_vfb,  "vfb",  self.colors["ref"]),
            ("R_Low", self.sv_low,  "low",  self.colors["low"])
        ]
        
        self.entries = {}
        
        # [緊湊化] 簡易表頭 (Row 0)
        ttk.Label(self, text="⚡", font=(self.f_norm[0], config.FONTSIZE)).grid(row=0, column=0, pady=1)
        ttk.Label(self, text="Param", font=(self.f_norm[0], config.FONTSIZE)).grid(row=0, column=1, pady=1)
        ttk.Label(self, text="Value", font=(self.f_norm[0], config.FONTSIZE)).grid(row=0, column=2, pady=1)

        for idx, (label_text, var, mode_key, color) in enumerate(rows_config):
            r = idx + 1
            
            # 1. RadioButton (緊湊版)
            rb = ttk.Radiobutton(
                self, 
                variable=self.target_mode, 
                value=mode_key,
                command=self.update_ui_state
            )
            rb.grid(row=r, column=0, padx=1, pady=1)
            
            # 2. Label (緊湊版)
            lbl = ttk.Label(self, text=label_text, font=self.f_bold, foreground=color, anchor="center")
            lbl.grid(row=r, column=1, padx=2, pady=1, sticky="ew")
            
            # 3. Entry (緊湊版)
            entry = tk.Entry(self, textvariable=var, font=self.f_norm, width=10, justify="center")
            entry.grid(row=r, column=2, padx=2, pady=1, sticky="ew")
            self.entries[mode_key] = entry
            
        self.columnconfigure(2, weight=1)
        # [UI優化] Row 0 (表頭) 不參與拉伸 (weight=0)，保持最小高度
        self.rowconfigure(0, weight=0)
        # [UI優化] Row 1~4 (資料列) 平均分配剩餘垂直空間 (weight=1)
        for i in range(1, len(rows_config) + 1):
            self.rowconfigure(i, weight=1)

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

            # 公式本體一律走 divider_math，不在 UI 層重複實作 (與搜尋演算法共用同一份知識)
            if target == "vout":
                self.sv_vout.set(f"{divider_math.solve_v_out(vfb, r1, r2):.6g}")
            elif target == "hi":
                self.sv_hi.set(f"{divider_math.solve_r_high(vfb, vout, r2):.6g}")
            elif target == "low":
                self.sv_low.set(f"{divider_math.solve_r_low(vfb, vout, r1):.6g}")
            elif target == "vfb":
                self.sv_vfb.set(f"{divider_math.solve_v_ref(vout, r1, r2):.6g}")
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
    PAD = 4          # 畫布四周留白
    ZIGZAG = 8       # 電阻鋸齒左右擺幅
    TEXT_GAP = 10    # 標籤與導線的水平間距
    GND_HALF = 15    # 接地符號最寬的半寬
    TERM_HALF = 20   # 頂端端子橫線的半寬

    def __init__(self, parent, ui_colors, app_font, **kwargs):
        super().__init__(parent, **kwargs)
        self.ui_colors = ui_colors
        self.app_font = app_font
        # 同一個字級在各作業系統的實際像素寬高不同，改用字型度量推算版面，避免標籤被畫布裁掉
        self.node_font = tkfont.Font(family=app_font[0], size=max(9, config.FONTSIZE - 2), weight="bold")
        self.label_font = tkfont.Font(family=app_font[0], size=max(8, config.FONTSIZE - 3), weight="bold")
        self._mode = None # 目前的 R_Hi 模式，供尺寸變動時重繪使用
        self._last_size = None # 上次重繪時的畫布尺寸，避免 Configure 事件重複觸發
        self.bind("<Configure>", self._on_resize) # 畫布被拉伸時重繪，讓電路圖填滿可用空間

    def draw_circuit(self, r_hi_mode):
        """ 繪製動態電路圖 (ANSI Zigzag Style)，尺寸依實際字型度量計算 """
        self._mode = r_hi_mode
        self._render()

    def _on_resize(self, event):
        """ 畫布尺寸改變時重繪 (例如視窗縮放或底部區塊高度變動) """
        if self._mode is None:
            return
        size = (event.width, event.height)
        if size == self._last_size: # 尺寸沒變就不重繪，避免與 _fit_to_content 互相觸發
            return
        self._last_size = size
        self._render()

    def _render(self):
        """ 依目前模式與可用空間實際繪製 """
        r_hi_mode = self._mode
        self.delete("all") # 清除畫布
        line_width = 2 # 設定線條寬度
        default_color = self.ui_colors["line"] # 設定預設顏色

        node_h = self.node_font.metrics("linespace") # 節點標籤 (V_Target / V_Ref) 行高
        label_h = self.label_font.metrics("linespace") # 電阻標籤行高
        # 主幹導線 x 座標：左側需容納最寬的符號，以及置中繪製的 V_Target 標籤半寬
        cx = self.PAD + max(self.TERM_HALF, self.GND_HALF, self.ZIGZAG, self.node_font.measure("V_Target") // 2 + 2)
        term_y = self.PAD + node_h + 4 # 端子橫線
        hi_y = term_y + 15 # R_Hi 起點
        gnd_span = 18 + line_width * 2 + self.PAD # 接地符號高度 + 線寬圓角 + 底部留白

        r_h = max(30, label_h * 2) # 單顆電阻高度 (雙電阻模式)
        mid_gap = max(20, label_h + 8) # V_Ref 節點上下的導線總長
        low_h = int(r_h * 4 / 3) # R_Low 高度
        single_h = low_h # 單電阻模式下 R_Hi1 的高度
        dual_span = r_h * 2 + 10 # 雙電阻模式的 R_Hi 區段高度 (含兩顆之間的導線)
        hi_natural = single_h if r_hi_mode == "Disable" else dual_span # 目前模式下 R_Hi 區段的自然高度

        # 目前模式的自然高度；畫布被拉伸得更高時，把多出來的空間分配給電阻與節點間距，讓電路圖填滿整塊區域
        natural_h = hi_y + hi_natural + mid_gap + low_h + gnd_span
        # 請求高度一律以雙電阻模式 (較高者) 為準，單/雙電阻切換時外層不會跟著改變高度
        request_h = hi_y + dual_span + mid_gap + low_h + gnd_span
        elastic = hi_natural + mid_gap + low_h # 可伸縮的部分 (文字與接地符號不縮放)
        avail = self.winfo_height() # 尚未 map 時為 1，此時不做伸展
        if avail > natural_h and elastic > 0:
            stretch = (elastic + avail - natural_h) / elastic
            r_h = int(r_h * stretch)
            single_h = int(single_h * stretch)
            mid_gap = int(mid_gap * stretch)
            low_h = int(low_h * stretch)
        hi_span = r_h * 2 + 10 # 拉伸後的 R_Hi 區段高度 (雙電阻模式)

        def draw_resistor(x, y, h, label, color): # 內部函數：繪製電阻
            seg = h / 6 # 計算區段高度
            ww = self.ZIGZAG # 設定鋸齒寬度
            coords = [
                x, y, x, y, x+ww, y+seg*1, x-ww, y+seg*2, x+ww, y+seg*3,
                x-ww, y+seg*4, x+ww, y+seg*5, x, y+seg*6, x, y+h
            ]
            self.create_line(coords, width=line_width, fill=color, capstyle=tk.ROUND, joinstyle=tk.ROUND)
            self.create_text(x+self.TEXT_GAP, y+h/2, text=label, anchor="w", font=self.label_font, fill=color) # 標籤垂直置中於電阻

        # 1. Top Node (V_Target)
        top_y = self.PAD + node_h / 2 # 標題文字中心
        self.create_text(cx, top_y, text="V_Target", font=self.node_font, fill=self.ui_colors["target"])
        self.create_line(cx-self.TERM_HALF, term_y, cx+self.TERM_HALF, term_y, width=line_width, fill=self.ui_colors["target"])
        self.create_line(cx, term_y, cx, hi_y, width=line_width, fill=self.ui_colors["target"])

        # 2. R_Hi Section
        if r_hi_mode == "Disable": # 若為單電阻模式
            draw_resistor(cx, hi_y, single_h, "R_Hi1", self.ui_colors["hi"])
            current_y = hi_y + single_h
        else: # 若為雙電阻模式
            draw_resistor(cx, hi_y, r_h, "R_Hi1", self.ui_colors["hi"])
            self.create_line(cx, hi_y+r_h, cx, hi_y+r_h+10, width=line_width, fill=self.ui_colors["hi"])
            draw_resistor(cx, hi_y+r_h+10, r_h, "R_Hi2", self.ui_colors["hi"])
            current_y = hi_y + hi_span

        # 3. Middle Node (V_Ref) & R_Low
        tap_y = current_y + mid_gap / 2 # V_Ref 分接點
        low_y = current_y + mid_gap # R_Low 起點
        self.create_line(cx, current_y, cx, low_y, width=line_width, fill=self.ui_colors["ref"])
        self.create_line(cx, tap_y, cx+self.TERM_HALF*2, tap_y, width=line_width, fill=self.ui_colors["ref"])
        self.create_text(cx+self.TEXT_GAP, tap_y+node_h/2+2, text="V_Ref", anchor="w", font=self.node_font, fill=self.ui_colors["ref"]) # 置於分接線下方，避免與線重疊
        draw_resistor(cx, low_y, low_h, "R_Low", self.ui_colors["low"])

        # 4. GND
        gy = low_y + low_h # 接地符號起點
        self.create_line(cx, gy, cx, gy+10, width=line_width, fill=default_color)
        self.create_line(cx-self.GND_HALF, gy+10, cx+self.GND_HALF, gy+10, width=line_width, fill=default_color)
        self.create_line(cx-10, gy+14, cx+10, gy+14, width=line_width, fill=default_color)
        self.create_line(cx-5, gy+18, cx+5, gy+18, width=line_width, fill=default_color)

        self._fit_to_content(request_h)

    def _fit_to_content(self, natural_h):
        """ 依繪製後的實際邊界調整畫布請求尺寸，讓標籤在任何字型下都不會被裁切

        高度一律請求「自然高度」而非拉伸後的高度：實際高度由 pack 的 fill 決定，
        若這裡回報拉伸後的高度會讓外層越撐越大，形成無限放大的迴圈。
        """
        bbox = self.bbox("all")
        if not bbox:
            return
        _, _, x1, _ = bbox
        self.configure(width=int(x1) + self.PAD, height=int(natural_h))

# ==============================================================================
# 📝 筆記區域 (Notes Frame)
# ==============================================================================
class NotesFrame(ttk.LabelFrame):
    def __init__(self, parent, app_font, save_callback):
        super().__init__(parent, padding=5)
        
        # 將標題與按鈕整合在 labelwidget 中，實現緊湊佈局
        note_title = ttk.Frame(self)
        ttk.Label(note_title, text="📝 Notes (Right-click to paste)  ").pack(side=tk.LEFT)
        note_save = ttk.Label(note_title, text="💾 Save", cursor="hand2", foreground="#AD00AD")
        note_save.pack(side=tk.LEFT)
        note_save.bind("<Button-1>", lambda event: save_callback())
        self.configure(labelwidget=note_title)

        note_scroll = ttk.Scrollbar(self)
        note_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(self, height=10, font=app_font, undo=True, relief="flat", borderwidth=0, highlightthickness=0)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # [UI] 預填表格標題至筆記區
        header_str = "\t".join(config.SHEET_BASE_HEADERS) + "\n"
        self.text_widget.insert("1.0", header_str)
        
        self.text_widget.config(yscrollcommand=note_scroll.set)
        note_scroll.config(command=self.text_widget.yview)
        self.text_widget.bind("<Button-3>", self.on_right_click)

    def on_right_click(self, event):
        """ Notes 區域右鍵直接貼上 """
        try:
            self.text_widget.focus_set()
            self.text_widget.mark_set("insert", f"@{event.x},{event.y}")
            self.text_widget.event_generate("<<Paste>>")
            return "break"
        except: pass