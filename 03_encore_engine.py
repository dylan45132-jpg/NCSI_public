import pandas as pd
import numpy as np
import os
'''
ENCORE評級轉換和Mandle圖層權重計算邏輯：
1. 定義評級轉換字典(RATING_TO_WEIGHT)，將ENCORE文件中的文字評級轉換為數值權重。
2. 定義默認值(NAN_DEFAULT)，用於處理ENCORE文件中未提及的評級，默認為0.30。
3. 定義ENCORE服務與Mandle圖層的對應關係(ENCORE_TO_MANDLE)，將ENCORE中的服務與Mandle原始圖資、Bio圖資對應，並指派權重。
4. 定義生物多樣性相關圖層(BIO_LAYERS)和其固定權重(BIO_WEIGHT)，因為ENCORE未提及生物多樣性相關指標，因此默認權重為0.30。
5. 建立get_mandle_weights函數，根據輸入的ISIC代碼列表和整理完的ENCORE數據(df)，計算Mandle圖層權重。
    該函數會處理ISIC代碼的完全匹配和前綴匹配，並根據ENCORE服務評級計算對應Mandle圖層的權重，
    最後返回一個字典，將Mandle/Bio圖層名稱映射到其計算出的權重。
6. 建立get_available_layers函數，檢查給定的圖層文件路徑字典中哪些文件存在，返回存在的圖層名稱列表。

預期最終輸出：
{
  "sediment": 0.75,
  "nitrogen": 0.50,
  "coastal": 0.25,
  ...
}
'''
# 將ENCORE文件內的文字評級轉換為數值權重
RATING_TO_WEIGHT = {
    "VH": 1.00,
    "H": 0.75,
    "M": 0.50,
    "L": 0.25,
    "VL": 0.10,
    "N/A": 0.00,
    "ND": 0.00
}

# ENCORE文件中未提及的則默認為0.30
NAN_DEFAULT = 0.30

# 將ENCORE中的服務與Mandle原始圖資、Bio圖資對應，並指派權重
ENCORE_TO_MANDLE = {
    "Soil and sediment retention": {"sediment": 1.0},
    "Water purification": {"nitrogen": 1.0, "sediment": 0.5},
    "Flood mitigation services": {"coastal": 1.0, "sediment": 0.5},
    "Storm mitigation": {"coastal": 1.0},
    "Water flow regulation": {"sediment": 0.5, "nitrogen": 0.5},
    "Water supply": {"sediment": 0.5, "nitrogen": 0.5},
    "Soil quality regulation": {"sediment": 0.5},
    "Local (micro and meso) climate regulation": {"nature_access": 0.5},
    "Recreation related services": {"nature_access": 1.0},
    "Visual amenity services": {"nature_access": 0.5},
    "Education, scientific and research services": {"nature_access": 0.5},
    "Spiritual, artistic and symbolic services": {"nature_access": 0.5}
}

# ENCORE未提及生物多樣性相關指標，因此默認權重為0.30
BIO_LAYERS = ["species", "red_list", "endemic", "kba"]
BIO_WEIGHT = NAN_DEFAULT

def get_mandle_weights(isic_codes: list, encore_df: pd.DataFrame) -> dict:
    """
    計算Mandle圖層權重，根據輸入的ISIC代碼列表和整理完的ENCORE數據(df)。
    
    Args:
        isic_codes: 要計算的ISIC代碼列表，用於對照ENCORE數據，計算權重。
        encore_df: 整理完成的ENCORE依賴數據的DataFrame。
        
    Returns:
        字典，將Mandle/Bio圖層名稱映射到其計算出的權重。
    
    ENCORE df裡面有isic_code欄位
    """
    all_scores = {}
    
    for isic_code in isic_codes:
        # Exact match
        matches = encore_df[encore_df["ISIC Unique code"] == isic_code]
        match_type = "Exact"
        
        # 如果沒有完全匹配的ISIC代碼，嘗試使用前綴匹配（例如C_23_231可以匹配C_23）
        if matches.empty:
            matches = encore_df[encore_df["ISIC Unique code"].str.startswith(f"{isic_code}_")]
            match_type = "Prefix"
            
        if matches.empty:
            print(f"Warning: ISIC code '{isic_code}' not found.")
            continue
            
        print(f"[{match_type} Match] ISIC: {isic_code} -> Found {len(matches)} rows")
        
        isic_scores = {}
        
        for col, mandle_mapping in ENCORE_TO_MANDLE.items(): # 拆成鍵值對, key是ENCORE的服務名稱, value是對應的Mandle圖層和權重
            if col not in encore_df.columns:
                continue
            # 把matches後的col欄位值轉換為字串並去除空白    
            col_values = matches[col].astype(str).str.strip()
            mapped_values = []
            # 根據RATING_TO_WEIGHT字典將評級轉換為數值權重，並處理缺失值
            for val in col_values:
                if val in RATING_TO_WEIGHT: # 對照評級字典轉換為數值權重
                    mapped_values.append(RATING_TO_WEIGHT[val]) # 如果評級在字典中，則使用對應的權重
                elif str(val).lower() == 'nan': # 處理 float NaN 或字串形式的 nan
                    mapped_values.append(NAN_DEFAULT)
                else:
                    mapped_values.append(NAN_DEFAULT)
                    
            avg_rating = np.mean(mapped_values) if mapped_values else NAN_DEFAULT # 計算平均評級，如果沒有有效評級則使用默認值
            
            for mandle_layer, layer_weight in mandle_mapping.items(): # 把 {"sediment": 1.0}這樣的對應關係拆成鍵值對, key是Mandle圖層名稱, value是對應的權重
                score = avg_rating * layer_weight
                # 將分數累加到對應的Mandle圖層上，如果同一ISIC對應多個ENCORE服務，則分數會累加
                isic_scores[mandle_layer] = isic_scores.get(mandle_layer, 0.0) + score
                
        # 將當前ISIC代碼的分數添加到總分數字典中，為每個Mandle圖層建立一個分數列表，以便後續平均
        for layer, score in isic_scores.items():
            # 用setdefault，若layer不存在則初始化為空列表，然後append當前score
            all_scores.setdefault(layer, []).append(score)
            
    final_weights = {}
    # 對每個Mandle圖層計算平均分數，作為最終權重
    for layer, scores in all_scores.items():
        final_weights[layer] = np.mean(scores)
        
    # 對於ENCORE未提及的生物多樣性相關圖層，直接賦予默認權重
    for bio_layer in BIO_LAYERS:
        final_weights[bio_layer] = BIO_WEIGHT
        
    return final_weights


if __name__ == "__main__":
    csv_path = "data/encore_dependency.csv"
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        exit(1) # 異常結束
        
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns] # strip去除表頭空白字元
    
    # 確保"ISIC Unique code"欄位存在且格式正確
    if "ISIC Unique code" in df.columns:
        df["ISIC Unique code"] = df["ISIC Unique code"].astype(str).str.strip()
    else:
        print("Error: 'ISIC Unique code' column not found in CSV.")
        exit(1)

    # 測試用ISIC代碼    
    # test_cases = [
    #     ["B_08_081", "C_23"],
    #     ["C_23_231"]
    # ]
    
    # for i, test_case in enumerate(test_cases, 1):
    #     print(f"\n--- Test Case {i}: {test_case} ---")
    #     weights = get_mandle_weights(test_case, df)
    #     print("\nLayer Weights:")
    #     for k, v in weights.items():
    #         suffix = " (固定)" if k in BIO_LAYERS else ""
    #         print(f"  {k}: {v:.4f}{suffix}")
