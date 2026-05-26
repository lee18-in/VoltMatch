# -*- coding: utf-8 -*-
import os
import sys
import math
import numpy as np
import config

def get_resource_path(relative_path):
    """ 取得資源檔案的絕對路徑，相容開發與打包環境 """
    if getattr(sys, 'frozen', False) or "__compiled__" in globals():
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_resistor_list(base_values, include_zero=True):
    """ 根據基值產生完整電阻列表 """
    multipliers = [1, 10, 100, 1000, 10000, 100000, 1000000]
    vals = [b * m for m in multipliers for b in base_values]
    if include_zero: vals.append(0.0)
    arr = np.array(vals, dtype=float)
    arr = np.round(arr, config.PRECISION_DIGITS)
    return np.unique(arr)

def generate_sig_figs(base_list):
    """ 產生標準電阻的有效數字集合 (乘以100後取整數) """
    return set(int(round(x * 100)) for x in base_list)

E24_SIGS = generate_sig_figs(config.E24_BASE)
E96_SIGS = generate_sig_figs(config.E96_BASE)

def fmt_rkm(val):
    """ 將數值格式化為 R/K/M (BS 1852) """
    if val is None: return ""
    try:
        val = float(val)
        if val == 0: return "0R"
    except (ValueError, TypeError):
        return str(val)
    try:
        if val >= 1_000_000: unit, num = 'M', val / 1_000_000
        elif val >= 1_000:   unit, num = 'K', val / 1_000
        else:                unit, num = 'R', val
        s = f"{float(f'{num:.4g}')}"
        if s.endswith(".0"): return s[:-2] + unit
        elif "." in s: return s.replace(".", unit)
        else: return s + unit
    except Exception:
        return str(val)

def determine_r_color(val):
    """ 判斷電阻值的顏色 (E24/E96) """
    if val <= 0: return config.C_RED
    try:
        exponent = math.floor(math.log10(val))
        mantissa = round(val / (10 ** exponent), 2)
        mantissa_int = int(round(mantissa * 100))
        if mantissa_int in E24_SIGS: return config.C_GREEN
        elif mantissa_int in E96_SIGS: return config.C_YELLOW
        else: return config.C_RED
    except Exception: return config.C_RED

def calc_gradient_hex(ratio):
    """ 計算 綠 -> 黃 -> 紅 -> 紫 的漸層 HEX """
    ratio = max(0.0, min(1.0, ratio))
    if ratio <= 0.33:
        r = ratio / 0.33
        s, e = (192, 255, 192), (255, 255, 192) # Green -> Yellow
    elif ratio <= 0.66:
        r = (ratio - 0.33) / 0.33
        s, e = (255, 255, 192), (255, 192, 192) # Yellow -> Red
    else:
        r = (ratio - 0.66) / 0.34
        s, e = (255, 192, 192), (255, 192, 255) # Red -> Purple
    rgb = tuple(int(s[i] + (e[i] - s[i]) * r) for i in range(3))
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"