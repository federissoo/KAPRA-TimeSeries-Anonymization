import pandas as pd
import numpy as np
import sys
import os
from kapra_utils import calculate_envelope_and_vl

# Parametro K richiesto dal modello (k,P)-anonimato
K = 3

# Mappings per la generalizzazione dei QI categorici


def isKAnon(dataset, k, QI):
    """Verifica se il dataset soddisfa il k-anonimato per i QI indicati."""
    df = pd.DataFrame(dataset) if isinstance(dataset, list) else dataset
    if df.empty: return False
    
    df_check = df.copy()
    for col in QI:
        df_check[col] = df_check[col].astype(str)
        
    group_sizes = df_check.groupby(QI).size()
    return group_sizes.min() >= k



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

def makeDatasetKAnon(dataset, k, qi_cat=None, time_cols=None):
    """
    Algorithm to find optimal time-series partitioning.
    Cost Function = (Average_VL / Normalization_Constant)
    """
    if time_cols is None:
        # Fallback if not provided (should not happen with new calls)
        time_cols = [c for c in dataset[0].keys() if c.startswith('H')]

    # Normalization factor for VL (heuristic: max expected VL approx 40?)
    VL_WEIGHT = 0.5 

    # 1. Apply Mondrian Clustering on the whole dataset (or per group if we had categorical QIs)
    # Since we removed Dept/Seniority, we treat the whole dataset as one group initially
    # or if there are other QIs passed in qi_cat, we group by them.
    # The user asked to remove Dept/Seniority as attributes. 
    # If qi_cat is empty, we just partition the whole dataset.
    
    current_dataset = []
    for row in dataset:
        current_dataset.append(row.copy())
    
    df_curr = pd.DataFrame(current_dataset)
    
    # If qi_cat is provided and not empty, group by it. Otherwise single group.
    if qi_cat:
        grouped = df_curr.groupby(qi_cat)
    else:
        # Dummy group
        grouped = [('All', df_curr)]
        
    all_partitions = []
    
    for _, group in grouped:
        # Check size constraint
        if len(group) < k:
            # Cannot satisfy k-anon even before splitting
            return None, (None, None)
        
        # 3. Apply Mondrian Clustering on this group
        group_list = group.to_dict('records')
        partitions = partition_dataset(group_list, k, time_cols)
        all_partitions.extend(partitions)
    
    # Calculate Cost
    avg_vl = calculate_partition_cost(all_partitions, time_cols)
    
    # Assign GroupIDs
    final_dataset = []
    for gid, part in enumerate(all_partitions, start=1):
        for row in part:
            row['GroupID'] = gid
            final_dataset.append(row)
    
    return final_dataset, (0, 0) # Returning dummy levels for compatibility check

if __name__ == "__main__":
    pass # Implementation moved to function logic mostly