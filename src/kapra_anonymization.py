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
# Defaults (can be overridden by function args)
DEFAULT_K = 8
DEFAULT_P = 2
DEFAULT_SAX_LEVEL = 8
DEFAULT_N_SEGMENTS = 4

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

def run_kapra_anonymization(K=DEFAULT_K, P=DEFAULT_P, SAX_LEVEL=DEFAULT_SAX_LEVEL, N_SEGMENTS=DEFAULT_N_SEGMENTS, verbose=True):
    start_time = time.time()
    
    # 1. Load Data
    data_path = os.path.join(os.path.dirname(__file__), '../docs/data/dataset_raw.csv')
    if not os.path.exists(data_path):
         data_path = os.path.join(os.path.dirname(__file__), '../../docs/data/dataset_raw.csv')
    
    if verbose:
        print(f"--- KAPRA Algorithm (K={K}, P={P}, MaxLevel={SAX_LEVEL}) ---")
        print(f"Loading data from {data_path}...")
    
    try:
        df = load_data(data_path)
    except FileNotFoundError:
        print(f"Error: {data_path} not found.")
        return None

    ts_data = get_time_series(df)
    
    # Prepare records with metadata
    records = []
    for idx, row in df.iterrows():
        ts = ts_data[idx]
        records.append({
            'original_index': idx,
            'timeseries': ts,
            'row_data': row,
            'sax': '', 
            'level': SAX_LEVEL, # Track distinct level per record/group
            'group_id': None
        })
        
    if verbose:
        print(f"Total records: {len(records)}")
        print("\n--- Phase 1 & 2: Initial Grouping & Recycling (Bottom-Up) ---")
    
    # In true KAPRA/Algorithm 2:
    # We start with ALL records at MAX_LEVEL.
    # We identify Bad Leaves (groups < P).
    # We iteratively lower the level for Bad Leaves only, trying to merge them.
    
    # Initial Grouping at MAX_LEVEL
    current_level = SAX_LEVEL
    
    # Helper to group records by their SAX at a specific level
    def group_records_by_sax(record_list, level):
        groups = {}
        for r in record_list:
            # Recompute SAX at 'level'
            # Note: r['timeseries'] is constant. 
            sax = ts_to_sax(r['timeseries'], level=level, n_segments=N_SEGMENTS)
            r['sax'] = sax # Update current sax
            r['level'] = level
            if sax not in groups:
                groups[sax] = []
            groups[sax].append(r)
        return groups

    # 1. Initial State: All records are "bad" (candidates) or "good"
    # Actually, we group all.
    all_groups = group_records_by_sax(records, current_level)
    
    final_p_groups = [] # List of {'sax':..., 'records':..., 'level':...}
    bad_records = []
    
    # Separate Good and Bad groups at MAX_LEVEL
    for sax, recs in all_groups.items():
        if len(recs) >= P:
            final_p_groups.append({
                'sax': sax, 
                'records': recs, 
                'level': current_level,
                'type': 'good-leaf'
            })
        else:
            bad_records.extend(recs)
            
    if verbose:
        print(f"Level {current_level}: {len(final_p_groups)} good groups found. {len(bad_records)} records remaining in bad leaves.")
        
    # 2. Recycle Loop (Algorithm 2)
    # While bad records exist, lower level, regroup, extract good groups.
    current_level -= 1
    
    while bad_records and current_level >= 3: # Assuming min SAX level typically 3 or 2
        # Regroup bad records at lower level
        groups = group_records_by_sax(bad_records, current_level)
        
        new_bad_records = []
        
        for sax, recs in groups.items():
            if len(recs) >= P:
                final_p_groups.append({
                    'sax': sax, 
                    'records': recs, 
                    'level': current_level,
                    'type': 'good-leaf-recycled'
                })
            else:
                new_bad_records.extend(recs)
                
        bad_records = new_bad_records
        if verbose and len(bad_records) > 0:
             print(f"Level {current_level}: Found new good groups. {len(bad_records)} records still bad.")
             
        current_level -= 1
        
    # Handle remaining bad records (suppression or merge to root)
    if bad_records:
        if verbose:
            print(f"Warning: {len(bad_records)} records could not form P-groups even at lowest level.")
        # Option A: Suppress (Paper says "Suppress all time-series contained in bad leaves")
        # Option B: Merge them all into a generic group (Level 1/2) if >= P?
        # Let's try to group them at Level 2 or 1.
        # If still < P, strict suppression.
        # For utility, let's create a "garbage" group if size >= P.
        if len(bad_records) >= P:
             final_p_groups.append({
                'sax': '*', 
                'records': bad_records, 
                'level': 0, # Symbolic
                'type': 'suppressed-but-kept'
            })
        else:
             # Strict suppression (exclude from output)
             pass
             
    current_groups = final_p_groups
    if verbose:
        print(f"Total Groups after Phase 2: {len(current_groups)}")
    
    # ==========================================
    # Phase 3: Formation of K-groups
    # ==========================================
    if verbose:
        print("\n--- Phase 3: Formation of K-groups ---")
    
    # Standard Greedy Merge to satisfy K
    while True:
        invalid_indices = [i for i, g in enumerate(current_groups) if len(g['records']) < K]
        if not invalid_indices:
            break 
            
        invalid_indices.sort(key=lambda i: len(current_groups[i]['records']))
        idx_to_merge = invalid_indices[0]
        group_to_merge = current_groups[idx_to_merge]
        
        best_partner_idx = -1
        min_merge_cost = float('inf')
        
        for i, other_group in enumerate(current_groups):
            if i == idx_to_merge:
                continue
            
            cost = calculate_merge_cost(group_to_merge['records'], other_group['records'])
            if cost < min_merge_cost:
                min_merge_cost = cost
                best_partner_idx = i
                
        if best_partner_idx != -1:
            partner_group = current_groups[best_partner_idx]
            
            # Merging
            # Logic: Combined records.
            # Pattern: The paper doesn't specify deeply for Phase 3 pattern.
            # We keep the pattern of the dominating group for reporting or a generalized one?
            # If we merge a Level 10 group and a Level 5 group, what is the result?
            # KAPRA aims to retain pattern. Reporting the separate patterns in the same K-group is valid in (k,P).
            # (k,P) allows groups to have sub-groups with different P-patterns.
            # BUT the output CSV structure usually implies 1 pattern per "Group".
            # If we must output 1 pattern, we pick the dominant one.
            
            merged_records = group_to_merge['records'] + partner_group['records']
            
            # Domination logic
            if len(partner_group['records']) >= len(group_to_merge['records']):
                dom_sax = partner_group['sax']
                dom_level = partner_group['level']
            else:
                dom_sax = group_to_merge['sax']
                dom_level = group_to_merge['level']
                
            new_group = {
                'sax': dom_sax,
                'records': merged_records,
                'level': dom_level,
                'type': 'merged'
            }
            
            idx1, idx2 = sorted([idx_to_merge, best_partner_idx], reverse=True)
            current_groups.pop(idx1)
            current_groups.pop(idx2)
            current_groups.append(new_group)
            
        else:
            if verbose:
                print("Warning: Cannot merge remaining group.")
            break

    if verbose:
        print(f"Final K-groups: {len(current_groups)}")
    
    # ==========================================
    # Generate Output & Metrics
    # ==========================================
    
    final_csv_rows = []
    total_vl = 0
    total_pl = 0
    total_records = 0
    
    for group_id, group in enumerate(current_groups):
        records = group['records']
        ts_data = np.array([r['timeseries'] for r in records])
        
        # Envelope & VL
        lower, upper, vl = calculate_envelope_and_vl(ts_data)
        
        # group_pattern = group['sax'] # OLD: Dominant pattern
        # group_level = group['level'] # OLD: Dominant level
        
        for r in records:
            # Use the specific P-subgroup pattern/level for this record
            r_pattern = r['sax']
            r_level = r['level']
            
            # PL calculation depends on the level of the pattern
            if r_level >= 3:
                try:
                    pl = calculate_pattern_loss(r['timeseries'], r_pattern, r_level)
                except:
                    pl = 0
            else:
                pl = 0 
                
            total_pl += pl
            
            csv_row = {
                'GroupID': group_id + 1,
                'Performance_SD': r['row_data']['Performance_SD'],
                'Pattern': r_pattern, # Use individual pattern
                'Level': r_level,   # Use individual level
                'Value_Loss': vl
            }
            
            for h_idx in range(len(lower)):
                l_val = lower[h_idx]
                u_val = upper[h_idx]
                csv_row[f'H{h_idx+1}'] = f"[{l_val:.2f}-{u_val:.2f}]"
                
            final_csv_rows.append(csv_row)
            
        total_records += len(records)
        
    end_time = time.time()
    execution_time = end_time - start_time
    
    if current_groups:
        avg_vl_groups = np.mean([calculate_group_vl(g['records']) for g in current_groups])
    else:
        avg_vl_groups = 0
        
    avg_pl = total_pl / total_records if total_records > 0 else 0
    
    if verbose:
        print("\n--- Final Metrics ---")
        print(f"Execution Time: {execution_time:.4f} seconds")
        print(f"Average Value Loss (per group): {avg_vl_groups:.4f}")
        print(f"Average Pattern Loss (per record): {avg_pl:.4f}")
    
    # Save CSV
    output_df = pd.DataFrame(final_csv_rows)
    cols = ['GroupID'] + [f'H{i+1}' for i in range(8)] + ['Performance_SD', 'Pattern', 'Level', 'Value_Loss']
    output_df = output_df[cols]
    
    output_path = os.path.join(os.path.dirname(__file__), '../docs/data/kapra_anonymized.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_df.to_csv(output_path, index=False)

    return {
        'K': K,
        'P': P,
        'SAX_LEVEL': SAX_LEVEL,
        'Time': execution_time,
        'VL': avg_vl_groups,
        'PL': avg_pl
    }

def main():
    run_kapra_anonymization()

if __name__ == "__main__":
    main()
