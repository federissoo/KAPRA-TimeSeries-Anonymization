import pandas as pd
import numpy as np
import sys
import os
import time

# Recupero la cartella dove si trova questo file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Se non è già presente nella lista di ricerca, la aggiungo
if current_dir not in sys.path:
    sys.path.append(current_dir)

from sax_utils import ts_to_sax, calculate_pattern_loss
from k_anon import makeDatasetKAnon
from kapra_utils import calculate_envelope_and_vl

class Node:
    def __init__(self, data, level, pattern, size, label="intermediate"):
        self.data = data  # List of records (dicts)
        self.level = level # SAX Word Length (matches 'max-level' concept)
        self.pattern = pattern # SAX String
        self.size = size
        self.label = label
        self.children = []

    def __repr__(self):
        return f"Node(level={self.level}, pattern='{self.pattern}', size={self.size}, label='{self.label}')"

def get_sax_pattern(series, level):
    """
    Generate SAX pattern for a time series.
    Level = Alphabet Size.
    """
    if level <= 0:
        return "" # Root level
    return ts_to_sax(series, level)

def naive_node_splitting(node, P, max_level, time_cols):
    """
    Recursive Node Splitting Algorithm.
    """
    # If the caller marked this as good-leaf (e.g. child_merge), stop.
    if node.label == "good-leaf":
        return

    # 2. Se N.size < P allora:
    if node.size < P:
        node.label = "bad-leaf"
        return

    # 4. Altrimenti se N.level == max-level allora:
    if node.level == max_level:
        node.label = "good-leaf"
        return

    # 6. Altrimenti se P <= N.size < 2*P allora:
    if P <= node.size < 2 * P:
        # 7. Massimizza N.level senza dividere il nodo
        # Loop to increase level as long as ALL records share the same pattern
        current_level = node.level
        current_pattern = node.pattern
        
        while current_level < max_level:
            next_level = current_level + 1
            patterns = []
            for row in node.data:
                ts = [row[c] for c in time_cols]
                patterns.append(get_sax_pattern(ts, next_level))
            
            # Check if all patterns are identical
            if len(set(patterns)) == 1:
                current_level = next_level
                current_pattern = patterns[0]
            else:
                # Divergence found, stop at current_level
                break
        
        # Update node state
        node.level = current_level
        node.pattern = current_pattern
        node.label = "good-leaf"
        return

    # 9. Altrimenti (N.size >= 2*P):
    # 10. Esegui una scissione tentativa incrementando il livello
    next_level = node.level + 1
    
    # Check if we can split: group data by next level patterns
    groups = {}
    for row in node.data:
        ts = [row[c] for c in time_cols]
        pat = get_sax_pattern(ts, next_level)
        if pat not in groups:
            groups[pat] = []
        groups[pat].append(row)
    
    valid_children = [] # Size >= P
    small_children = [] # Size < P (TB-nodes)
    
    for pat, rows in groups.items():
        child = Node(rows, next_level, pat, len(rows))
        if len(rows) >= P:
            valid_children.append(child)
        else:
            small_children.append(child)
    
    # 12. Se la somma delle dimensioni dei figli piccoli (TB-nodes) >= P allora:
    total_small_size = sum(c.size for c in small_children)
    
    if total_small_size >= P:
        # 13. Crea un nuovo nodo unificandoli (child_merge)
        merged_data = []
        for c in small_children:
            merged_data.extend(c.data)
        
        # 14. Imposta livello di child_merge = N.level (Parent Level)
        # This effectively resets the specific patterns they had at level+1.
        # They share the parent's pattern.
        child_merge = Node(merged_data, node.level, node.pattern, len(merged_data), label="intermediate")
        
        # TO AVOID LOOP: We must recognize this node shouldn't be split again at level+1.
        child_merge.label = "good-leaf"
        valid_children.append(child_merge)
        small_children = [] # Handled matches
    
    # Any remaining small_children (if sum < P) must be added to children
    # so they can be visited and labeled "bad-leaf" by the recursion base case.
    valid_children.extend(small_children)
    
    if valid_children:
        node.children = valid_children
        # 15. Invocazione ricorsiva su tutti i figli validi generati
        for child in node.children:
            naive_node_splitting(child, P, max_level, time_cols)
    else:
        # 16. Altrimenti (nessun figlio valido generato)
        # 17. N.label = good-leaf (Retract split, make parent a leaf)
        node.children = []
        node.label = "good-leaf"

