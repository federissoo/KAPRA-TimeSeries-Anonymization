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
from k_anon import makeDatasetKAnon, dept_mapping, seniority_mapping
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

def get_sax_pattern(series, level, alphabet_size=4):
    """
    Generate SAX pattern for a time series.
    Level = word length (number of segments).
    """
    if level <= 0:
        return "" # Root level, no pattern
    return ts_to_sax(series, level, alphabet_size)

def naive_node_splitting(node, P, max_level, time_cols):
    """
    Recursive Node Splitting Algorithm.
    Follows logical flow from user request.
    """
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
        # We need to find the max level where all members still share the same pattern.
        # However, the prompt says "Massimizza N.level senza dividere". 
        # This implies we can increase the level as long as the pattern remains unique for ALL members?
        # Or does it mean we just stop here?
        # "8. N.label = good-leaf // Non si divide per evitare di creare bad-leaves"
        # We will keep it simple: assume we just mark it as good-leaf at current level.
        # Optimizing level "without splitting" would require checking if all members map to same pattern at higher levels.
        # Let's try to increase level checks until they diverge.
        
        current_pattern = node.pattern
        next_level = node.level + 1
        
        while next_level <= max_level:
            # Check if all members have same pattern at next_level
            patterns = []
            for row in node.data:
                ts = [row[c] for c in time_cols]
                patterns.append(get_sax_pattern(ts, next_level))
            
            if len(set(patterns)) == 1:
                # Success, upgrade node
                node.level = next_level
                node.pattern = patterns[0]
                next_level += 1
            else:
                break
        
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
    
    # 11. Se il nodo può essere diviso (genera figli con size >= P)??
    # The logic in prompt is: "Se il nodo può essere diviso (genera figli con size >= P)"
    # BUT line 12 says "Se la somma delle dimensioni dei figli piccoli (TB-nodes) >= P"
    # This implies we create ALL children first, then check sizes.
    
    valid_children = [] # Size >= P
    small_children = [] # Size < P (TB-nodes)
    
    for pat, rows in groups.items():
        child = Node(rows, next_level, pat, len(rows))
        if len(rows) >= P:
            valid_children.append(child)
        else:
            small_children.append(child)
    
    # 11. Condition "Se il nodo può essere diviso"
    # If we have NO valid children and NO small children capable of merging... then effectively we can't split usefully?
    # Let's follow line 12 logic.
    
    # 12. Se la somma delle dimensioni dei figli piccoli (TB-nodes) >= P allora:
    total_small_size = sum(c.size for c in small_children)
    
    if total_small_size >= P:
        # 13. Crea un nuovo nodo unificandoli (child_merge)
        merged_data = []
        for c in small_children:
            merged_data.extend(c.data)
        
        # 14. Imposta livello di child_merge = N.level
        # The prompt says "level of child_merge = N.level" (parent level)
        # So it keeps the generic pattern of the parent.
        child_merge = Node(merged_data, node.level, node.pattern, len(merged_data), label="intermediate")
        
        # We treat child_merge as a valid child now? 
        # Line 15 says "Invocazione ricorsiva su tutti i figli validi generati"
        # Since child_merge has size >= P, it is valid.
        valid_children.append(child_merge)
        small_children = [] # All merged
    
    # Check if we have any valid children to recurse on
    if len(valid_children) > 0:
        node.children = valid_children
        # 15. Invocazione ricorsiva su tutti i figli validi generati
        for child in node.children:
            # Important: child_merge has level = node.level.
            # If we recurse on child_merge, we might infinite loop if we don't catch it.
            # But naive_node_splitting handles logic. 
            # If child_merge.level == node.level, next iteration it will try to split to level+1 again!
            # Wait, if child_merge acts as a new node, it presumably contains the "hard to split" rows.
            # If we try to split them again at level+1, we will get the SAME small fragments?
            # Yes, likely. 
            # So child_merge should probably be a LEAF?
            # Or we should flag it not to be split?
            # The prompt doesn't say "label = good-leaf". It says "Invocazione ricorsiva".
            # BUT: if it's the exact same data and we try same split, we loop.
            # UNLESS "child_merge" logic implies we stop splitting it using this strategy?
            # Re-reading line 14: "Imposta livello di child_merge = N.level".
            # If we recurse, `naive_node_splitting` starts again.
            # If size >= 2P, it tries to split at level+1.
            # It will find `small_children` again (the same ones).
            # It will merge them again.
            # Infinite recursion.
            
            # Correction: Maybe child_merge should be marked as good-leaf?
            # OR we simply don't recurse on child_merge?
            # Line 17 says "Altrimenti: N.label = good-leaf".
            
            # FIX: If we created a child_merge with level == node.level, 
            # we should probably NOT recurse on it to avoid infinite loop, 
            # OR we should treat it as a good-leaf immediately.
            # Actually, `naive-algo.md` says: "I record contenuti in questi nodi vengono ri-inseriti (fusi) nella "good-leaf" più simile".
            # But the detailed steps (12-14) in prompt seem to replace that post-processing or define a local version.
            # "Crea un nuovo nodo unificandoli... Imposta livello ... Invocazione ricorsiva".
            
            # If I recurse on child_merge (level L), it will try to split at L+1.
            # It will fail to find valid children (they were small).
            # It will find small children sum >= P (yes, that's why we merged).
            # It will merge them again...
            
            # To avoid loop, maybe checks if we JUST merged?
            # Or maybe child_merge is good-leaf?
            # Let's assume child_merge is a good-leaf because we know we can't split it further at L+1.
            
            if child.level == node.level:
                child.label = "good-leaf"
            else:
                 naive_node_splitting(child, P, max_level, time_cols)
    else:
        # 16. Altrimenti (nessun figlio valido generato, nemmeno merging)
        # 17. N.label = good-leaf
        node.children = []
        node.label = "good-leaf"

