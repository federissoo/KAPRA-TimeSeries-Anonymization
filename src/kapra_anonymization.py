import pandas as pd
import numpy as np
import time
import os
import sys

# Add src to path to import utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.sax_utils import ts_to_sax, calculate_pattern_loss, sax_to_values
from src.kapra_utils import calculate_envelope_and_vl

# --- Configuration ---
K = 8
P = 2
SAX_LEVEL = 8
N_SEGMENTS = 4

def load_data(filepath):
    """Load the dataset."""
    return pd.read_csv(filepath)

def get_time_series(df):
    """Extract time series columns (H1..H8) as a numpy array."""
    ts_cols = [c for c in df.columns if c.startswith('H')]
    return df[ts_cols].values

def calculate_group_vl(group_records):
    """Calculate Value Loss for a group of records."""
    if len(group_records) == 0:
        return 0.0
    ts_data = np.array([r['timeseries'] for r in group_records])
    _, _, vl = calculate_envelope_and_vl(ts_data)
    return vl

def calculate_merge_cost(group1_records, group2_records):
    """
    Calculate the cost of merging two groups.
    Cost is defined as the increase in VL or the resulting VL.
    Here we use the resulting VL of the combined group.
    """
    combined = group1_records + group2_records
    return calculate_group_vl(combined)