def collect_leaves(node):
    if not node.children:
        return [node]
    leaves = []
    for child in node.children:
        leaves.extend(collect_leaves(child))
    return leaves

def calculate_distance(ts_data, leaf_pattern, level):
    """
    Calculate distance between a raw time series and a leaf's pattern/reconstruction.
    Uses Patterns Loss metric.
    """
    # Assuming leaf.pattern represents the centroid reconstruction
    try:
        return calculate_pattern_loss(ts_data, leaf_pattern, level)
    except:
        return float('inf')

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "../docs/data/dataset_raw.csv")
    output_path = os.path.join(base_dir, "../docs/data/naive_anonymized.csv")
    
    # Parameters
    K = 8
    P = 2
    MAX_LEVEL = 5 # SAX Alphabet Size Limit
    
    print(f"--- Naive (k,P)-Anonymization Algorithm (K={K}, P={P}) ---")
    start_time = time.time()
    
    # 1. Load Data
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        sys.exit(1)
        
    # Drop EI
    eis = ['ID', 'Name', 'Surname']
    df_clean = df.drop(columns=[c for c in eis if c in df.columns])
    
    time_cols = [c for c in df.columns if c.startswith('H')]
    
    # 2. Phase 1: Mondrian Partitioning on Time Series
    print("Phase 1: Partitioning dataset into K-groups (Time Series Clustering)...")
    dataset_dict = df_clean.to_dict('records')
    anon_dataset, ph1_levels = makeDatasetKAnon(dataset_dict, K, time_cols=time_cols)
    
    if not anon_dataset:
        print("Failed Phase 1.")
        sys.exit(1)
        
    print(f"Phase 1 Complete.")
    
    df_ph1 = pd.DataFrame(anon_dataset)
    grouped = df_ph1.groupby('GroupID')
    
    final_leaves = []
    
    # 3. Phase 2: Node Splitting per K-group
    print("Phase 2: Node Splitting per K-group...")
    
    for group_id, group in grouped:
        group_data = group.to_dict('records')
        # Start at Level 1 (Coarsest granularity "aaaa")
        initial_level = 1
        
        # Calculate initial pattern from the first record (representative)
        # All records at level 1 should produce the same "aaaa" pattern given our logic
        first_ts = [group_data[0][c] for c in time_cols]
        initial_pattern = get_sax_pattern(first_ts, initial_level)
        
        root = Node(group_data, level=initial_level, pattern=initial_pattern, size=len(group_data))
        
        naive_node_splitting(root, P, MAX_LEVEL, time_cols)
        
        leaves = collect_leaves(root)
        for l in leaves:
            l.group_id = group_id
        
        good_leaves = [l for l in leaves if l.label == "good-leaf"]
        bad_leaves = [l for l in leaves if l.label == "bad-leaf"]
        
        # Post-processing: Merge bad leaves
        if bad_leaves:
            if not good_leaves:
                 # If all bad, force merge all into one good leaf (fallback)
                 merged_all = Node([], 2, "*", 0, "good-leaf")
                 for l in bad_leaves:
                     merged_all.data.extend(l.data)
                 merged_all.size = len(merged_all.data)
                 merged_all.group_id = group_id
                 good_leaves = [merged_all]
            else:
                for bl in bad_leaves:
                    # Find nearest good leaf
                    best_target = None
                    min_dist = float('inf')
                    
                    # Compute centroid of bad leaf for efficiency?
                    # Or avg distance of all rows?
                    # Let's take the first row as representative or compute mean series.
                    bl_matrix = np.array([[row[c] for c in time_cols] for row in bl.data])
                    bl_mean_ts = np.mean(bl_matrix, axis=0)
                    
                    for gl in good_leaves:
                        # Distance between BadLeaf Mean TS and GoodLeaf Pattern
                        # The GoodLeaf pattern reconstruction depends on its Level.
                        d = calculate_pattern_loss(bl_mean_ts, gl.pattern, gl.level)
                        if d < min_dist:
                            min_dist = d
                            best_target = gl
                    
                    if best_target:
                        best_target.data.extend(bl.data)
                        best_target.size += bl.size
                        # Do NOT update pattern/level. They just get absorbed.
        
        final_leaves.extend(good_leaves)
        
    # 4. Construct Final Dataset
    print("Constructing final anonymized dataset...")
    final_rows = []
    
    total_pl = 0
    total_records = 0
    
    for leaf in final_leaves:
        cluster_data = [[row[c] for c in time_cols] for row in leaf.data]
        lower, upper, vl = calculate_envelope_and_vl(cluster_data)
        
        leaf_pattern = leaf.pattern
        leaf_level = leaf.level
        
        for row in leaf.data:
            new_row = row.copy()
            for i, col in enumerate(time_cols):
                new_row[col] = f"[{lower[i]}-{upper[i]}]"
            
            new_row['Value_Loss'] = round(vl, 4)
            new_row['Pattern'] = leaf_pattern
            new_row['Level'] = leaf_level
            new_row['GroupID'] = leaf.group_id
            final_rows.append(new_row)
            
            # Pattern Loss Metric
            ts = [row[c] for c in time_cols]
            try:
                # If level < 3 (e.g. root wasn't split), we can't calc PL via SAX?
                # If leaf.level < 3 (e.g. 2), we treat it as no pattern?
                if leaf_level >= 3:
                     pl = calculate_pattern_loss(ts, leaf_pattern, leaf_level)
                else:
                     pl = 0 # Or max?
                total_pl += pl
            except Exception as e:
                pass
            total_records += 1
            
    df_final = pd.DataFrame(final_rows)
    df_final.sort_values(by=['GroupID'], inplace=True)
    
    # Export
    cols_to_drop = ['Value_Loss', 'Level'] # Keep Pattern? Maybe.
    df_export = df_final.drop(columns=[c for c in cols_to_drop if c in df_final.columns])
    if 'GroupID' in df_export.columns:
        cols = ['GroupID'] + [c for c in df_export.columns if c != 'GroupID']
        df_export = df_export[cols]

    df_export.to_csv(output_path, index=False)
    print(f"Done. Saved to {output_path}")

    # --- Metrics ---
    print("\n--- Evaluation Metrics ---")
    
    end_time = time.time()
    print(f"Total Execution Time: {end_time - start_time:.4f} seconds")
    
    avg_vl = df_final['Value_Loss'].mean()
    print(f"Average Instant Value Loss (VL): {avg_vl:.4f}")
    
    avg_pl = total_pl / total_records if total_records > 0 else 0
    print(f"Average Pattern Loss (PL): {avg_pl:.4f}")

    # 3. Query Metrics (Simulation)
    # Relative Error in Range Queries
    # We simulate N random range queries on H1..H8
    
    print("Simulating Range Queries...")
    # Need access to original df with time cols (df_clean has them)
    # And df_final
    
    # Simple Benchmark: 
    # Select a random column C, random range [v1, v2]
    # Count(Original) where C in [v1, v2]
    # Count(Anonymized) where Interval overlaps [v1, v2]
    # Estimate overlap assuming uniform distribution in [min, max]
    
    import random
    random.seed(42)
    n_queries = 50
    total_rel_error = 0
    
    for _ in range(n_queries):
        col = random.choice(time_cols)
        # Range derivation
        min_val = df_clean[col].min()
        max_val = df_clean[col].max()
        
        # Random range of size 10% to 50% of domain
        range_size = (max_val - min_val) * random.uniform(0.1, 0.5)
        start = random.uniform(min_val, max_val - range_size)
        end = start + range_size
        
        # True Count
        true_count = df_clean[(df_clean[col] >= start) & (df_clean[col] <= end)].shape[0]
        
        if true_count == 0:
            continue # Skip to avoid div by zero issues in simple metric
            
        # Estimated Count
        # df_final[col] is "[min-max]"
        # Parse intervals
        est_count = 0
        for val_str in df_final[col]:
            # val_str format "[min-max]"
            try:
                content = val_str.strip("[]")
                # Handle possible float values
                v_min, v_max = map(float, content.split('-'))
                
                # Check overlap
                # Interval [v_min, v_max]
                # Query [start, end]
                
                overlap_start = max(v_min, start)
                overlap_end = min(v_max, end)
                
                if overlap_start < overlap_end:
                    # There is overlap
                    overlap_len = overlap_end - overlap_start
                    interval_len = v_max - v_min
                    
                    if interval_len == 0:
                        # Point value
                        est_count += 1
                    else:
                        # Fraction
                        est_count += (overlap_len / interval_len)
            except:
                pass
                
        rel_error = abs(true_count - est_count) / true_count
        total_rel_error += rel_error
        
    avg_rel_error = total_rel_error / n_queries
    print(f"Average Relative Error in Range Queries (avg {n_queries} runs): {avg_rel_error:.4f}")


if __name__ == "__main__":
    main()