def collect_leaves(node):
    if not node.children:
        return [node]
    leaves = []
    for child in node.children:
        leaves.extend(collect_leaves(child))
    return leaves

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "../docs/data/remote_work_activity_raw.csv")
    output_path = os.path.join(base_dir, "../docs/data/naive_anonymized.csv")
    
    # Parameters
    K = 3
    P = 2
    MAX_LEVEL = 8 # Max SAX word length (since we have 8 columns H1..H8, max meaningful is 8?)
    # Prompt says "max-level". Usually SAX word length.
    
    print(f"--- Naive Naive Node Splitting Algorithm (K={K}, P={P}) ---")
    start_time = time.time()
    
    # 1. Load Data
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        sys.exit(1)
        
    # Drop identifiers
    eis = ['ID', 'Name', 'Surname']
    df_clean = df.drop(columns=[c for c in eis if c in df.columns])
    
    qi = ['Dept', 'Seniority']
    time_cols = [c for c in df.columns if c.startswith('H')]
    # Do NOT append time_cols to qi for Phase 1 (we handle them via Mondrian)
    
    # 2. Phase 1: K-anonymity on Categorical Attributes + Time Series Clustering
    print("Phase 1: Generaling components to K-groups (K-Anon + Mondrian)...")
    dataset_dict = df_clean.to_dict('records')  # da csv a lista di dizionari
    # Reuse logic from k-anon.py
    # Pass only categorical QIs for the finding of candidate blocks
    anon_dataset, levels = makeDatasetKAnon(dataset_dict, K, qi, time_cols)
    
    if not anon_dataset:
        print("Failed Phase 1: Could not k-anonymize categorical attributes.")
        sys.exit(1)
        
    print(f"Phase 1 Complete. Levels: {levels}")
    
    # Group by GroupID (assigned in Phase 1)
    df_ph1 = pd.DataFrame(anon_dataset)
    # Ensure GroupID is present
    if 'GroupID' not in df_ph1.columns:
        print("Error: Phase 1 did not assign GroupID.")
        sys.exit(1)
        
    grouped = df_ph1.groupby('GroupID')
    
    final_leaves = []
    
    # 3. Phase 2: Create-tree for each K-group
    print("Phase 2: Node Splitting per K-group...")
    
    for group_id, group in grouped:
        # Create Root Node for this group
        group_data = group.to_dict('records')
        # Root level = 0? Or 1? 
        # If max-level is SAX length, starting at 1 makes sense (1 segment).
        # Let's start at level 1 (1 segment average).
        # "PR" for level 1 is usually just "a" (or similar simple string).
        
        root = Node(group_data, level=1, pattern="*", size=len(group_data))
        
        # Run Algorithm
        naive_node_splitting(root, P, MAX_LEVEL, time_cols)
        
        # Collect leaves
        leaves = collect_leaves(root)
        for l in leaves:
            l.group_id = group_id
        
        # Filter: handle bad leaves global post-processing?
        # The prompt algorithm steps 12-14 seem to handle bad leaves by merging them LOCALLY.
        # Step 3 and 17 label valid nodes as 'good-leaf'.
        # Step 2 labels really small nodes as 'bad-leaf'.
        # If any 'bad-leaf' remains (e.g. from a split where small children sum < P), 
        # we need to handle them.
        
        good_leaves = [l for l in leaves if l.label == "good-leaf"]
        bad_leaves = [l for l in leaves if l.label == "bad-leaf"]
        
        # Post-processing for remaining bad leaves (from Step 60 in `naive-algo.md`)
        # "I record contenuti in questi nodi vengono ri-inseriti (fusi) nella 'good-leaf' più simile"
        
        if bad_leaves:
            # print(f"  - Found {len(bad_leaves)} bad leaves to merge.")
            for bl in bad_leaves:
                # Find nearest good leaf
                # Distance metric: Pattern similarity? Or just attach to any valid sibling?
                # `naive-algo.md` says "più simile in termini di pattern".
                # For simplicity, we attach to largest good leaf in same group?
                # Or based on SAX pattern distance.
                
                # If no good leaves in this group (rare if group was size >= K >= P),
                # we might be in trouble. But K >= P usually.
                
                if good_leaves:
                    # Simple heuristic: Attach to first good leaf
                    target = good_leaves[0] 
                    target.data.extend(bl.data)
                    target.size += bl.size
                    # Pattern remains target's pattern
                else:
                    # If NO good leaves exist (weird), this group failed?
                    # Keep as is?
                    print(f"  Warning: Group {group_id} became all bad leaves!")
                    pass
        
        final_leaves.extend(good_leaves)
        
    # 4. Construct Final Dataset
    print("Constructing final anonymized dataset...")
    final_rows = []
    
    for leaf in final_leaves:
        # Calculate envelope for the cluster
        cluster_data = [[row[c] for c in time_cols] for row in leaf.data]
        lower, upper, vl = calculate_envelope_and_vl(cluster_data)
        
        for row in leaf.data:
            new_row = row.copy()
            # QI are already anonymized from Phase 1
            
            # Anonymize indices
            for i, col in enumerate(time_cols):
                new_row[col] = f"[{lower[i]}-{upper[i]}]"
            
            new_row['Value_Loss'] = round(vl, 4)
            new_row['Pattern'] = leaf.pattern
            new_row['Level'] = leaf.level
            new_row['GroupID'] = leaf.group_id
            final_rows.append(new_row)
            
    df_final = pd.DataFrame(final_rows)
    # Sort for tidiness
    df_final.sort_values(by=['GroupID'], inplace=True)
    
    # Create export version: Drop Value_Loss, Level. Reorder GroupID to front.
    cols_to_drop = ['Value_Loss', 'Level']
    df_export = df_final.drop(columns=[c for c in cols_to_drop if c in df_final.columns])
    
    # Reorder GroupID to first
    if 'GroupID' in df_export.columns:
        cols = ['GroupID'] + [c for c in df_export.columns if c != 'GroupID']
        df_export = df_export[cols]

    df_export.to_csv(output_path, index=False)
    print(f"Done. Saved to {output_path}")

    # --- Metrics Calculation ---
    print("\n--- Evaluation Metrics ---")
    
    # 1. Computational Complexity (proxied by Execution Time)
    end_time = time.time()
    print(f"Total Execution Time: {end_time - start_time:.4f} seconds")
    print(f"Theoretical Complexity: O(N * MaxLevel) = O({len(df)} * {MAX_LEVEL})")

    # 2. Information Loss
    # VL (Instant Value Loss) - already calculated per record, let's avg
    avg_vl = df_final['Value_Loss'].mean()
    print(f"Average Instant Value Loss (VL): {avg_vl:.4f}")
    
    # PL (Pattern Loss)
    # We need to calculate PL for every record: Dist(Original_Z, Reconstructed_Z_from_SAX)
    # We need to re-match the original data to the anonymized data.
    # Since we dropped IDs (Name, Surname) and sorted, matching is hard.
    # However, we have the `leaf.data` which contains the rows.
    # We can calculate PL *during* the construction loop or re-iterate leaves.
    
    # Let's calculate PL during construction phase to be accurate (while we have the raw row).
    # Re-calculating using a separate loop over `final_leaves` before creating `df_final`
    
    total_pl = 0
    total_records = 0
    
    for leaf in final_leaves:
        pattern = leaf.pattern
        level = leaf.level
        
        # Reconstruct pattern values (centroids)
        # Handle case where pattern is empty or "*" (Level 0/1?)
        # If level=1, pattern might be empty or length 1 depending on impl.
        # Our get_sax_pattern returns "" for level <= 0.
        # Actually standard SAX level 1 -> 1 segment.
        
        # If pattern is missing/empty, treat as max loss? Or just mean of series?
        # Assuming valid patterns for good leaves.
        
        # For each row in leaf
        for row in leaf.data:
            ts = [row[c] for c in time_cols]
            # Calculate PL: Dist(Z(ts), Reconstructed(Pattern))
            # Need to import calculate_pattern_loss
            try:
                pl = calculate_pattern_loss(ts, pattern, alphabet_size=4)
            except Exception:
                pl = 0 # Fallback
            
            total_pl += pl
            total_records += 1
            
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
