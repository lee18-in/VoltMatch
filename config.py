# -*- coding: utf-8 -*-

# 顏色常數 (背景色)
C_GREEN = "#C0FFC0"     # Light Green
C_YELLOW = "#FFFFC0"    # Light Yellow
C_RED = "#FFC0C0"       # Light Red
C_PURPLE = "#FFC0FF"    # Light Purple
FONTSIZE = 12           # 預設字型大小

# UI 區塊配色方案 (字體/線條)
UI_COLORS = {
    "target": "#AD00AD",  # Red/Purple (Target Voltage)
    "hi":     "#FF0000",  # Red (High Side)
    "ref":    "#2F00FF",  # Blue (V_Ref)
    "low":    "#008000",  # Green (Low Side)
    "line":   "#000000"   # Dark Gray (Default Line)
}

# 全域常數
PRECISION_DIGITS = 4    # 精度設定：用於浮點數比對的位數
H_TITLE = "VoltMatch - Voltage Divider Optimizer - by lee18.in - Ver. 26.0526.1"
MAX_TOLERANCE = 5       # 最大容差限制 %
MIN_TOLERANCE = 0.00001 # 最小容差限制 %
WINDOWS_SIZE = "1800x1000" # 主視窗
MIN_WINDOW_SIZE = (1800, 1000) # 主視窗最小尺寸 (寬, 高)；高度下限來自左欄控制項的自然高度(實測約 648px)，再縮會裁掉 About 按鈕

# UI 預設參數
DEFAULT_V_REF = 3.3       # 預設參考電壓
DEFAULT_V_TARGET = 81.92  # 預設目標電壓
DEFAULT_TOLERANCE = "0.5" # 預設容差

DEFAULT_DISPLAY_LIMIT = 100 # 顯示限制：最多顯示前 100 組結果
DEFAULT_LIMIT_MIN = 10      # 最小限制：至少顯示 10 組結果
DEFAULT_LIMIT_MAX = 1000    # 最大限制：最多顯示 1000 組結果  「Max Results」滑桿
FILTER_DISPLAY_LIMIT = 1000 # 顯示過濾限制：當結果超過此數量時，啟用過濾機制  選器選項的數量上限

DEFAULT_R_LOW_MODE = "Unlock"       # 預設 R_Low 模式
DEFAULT_R_LOW_LOCK_VAL = 10000.0    # 預設 R_Low 鎖定值 (當 R_Low 模式為 "Lock" 時使用)
DEFAULT_R_LOW_MIN = 1000.0          # 預設 R_Low 最小值
DEFAULT_R_LOW_MAX = 1000000.0       # 預設 R_Low 最大值

DEFAULT_R_HI_MODE = "Unlock"    # 預設 R_Hi 模式
DEFAULT_R_HI_MIN = 0.0          # 預設 R_Hi 最小值
DEFAULT_R_HI_MAX = 1000000.0    # 預設 R_Hi 最大值

# 試算表設定 (Sheet Settings)
SHEET_BASE_HEADERS = ["R_Low", "R_Hi1", "R_Hi2", "V_Out", "Dev %", "E24"]   # 試算表標題列
SHEET_COLUMN_WIDTHS = (68.0, 68.0, 68.0, 98.0, 72.0, 52.0)                  # 試算表各欄寬度
SHEET_INDEX_WIDTH = 42                                                      # 試算表索引欄寬度                

# 緊湊型求解器預設值 (Compact Solver)
DEFAULT_SOLVER_LOW = "100"          # 預設 R_Low 值
DEFAULT_SOLVER_HI = "2382.42"       # 預設 R_Hi 值
DEFAULT_SOLVER_TARGET = "hi"        

# 背景運算常數 (Calculation Worker)
WORKER_MAX_RETRY = 40               # 最大重試次數：當運算過程中發生錯誤時，最多重試的次數
WORKER_CHUNK_SIZE = 500             # 運算分塊大小：每次運算處理的組合數量，過大可能導致 UI 卡頓，過小可能增加總運算時間

# 標準電阻表
E96_BASE = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 
    1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 
    1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 
    2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 
    3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 
    5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76, 0
]
E24_BASE = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1, 0
]