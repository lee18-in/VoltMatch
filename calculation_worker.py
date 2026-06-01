# -*- coding: utf-8 -*-
import time
import traceback
import numpy as np
import config
import utils

def worker_calculation(p, msg_queue): # 背景計算函數
    """ 子執行緒：Numpy 運算與原生 Python 資料處理 """ # 函數說明
    try: # 嘗試執行
        msg_queue.put(("status", ("Initializing resistor database...", "blue"))) # 發送狀態訊息
        
        # --- 準備電阻庫 (保持不變) ---
        r_all = np.unique(np.concatenate((utils.get_resistor_list(config.E96_BASE), utils.get_resistor_list(config.E24_BASE)))) # 產生所有電阻值
        r_all = np.round(r_all, config.PRECISION_DIGITS) # 四捨五入
        e24_full_list = np.round(utils.get_resistor_list(config.E24_BASE), config.PRECISION_DIGITS) # 產生 E24 電阻值列表
        
        if p['r_low_mode'] == "Locked": # 若 R_Low 為鎖定模式
            r_low_rng = np.array([p['r_low_lock']]) # 設定為鎖定值
        else: # 若為掃描模式
            r_low_rng = r_all[(r_all >= p['r_low_min']) & (r_all <= p['r_low_max'])] # 篩選範圍內的電阻
            if p['r_low_e24']: # 若限制 E24
                 r_low_rng = r_low_rng[np.isin(r_low_rng, e24_full_list)] # 篩選 E24 電阻
        r_low_rng = r_low_rng[r_low_rng > 0] # 移除 0 或負值
        
        if len(r_low_rng) == 0: # 若無有效 R_Low
            msg_queue.put(("error", "No valid R_Low found in the specified range.")) # 發送錯誤訊息
            return # 結束函數

        r_hi1_rng = r_all[(r_all >= p['r_hi_min']) & (r_all <= p['r_hi_max'])] # 篩選 R_Hi1 範圍
        if p['r_hi1_e24']: # 若限制 E24
            r_hi1_rng = r_hi1_rng[np.isin(r_hi1_rng, e24_full_list)] # 篩選 E24 電阻
        
        if p['r_hi_mode'] == "Disable": # 若 R_Hi2 停用
            r_hi2_rng = np.array([0.0]) # 設定為 0
        else: # 若為掃描模式
            r_hi2_rng = r_all[(r_all >= p['r_hi_min']) & (r_all <= p['r_hi_max'])] # 篩選 R_Hi2 範圍
            if p['r_hi2_e24']: # 若限制 E24
                r_hi2_rng = r_hi2_rng[np.isin(r_hi2_rng, e24_full_list)] # 篩選 E24 電阻

        if len(r_hi1_rng) * len(r_hi2_rng) > 50_000_000: # 若搜尋空間過大
            msg_queue.put(("error", "Search space too large (>50M). Please reduce range.")) # 發送錯誤訊息
            return # 結束函數

        msg_queue.put(("status", ("Generating combination matrix...", "blue"))) # 發送狀態訊息
        
        current_tol = p['tol'] # 取得目前容差
        MAX_RETRY_LIMIT = 40 # 設定最大重試次數
        retry_count = 0 # 初始化重試計數
        final_rows = [] # 初始化結果列表
        
        while retry_count < MAX_RETRY_LIMIT: # 迴圈重試
            
            # [ROMANCE] 每次迴圈開始，更新介面滑塊位置
            # 這樣你可以看到滑塊跳到新的位置，準備開始掃描
            msg_queue.put(("update_tol", current_tol)) # 發送更新容差訊息
            
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
                    msg_queue.put(("status", (f"Scanning... {current_tol:.4f}% (Attempt {retry_count})", "orange"))) # 發送狀態訊息
                
                chunk = r_low_rng[i:i+chunk_size] # 取得目前區塊
                for rl in chunk: # 遍歷區塊內的 R_Low
                    t_min, t_max = rl * k_min, rl * k_max # 計算目標範圍
                    mask = (flat >= t_min) & (flat <= t_max) # 建立遮罩
                    if np.any(mask): # 若有符合的組合
                        idxs = np.where(mask)[0] # 取得索引
                        valid_idx.append(idxs) # 加入有效索引列表
                        valid_rlow.append(np.full(len(idxs), rl)) # 加入對應的 R_Low
            
            # --- 無解處理 (放寬 - 滑塊會往右跳) ---
            if not valid_idx:  # 進入無解處理邏輯：當前容差範圍內找不到任何組合 # 若無解
                if current_tol >= config.MAX_TOLERANCE: # 檢查是否已達到系統設定的最大容差上限 (例如 3%) # 若已達最大容差
                    msg_queue.put(("error", f"No solution found within max tolerance ({config.MAX_TOLERANCE}%).")) # 回報錯誤給主介面並終止 # 發送錯誤訊息
                    return # 結束函數
                
                new_tol = (current_tol + (config.MIN_TOLERANCE*100 )) * 10  # 自動放寬演算法：採用階梯式倍增，確保能快速跳出死胡同 # 計算新容差
                current_tol = round(new_tol, config.PRECISION_DIGITS)  # 四捨五入以保持滑塊數值整潔，避免浮點數細微誤差 # 更新目前容差
                
                msg_queue.put(("status", (f"Relaxing tolerance... -> {current_tol:.4f}%", "purple")))  # 更新狀態列顏色為紫色，提示使用者正在放寬條件 # 發送狀態訊息
                # 滑塊將在下一次迴圈開頭更新
                continue # 繼續下一次迴圈

            msg_queue.put(("status", ("Processing results...", "blue"))) # 發送狀態訊息
            
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
                 msg_queue.put(("status", (f"Optimizing... {current_tol:.4f}% -> {new_shrink_tol:.4f}% ({total_n} found)", "purple"))) # 發送狀態訊息
                 current_tol = new_shrink_tol # 更新目前容差
                 retry_count += 1 # 增加重試計數
                 # 滑塊將在下一次迴圈開頭更新
                 continue # 繼續下一次迴圈
            else: # 若結果數未超過限制
                final_rows.sort(key=lambda x: x['V_Dev']) # 依誤差排序
                msg_queue.put(("success", (final_rows, current_tol))) # 發送成功訊息
                return # 結束函數

        # Retry 次數用盡
        final_rows.sort(key=lambda x: x['V_Dev']) # 依誤差排序
        if len(final_rows) > p['limit']: # 若結果數超過限制
             final_rows = final_rows[:p['limit']] # 截斷結果
        msg_queue.put(("success", (final_rows, current_tol))) # 發送成功訊息
        
    except Exception as e: # 捕捉例外
        traceback.print_exc() # 印出堆疊
        msg_queue.put(("error", str(e))) # 發送錯誤訊息
