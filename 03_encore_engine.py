import pandas as pd
import numpy as np
import os

RATING_TO_WEIGHT = {
    "VH": 1.00,
    "H": 0.75,
    "M": 0.50,
    "L": 0.25,
    "VL": 0.10,
    "N/A": 0.00,
    "ND": 0.00
}

NAN_DEFAULT = 0.30

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

BIO_LAYERS = ["species", "red_list", "endemic", "kba"]
BIO_WEIGHT = NAN_DEFAULT

def get_mandle_weights(isic_codes: list, encore_df: pd.DataFrame) -> dict:
    """
    Calculate Mandle layer weights based on ISIC codes and ENCORE dependency matrix.
    
    Args:
        isic_codes: List of ISIC unique codes to query.
        encore_df: DataFrame containing the ENCORE dependency data.
        
    Returns:
        Dictionary mapping Mandle/Bio layer names to their calculated weights.
    """
    all_scores = {}
    
    for isic_code in isic_codes:
        # Exact match
        matches = encore_df[encore_df["ISIC Unique code"] == isic_code]
        match_type = "Exact"
        
        # Prefix match
        if matches.empty:
            matches = encore_df[encore_df["ISIC Unique code"].str.startswith(f"{isic_code}_")]
            match_type = "Prefix"
            
        if matches.empty:
            print(f"Warning: ISIC code '{isic_code}' not found.")
            continue
            
        print(f"[{match_type} Match] ISIC: {isic_code} -> Found {len(matches)} rows")
        
        isic_scores = {}
        
        for col, mandle_mapping in ENCORE_TO_MANDLE.items():
            if col not in encore_df.columns:
                continue
                
            col_values = matches[col].astype(str).str.strip()
            mapped_values = []
            for val in col_values:
                if val in RATING_TO_WEIGHT:
                    mapped_values.append(RATING_TO_WEIGHT[val])
                elif val.lower() == 'nan':
                    mapped_values.append(NAN_DEFAULT)
                else:
                    mapped_values.append(NAN_DEFAULT)
                    
            avg_rating = np.mean(mapped_values) if mapped_values else NAN_DEFAULT
            
            for mandle_layer, layer_weight in mandle_mapping.items():
                score = avg_rating * layer_weight
                # Accumulate scores from different ENCORE categories for the same ISIC
                isic_scores[mandle_layer] = isic_scores.get(mandle_layer, 0.0) + score
                
        # Store scores for this ISIC
        for layer, score in isic_scores.items():
            all_scores.setdefault(layer, []).append(score)
            
    final_weights = {}
    # Average the scores across multiple ISIC codes
    for layer, scores in all_scores.items():
        final_weights[layer] = np.mean(scores)
        
    # Append BIO_LAYERS with fixed weight
    for bio_layer in BIO_LAYERS:
        final_weights[bio_layer] = BIO_WEIGHT
        
    return final_weights

def get_available_layers(raster_paths: dict) -> list:
    """
    Check which raster files exist.
    
    Args:
        raster_paths: Dictionary mapping layer names to their file paths.
        
    Returns:
        List of layer names where the corresponding file exists.
    """
    return [name for name, path in raster_paths.items() if os.path.exists(path)]

if __name__ == "__main__":
    csv_path = "data/encore_dependency.csv"
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        exit(1)
        
    # Read CSV and strip column names
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    
    # Ensure ISIC column is treated as string and stripped
    if "ISIC Unique code" in df.columns:
        df["ISIC Unique code"] = df["ISIC Unique code"].astype(str).str.strip()
    else:
        print("Error: 'ISIC Unique code' column not found in CSV.")
        exit(1)
        
    test_cases = [
        ["B_08_081", "C_23"],
        ["C_23_231"]
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case} ---")
        weights = get_mandle_weights(test_case, df)
        print("\nLayer Weights:")
        for k, v in weights.items():
            suffix = " (固定)" if k in BIO_LAYERS else ""
            print(f"  {k}: {v:.4f}{suffix}")
