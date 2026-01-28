import pandas as pd
import numpy as np
import sys
import os
from kapra_utils import calculate_envelope_and_vl

# Parametro K richiesto dal modello (k,P)-anonimato
K = 3

# Mappings per la generalizzazione dei QI categorici
dept_mapping = {
    "IT": "Technical",
    "Sales": "Commercial", 
    "Marketing": "Commercial",
    "HR": "Administrative",
    "Technical": "*",
    "Commercial": "*",
    "Administrative": "*",
    "*": "*"
}

seniority_mapping = {
    "Junior": "Non-Senior",
    "Mid": "Non-Senior",
    "Senior": "Senior",
    "Non-Senior": "*",
    "Senior": "*",
    "*": "*"
}

def isKAnon(dataset, k, QI):
    """Verifica se il dataset soddisfa il k-anonimato per i QI indicati."""
    df = pd.DataFrame(dataset) if isinstance(dataset, list) else dataset
    if df.empty: return False
    
    df_check = df.copy()
    for col in QI:
        df_check[col] = df_check[col].astype(str)
        
    group_sizes = df_check.groupby(QI).size()
    return group_sizes.min() >= k

def generalizeCategorical(value, level, mapping):
    """Applica la gerarchia di generalizzazione per gli attributi categorici."""
    for _ in range(level):
        if value in mapping:
            value = mapping[value]
    return value

def partition_dataset(dataset, k, time_cols):
    """
    Mondrian-like Top-Down Greedy Partitioning on Time Series columns.
    Splits the dataset recursively to minimize envelope size (proxy for VL).
    """
    # 1. Base case: Cannot split if size < 2*k
    if len(dataset) < 2 * k:
        return [dataset]
    
    # 2. Find dimension to split (widest range)
    # We want to minimize the envelope, so we cut the dimension with largest spread.
    best_col = None
    max_spread = -1
    
    # Extract columns to numpy for speed
    data_df = pd.DataFrame(dataset)
    
    for col in time_cols:
        try:
            vals = data_df[col].values
            spread = np.max(vals) - np.min(vals)
            if spread > max_spread:
                max_spread = spread
                best_col = col
        except Exception:
            continue
            
    if best_col is None or max_spread == 0:
        return [dataset] # Cannot split
    
    # 3. Sort and Split
    dataset.sort(key=lambda x: x[best_col])
    mid = len(dataset) // 2
    
    lhs = dataset[:mid]
    rhs = dataset[mid:]
    
    # 4. Check K-constraint and Recurse
    if len(lhs) >= k and len(rhs) >= k:
        return partition_dataset(lhs, k, time_cols) + partition_dataset(rhs, k, time_cols)
    else:
        # If strict median split violates k (e.g. many duplicates), try to adjust?
        # For simple Mondrian, we just stop.
        return [dataset]

def calculate_partition_cost(partitions, time_cols):
    """
    Calculates the average Value Loss (VL) of the partitions.
    """
    total_vl = 0
    total_records = 0
    
    for part in partitions:
        _, _, vl = calculate_envelope_and_vl(pd.DataFrame(part)[time_cols])
        total_vl += (vl * len(part)) # Weighted by size
        total_records += len(part)
        
    if total_records == 0: return float('inf')
    return total_vl / total_records

def makeDatasetKAnon(dataset, k, qi_cat, time_cols=None):
    """
    Algorithm to find minimal categorical generalization + optimal time-series partitioning.
    Cost Function = Categorical_Levels + (Average_VL / Normalization_Constant)
    """
    if time_cols is None:
        # Fallback if not provided (should not happen with new calls)
        time_cols = [c for c in dataset[0].keys() if c.startswith('H')]

    best_result = None
    min_global_cost = float('inf')
    
    # Normalization factor for VL (heuristic: max expected VL approx 40?)
    # We want Cat Levels (0-4) to be comparable to VL. 
    # Let's say we weight VL by 0.1 to favor structure preservation?
    # Or just sum them.
    VL_WEIGHT = 0.5 

    # Livelli massimi: Dept (0->1->2), Seniority (0->1->2)
    for dept_level in range(3):
        for seniority_level in range(3):
            # 1. Apply Categorical Generalization
            current_dataset = []
            for row in dataset:
                new_row = row.copy()
                new_row['Dept'] = generalizeCategorical(row['Dept'], dept_level, dept_mapping)
                new_row['Seniority'] = generalizeCategorical(row['Seniority'], seniority_level, seniority_mapping)
                current_dataset.append(new_row)
            
            # 2. Check if Categorical Grouping satisfies K (Candidate Blocks)
            # Mondrian needs the *initial* blocks to be >= K (actually >= 2K to be splittable, but >= K to be valid leaves)
            # If a categorical block is < K, we can't fix it by splitting. We must merge categoricals (increase level).
            
            df_curr = pd.DataFrame(current_dataset)
            grouped = df_curr.groupby(qi_cat)
            
            valid_categorical = True
            all_partitions = []
            
            for _, group in grouped:
                if len(group) < k:
                    valid_categorical = False
                    break
                
                # 3. Apply Mondrian Clustering on this group
                group_list = group.to_dict('records')
                partitions = partition_dataset(group_list, k, time_cols)
                all_partitions.extend(partitions)
            
            if valid_categorical:
                # Calculate Cost
                avg_vl = calculate_partition_cost(all_partitions, time_cols)
                cat_cost = dept_level + seniority_level
                
                global_cost = cat_cost + (avg_vl * VL_WEIGHT)
                
                if global_cost < min_global_cost:
                    min_global_cost = global_cost
                    # Assign GroupIDs
                    final_dataset = []
                    for gid, part in enumerate(all_partitions, start=1):
                        for row in part:
                            row['GroupID'] = gid
                            final_dataset.append(row)
                    
                    best_result = (final_dataset, (dept_level, seniority_level), avg_vl)
                    
                    # Optimization: If cost is very low?
                    
    if best_result:
        ds, levels, vl = best_result
        return ds, levels
    else:
        return None, (None, None)

if __name__ == "__main__":
    pass # Implementation moved to function logic mostly