def main():
    start_time = time.time()
    
    # 1. Load Data
    data_path = os.path.join(os.path.dirname(__file__), '../docs/data/dataset_raw.csv')
    if not os.path.exists(data_path):
         # Fallback for running from src directly
         data_path = os.path.join(os.path.dirname(__file__), '../../docs/data/dataset_raw.csv')
    
    print(f"Loading data from {data_path}...")
    df = load_data(data_path)
    ts_data = get_time_series(df)
    
    # Prepare records with metadata
    records = []
    for idx, row in df.iterrows():
        ts = ts_data[idx]
        records.append({
            'original_index': idx,
            'timeseries': ts,
            'row_data': row,
            'sax': '', # To be filled
            'group_id': None
        })
        
    print(f"Total records: {len(records)}")
    
    # ==========================================
    # Phase 1: Initial Grouping (Pattern Creation)
    # ==========================================
    print("\n--- Phase 1: Initial Grouping ---")
    
    # Convert to SAX and group
    groups = {} # sax_string -> list of records
    
    for r in records:
        sax = ts_to_sax(r['timeseries'], level=SAX_LEVEL, n_segments=N_SEGMENTS)
        r['sax'] = sax
        if sax not in groups:
            groups[sax] = []
        groups[sax].append(r)
        
    p_groups = []   # List of dicts: {'sax': str, 'records': list, 'type': 'good'}
    bad_leaves = [] # List of dicts: {'sax': str, 'records': list, 'type': 'bad'}
    
    for sax, group_records in groups.items():
        group_info = {'sax': sax, 'records': group_records}
        if len(group_records) >= P:
            group_info['type'] = 'good'
            p_groups.append(group_info)
        else:
            group_info['type'] = 'bad'
            bad_leaves.append(group_info)
            
    print(f"P-groups (Good Leaves): {len(p_groups)}")
    print(f"Bad Leaves: {len(bad_leaves)}")
    
    # ==========================================
    # Phase 2: Recycle Bad-Leaves
    # ==========================================
    print("\n--- Phase 2: Recycle Bad-Leaves ---")
    
    if not p_groups and bad_leaves:
        # Edge case: No P-groups exist initially. 
        # Should create at least one P-group from largest bad leaves or force merge?
        # For this implementation, we assume at least one P-group usually exists.
        # If not, we might treat the largest bad leaf as a P-group (if >= P not met, but that contradicts definition).
        # Let's panic-merge bad leaves to form a P-group if needed or just skip.
        print("Warning: No P-groups found. Bad leaves cannot be recycled properly.")
    
    for bad_group in bad_leaves:
        # Calculate representative for bad group (mean)
        bad_ts = np.array([r['timeseries'] for r in bad_group['records']])
        bad_mean_ts = np.mean(bad_ts, axis=0)
        
        best_p_group = None
        min_dist = float('inf')
        
        # Find nearest P-group
        for p_group in p_groups:
            p_ts = np.array([r['timeseries'] for r in p_group['records']])
            p_mean_ts = np.mean(p_ts, axis=0)
            
            # Euclidean distance between means
            dist = np.linalg.norm(bad_mean_ts - p_mean_ts)
            
            if dist < min_dist:
                min_dist = dist
                best_p_group = p_group
        
        if best_p_group:
            # Move records to best P-group
            # Update SAX of moved records to match P-group
            target_sax = best_p_group['sax']
            for r in bad_group['records']:
                r['sax'] = target_sax 
                best_p_group['records'].append(r)
        else:
            # Should not happen if p_groups is not empty
            print(f"Could not recycle bad group {bad_group['sax']}")

    # Reform the list of groups (now all are technically P-groups or candidate groups)
    # Filter out empty bad groups (they were moved)
    # Actually, we just use p_groups now, as bad_leaves content was moved into them.
    # What if a bad_leaf was not moved? (Only if no P-groups exist).
    
    current_groups = p_groups
    print(f"Groups after Phase 2: {len(current_groups)}")
    
    # ==========================================
    # Phase 3: Formation of K-groups
    # ==========================================
    print("\n--- Phase 3: Formation of K-groups ---")
    
    # We need to ensure every group has size >= K.
    # Greedy approach:
    # 1. Identify groups with size < K.
    # 2. Pick one, merge with nearest group (minimizing VL increase).
    # 3. Repeat until all >= K.
    
    while True:
        # Identify invalid groups
        invalid_indices = [i for i, g in enumerate(current_groups) if len(g['records']) < K]
        
        if not invalid_indices:
            break # All valid
            
        # Pick one invalid group (e.g., the smallest)
        # Sort invalid indices by size of group to pick smallest first
        invalid_indices.sort(key=lambda i: len(current_groups[i]['records']))
        idx_to_merge = invalid_indices[0]
        group_to_merge = current_groups[idx_to_merge]
        
        # Find best merge partner
        best_partner_idx = -1
        min_merge_cost = float('inf')
        
        for i, other_group in enumerate(current_groups):
            if i == idx_to_merge:
                continue
                
            # Calculate cost (VL of combined group)
            cost = calculate_merge_cost(group_to_merge['records'], other_group['records'])
            
            if cost < min_merge_cost:
                min_merge_cost = cost
                best_partner_idx = i
                
        if best_partner_idx != -1:
            # Merge
            partner_group = current_groups[best_partner_idx]
            
            # Combine records
            # Which SAX pattern to keep?
            # Usually strict KAPRA keeps pattern of the larger group or re-computes?
            # The prompt says: "Uniscilo al P-group più vicino...".
            # Usually we adopt the pattern of the dominating group or keep them separate in terms of pattern but same ID?
            # "Importante: I record spostati 'adottano' il pattern del P-group ospitante" applies to Phase 2.
            # In Phase 3, we are merging P-groups.
            # Let's assume we maintain the pattern of the destination (partner) or just treat them as a group.
            # BUT the output requires "Pattern". If a group has mixed patterns, that's an issue.
            # However, in Phase 1 & 2 we aligned patterns.
            # If we merge two P-groups with DIFFERENT patterns, the final group will have mixed patterns logically.
            # BUT KAPRA goal is Pattern Retention.
            # The paper says Phase 3 forms K-groups.
            # Usually we treat the final group as having a "representative" pattern or we report the pattern of the majority?
            # Or - maybe we don't change the pattern in Phase 3, but they share the same GroupID and calculating VL is on values.
            # The prompt asks for "Pattern (il pattern SAX finale del gruppo)".
            # If we merge, we should probably pick one pattern.
            # Let's pick the pattern of the larger group (or partner).
            
            # MERGING
            merged_records = group_to_merge['records'] + partner_group['records']
            
            # Decide dominating pattern
            if len(partner_group['records']) >= len(group_to_merge['records']):
                dom_sax = partner_group['sax']
            else:
                dom_sax = group_to_merge['sax']
                
            # Update records' sax to dominating pattern?
            # If we want "Pattern Retention", maybe we shouldn't overwrite it if they were distinct valid P-groups?
            # But for the output CSV, we have one "Pattern" column per group.
            # So we effectively generalize the pattern too.
            for r in merged_records:
                r['sax'] = dom_sax
                
            new_group = {
                'sax': dom_sax,
                'records': merged_records,
                'type': 'merged'
            }
            
            # Remove old groups and add new one
            # Be careful with indices since we change the list
            # Easier to rebuild list: remove both, add new
            
            # We remove by index, so we need to be careful.
            # Remove higher index first to preserve lower index
            idx1, idx2 = sorted([idx_to_merge, best_partner_idx], reverse=True)
            current_groups.pop(idx1)
            current_groups.pop(idx2)
            
            current_groups.append(new_group)
            
        else:
            # No partner found? Should not happen unless only 1 group left < K.
            # If only 1 group exists and < K, we can't do anything.
            print("Warning: Cannot merge remaining group.")
            break

    print(f"Final K-groups: {len(current_groups)}")
    
    # ==========================================
    # Generate Output & Metrics
    # ==========================================
    
    output_rows = []
    total_vl = 0
    total_pl = 0
    total_records = 0
    
    final_csv_rows = []
    
    for group_id, group in enumerate(current_groups):
        records = group['records']
        ts_data = np.array([r['timeseries'] for r in records])
        
        # Calculate Envelope
        lower, upper, vl = calculate_envelope_and_vl(ts_data)
        
        # Add to totals
        total_vl += vl * len(records) # Weighted by size? Usually average VL is sum(VL) / num_groups OR avg VL per record?
        # Prompt says "Average Value Loss". Usually over all records or groups?
        # Standard: Sum(VL_group * |group|) / Total_Records gives avg VL per record.
        # OR just Avg of VLs of groups.
        # Let's use weighted average (per record) as it's more representative.
        
        # Calculate Pattern Loss for each record
        group_pattern = group['sax']
        
        for r in records:
            pl = calculate_pattern_loss(r['timeseries'], group_pattern, SAX_LEVEL)
            total_pl += pl
            
            # Prepare CSV row
            # GroupID, H1..H8 (interval), Performance_SD, Pattern
            csv_row = {
                'GroupID': group_id + 1,
                'Performance_SD': r['row_data']['Performance_SD'],
                'Pattern': group_pattern
            }
            
            # Format intervals [min-max]
            for h_idx in range(len(lower)):
                l_val = lower[h_idx]
                u_val = upper[h_idx]
                csv_row[f'H{h_idx+1}'] = f"[{l_val:.2f}-{u_val:.2f}]"
                
            final_csv_rows.append(csv_row)
            
        total_records += len(records)
        
    end_time = time.time()
    execution_time = end_time - start_time
    
    avg_vl = total_vl / len(current_groups) # Average per group? Or per record?
    # Let's print both or stick to one. "Average Value Loss".
    # Usually in k-anon papers, GCP (Global Certainty Penalty) is normalized by # cells.
    # Here VL is per group. Let's return the unweighted average across records?
    # Actually, VL is defined for a group. If we want global metric:
    # Let's use the average VL per group for now, but also tracking weighted might be good.
    # User just said "Average Value Loss". I'll compute average VL across all groups. 
    # WAIT: VL is an instant loss for the group. If I have 1 huge group and 1 tiny group, unweighted avg is misleading.
    # Let's calculate: (Sum of VL of each group * size of group) / total records is NOT dimensionally correct for "Average VL".
    # VL is already "per timestamp" (sqrt/n).
    # Let's just average the VL values of the Groups.
    avg_vl_groups = np.mean([calculate_group_vl(g['records']) for g in current_groups])
    
    avg_pl = total_pl / total_records
    
    print("\n--- Final Metrics ---")
    print(f"Execution Time: {execution_time:.4f} seconds")
    print(f"Average Value Loss (per group): {avg_vl_groups:.4f}")
    print(f"Average Pattern Loss (per record): {avg_pl:.4f}")
    
    # Save CSV
    output_df = pd.DataFrame(final_csv_rows)
    # Reorder columns: GroupID, H1...H8, Performance_SD, Pattern
    cols = ['GroupID'] + [f'H{i+1}' for i in range(8)] + ['Performance_SD', 'Pattern']
    output_df = output_df[cols]
    
    output_path = os.path.join(os.path.dirname(__file__), '../docs/data/kapra_anonymized.csv')
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    output_df.to_csv(output_path, index=False)
    print(f"Anonymized data saved to: {output_path}")

if __name__ == "__main__":
    main()
