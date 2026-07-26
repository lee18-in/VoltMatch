# -*- coding: utf-8 -*-
"""分壓電路的核心數學。

本模組刻意不 import 任何東西：沒有 UI、沒有 numpy、沒有 config，
純量與 numpy 陣列都能直接運算 (靠運算子多載)，因此可以原封不動搬到
其他前端 (Web / API / CLI) 重用。新增內容前請維持這個「零依賴」性質。

分壓關係式：

    V_Out = V_Ref * (1 + R_high / R_Low)

四個參數任三個已知即可解出第四個。
"""


def calc_v_out(v_ref, r_high, r_low):
    """分壓正解本體，不做除零檢查 (呼叫端負責)。

    刻意不加保護是為了讓搜尋演算法能直接餵入 numpy 陣列做向量化運算；
    需要保護的單點計算請改用 solve_v_out()。
    """
    return v_ref * (1 + r_high / r_low)


# ------------------------------------------------------------------
# 以下為單點反解 (Quick Solver 用)。
# 無解或除數為 0 時一律回傳 0.0，與原本 Quick Solver 的顯示行為一致。
# ------------------------------------------------------------------

def solve_v_out(v_ref, r_high, r_low):
    """已知 V_Ref / R_high / R_Low，求 V_Out。"""
    if r_low == 0:
        return 0.0
    return calc_v_out(v_ref, r_high, r_low)


def solve_r_high(v_ref, v_out, r_low):
    """已知 V_Ref / V_Out / R_Low，求 R_high。"""
    if v_ref == 0:
        return 0.0
    return r_low * (v_out / v_ref - 1)


def solve_r_low(v_ref, v_out, r_high):
    """已知 V_Ref / V_Out / R_high，求 R_Low。"""
    if v_ref == 0:
        return 0.0
    ratio = v_out / v_ref - 1
    if ratio == 0:
        return 0.0
    return r_high / ratio


def solve_v_ref(v_out, r_high, r_low):
    """已知 V_Out / R_high / R_Low，求 V_Ref。"""
    if r_low == 0:
        return 0.0
    ratio = 1 + r_high / r_low
    if ratio == 0:
        return 0.0
    return v_out / ratio
