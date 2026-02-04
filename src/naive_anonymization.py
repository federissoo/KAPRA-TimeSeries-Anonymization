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
    Genera il pattern SAX per una serie temporale.
    Level = Dimensione dell'alfabeto.
    """
    if level <= 0:
        return "" # Root level
    return ts_to_sax(series, level)

def naive_node_splitting(node, P, max_level, time_cols):
    """
    Algoritmo di divisione ricorsiva dei nodi:
    node = nodo da dividere
    P = parametro di privacy
    max_level = livello massimo di SAX
    time_cols = colonne temporali
    """
    # se il chiamante ha contrassegnato questo come good-leaf (es. child_merge), fermati.
    if node.label == "good-leaf":
        return

    # se node.size < P allora:
    if node.size < P:
        node.label = "bad-leaf"
        return

    # se node.level == max-level allora:
    if node.level == max_level:
        node.label = "good-leaf"
        return

    # se P <= node.size < 2*P allora:
    if P <= node.size < 2 * P:
        # Massimizza node.level (livello di dettaglio SAX) senza dividere il nodo
        # Loop to increase level as long as ALL records share the same pattern
        current_level = node.level
        current_pattern = node.pattern
        
        # loop per aumentare il livello di dettaglio SAX
        while current_level < max_level:
            next_level = current_level + 1
            patterns = []
            for row in node.data: # Per ogni record nel nodo
                ts = [row[c] for c in time_cols] # Prendi la serie temporale [val1, val2, ..., valn]
                patterns.append(get_sax_pattern(ts, next_level)) # ricalcola il pattern SAX con il livello aumentato
            
            # Se tutti i pattern sono identici aumento di un livello e aggiorno il pattern e riciclo
            if len(set(patterns)) == 1:
                current_level = next_level
                current_pattern = patterns[0]
            else:
                # altrimenti rimangono a quello precedente
                break
        
        # aggiorna il nodo
        node.level = current_level
        node.pattern = current_pattern
        node.label = "good-leaf"
        return

    # Altrimenti (node.size >= 2*P):
    # Eseguo una scissione tentativa incrementando il livello
    next_level = node.level + 1
    
    # Raggruppo i record per pattern SAX al livello successivo
    groups = {}
    for row in node.data: # per ogni record
        ts = [row[c] for c in time_cols] # prendi la serie temporale
        pat = get_sax_pattern(ts, next_level) # ricalcola il pattern SAX con il livello aumentato
        if pat not in groups: # se il gruppo con quel pattern non esiste lo creo 
            groups[pat] = []
        groups[pat].append(row) # aggiungi il record al gruppo
        """ groups = {
            pattern1: [row1, row2, ...],
            pattern2: [row3, row4, ...],
            ...
        } """
    
    valid_children = [] # Size >= P
    small_children = [] # Size < P (TB-nodes)
    
    for pat, rows in groups.items(): # per ogni GRUPPO
        child = Node(rows, next_level, pat, len(rows)) # crea un nodo figlio per ogni gruppo
        if len(rows) >= P: # se la dimensione del gruppo >= P
            valid_children.append(child) # lo aggiungo ai figli validi
        else:
            small_children.append(child) # altrimenti lo aggiungo ai figli piccoli
    
    total_small_size = sum(c.size for c in small_children)
    
    if total_small_size >= P: # se la somma delle dimensioni dei figli piccoli >= P
        # Crea un nuovo nodo unificandoli (child_merge)
        merged_data = []
        for c in small_children:
            merged_data.extend(c.data)
        
        # Imposta livello di child_merge = N.level (livello del padre)
        child_merge = Node(merged_data, node.level, node.pattern, len(merged_data), label="intermediate")
        
        # per evitare loop mettiamo child_merge come good-leaf
        child_merge.label = "good-leaf"
        valid_children.append(child_merge)
        small_children = [] 
    
    # Aggiungiamo i figli piccoli (rimasti se < P) ai figli validi
    valid_children.extend(small_children)
    
    if valid_children: # se ci sono figli validi
        node.children = valid_children # li aggiungiamo ai figli del nodo
        # 15. Invocazione ricorsiva su tutti i figli validi generati
        for child in node.children:
            naive_node_splitting(child, P, max_level, time_cols)
    else: # Altrimenti (nessun figlio valido generato)
        node.children = [] # ritrattiamo la divisione rendendo il padre una foglia
        node.label = "good-leaf"

def collect_leaves(node): # raccoglie tutte le foglie dell'albero
    if not node.children: # se il nodo non ha figli è una foglia
        return [node] # restituisce il nodo
    leaves = [] # lista delle foglie
    for child in node.children: # per ogni figlio
        leaves.extend(collect_leaves(child)) # aggiunge le foglie del figlio alla lista
    return leaves # restituisce la lista delle foglie

def calculate_distance(ts_data, leaf_pattern, level):
    """
    Calcola la distanza tra una serie temporale grezza e il pattern/ricostruzione di una foglia.
    Usa la metrica Pattern Loss.
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
    
    # parametri
    K = 8
    P = 2
    MAX_LEVEL = 5 # limito la dimensione del SAX alphabet
    
    print(f"--- Naive (k,P)-Anonymization Algorithm (K={K}, P={P}) ---")
    start_time = time.time()
    
    # carico i dati
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        sys.exit(1)
        
    # droppo EI
    eis = ['ID', 'Name', 'Surname']
    df_clean = df.drop(columns=[c for c in eis if c in df.columns])
    
    time_cols = [c for c in df.columns if c.startswith('H')]
    
    # divido dataset 
    print("Phase 1: Partitioning dataset into K-groups (Time Series Clustering)...")
    dataset_dict = df_clean.to_dict('records') # trasformo il dataset in una lista di dizionari
    anon_dataset = makeDatasetKAnon(dataset_dict, K, time_cols=time_cols) # divido il dataset in K gruppi
    
    if not anon_dataset:
        print("Failed Phase 1.")
        sys.exit(1)
        
    print(f"Phase 1 Complete.")
    
    df_ph1 = pd.DataFrame(anon_dataset) 
    grouped = df_ph1.groupby('GroupID') # raggruppo i record per GroupID
    
    final_leaves = []
    
    # divido i gruppi in nodi
    print("Phase 2: Node Splitting per K-group...")
    
    for group_id, group in grouped: # per ogni gruppo
        group_data = group.to_dict('records') # trasformo il gruppo in una lista di dizionari
        initial_level = 1 # inizio a livello 1
        
        # calcolo il pattern iniziale dal primo record (rappresentante)
        # tutti i record al livello 1 hanno stesso pattern "aaaa"
        first_ts = [group_data[0][c] for c in time_cols] # prendo la prima serie temporale del gruppo
        initial_pattern = get_sax_pattern(first_ts, initial_level) # calcolo il pattern iniziale 
        
        root = Node(group_data, level=initial_level, pattern=initial_pattern, size=len(group_data)) # creo il nodo radice
        
        naive_node_splitting(root, P, MAX_LEVEL, time_cols) # divido i nodi
        
        leaves = collect_leaves(root) # raccolgo le foglie
        for l in leaves:
            l.group_id = group_id
        
        # divido le foglie in good e bad
        good_leaves = [l for l in leaves if l.label == "good-leaf"]
        bad_leaves = [l for l in leaves if l.label == "bad-leaf"]
        
        # se ci sono foglie bad
        if bad_leaves:
            if not good_leaves:
                 # se tutte le foglie sono bad, le unisco in una sola good leaf
                 merged_all = Node([], 2, "*", 0, "good-leaf")
                 for l in bad_leaves:
                     merged_all.data.extend(l.data)
                 merged_all.size = len(merged_all.data)
                 merged_all.group_id = group_id
                 good_leaves = [merged_all]
            else:
                for bl in bad_leaves:
                    # trovo la good leaf più vicina alla bad leaf
                    best_target = None
                    min_dist = float('inf')
                    
                    # calcolo la serie temporale media della bad leaf
                    bl_matrix = np.array([[row[c] for c in time_cols] for row in bl.data])
                    bl_mean_ts = np.mean(bl_matrix, axis=0)
                    
                    for gl in good_leaves:
                        # Distanza tra la serie media della BadLeaf e il pattern della GoodLeaf
                        # La ricostruzione del pattern della GoodLeaf dipende dal suo livello.
                        d = calculate_distance(bl_mean_ts, gl.pattern, gl.level)
                        if d < min_dist:
                            min_dist = d
                            best_target = gl
                    
                    if best_target:
                        best_target.data.extend(bl.data)
                        best_target.size += bl.size
                        # NON aggiornare pattern/livello. Vengono semplicemente assorbiti.
        
        final_leaves.extend(good_leaves)
        
    # 4. Costruzione del Dataset Finale Anonimizzato
    print("Costruzione del dataset finale anonimizzato...")
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
            
            # Metrica Pattern Loss
            ts = [row[c] for c in time_cols]
            try:
                # Se livello < 3 (es. radice non divisa), non possiamo calcolare PL via SAX
                # Se leaf.level < 3 (es. 2), lo trattiamo come nessun pattern
                if leaf_level >= 3:
                     pl = calculate_pattern_loss(ts, leaf_pattern, leaf_level)
                else:
                     pl = 0 # O max?
                total_pl += pl
            except Exception as e:
                pass
            total_records += 1
            
    df_final = pd.DataFrame(final_rows)
    df_final.sort_values(by=['GroupID'], inplace=True)
    
    # Esportazione
    cols_to_drop = ['Value_Loss', 'Level'] # Mantenere Pattern? Forse.
    df_export = df_final.drop(columns=[c for c in cols_to_drop if c in df_final.columns])
    if 'GroupID' in df_export.columns:
        cols = ['GroupID'] + [c for c in df_export.columns if c != 'GroupID']
        df_export = df_export[cols]

    df_export.to_csv(output_path, index=False)
    print(f"Done. Saved to {output_path}")

    # --- Metriche ---
    print("\n--- Metriche di Valutazione ---")
    
    end_time = time.time()
    print(f"Tempo Totale di Esecuzione: {end_time - start_time:.4f} secondi")
    
    avg_vl = df_final['Value_Loss'].mean()
    print(f"Average Instant Value Loss (VL): {avg_vl:.4f}")
    
    avg_pl = total_pl / total_records if total_records > 0 else 0
    print(f"Average Pattern Loss (PL): {avg_pl:.4f}")

    # 3. Query Metrics (Simulazione)
    # Errore Relativo nelle Range Queries
    # Simuliamo N range queries casuali su H1..H8
    
    print("Simulazione Range Queries...")
    # Serve accesso al df originale con colonne temporali (df_clean le ha)
    # E df_final
    
    # Benchmark Semplice: 
    # Seleziona una colonna C, range casuale [v1, v2]
    # Conta(Originale) dove C in [v1, v2]
    # Conta(Anonimizzato) dove Intervallo si sovrappone a [v1, v2]
    # Stima sovrapposizione assumendo distribuzione uniforme in [min, max]
    
    import random
    random.seed(42)
    n_queries = 50
    total_rel_error = 0
    
    for _ in range(n_queries):
        col = random.choice(time_cols)
        # Derivazione del range
        min_val = df_clean[col].min()
        max_val = df_clean[col].max()
        
        # Range casuale di dimensione 10% a 50% del dominio
        range_size = (max_val - min_val) * random.uniform(0.1, 0.5)
        start = random.uniform(min_val, max_val - range_size)
        end = start + range_size
        
        # Conteggio Reale
        true_count = df_clean[(df_clean[col] >= start) & (df_clean[col] <= end)].shape[0]
        
        if true_count == 0:
            continue # Salta per evitare div by zero
            
        # Conteggio Stimato
        # df_final[col] è "[min-max]"
        # Parsa intervalli
        est_count = 0
        for val_str in df_final[col]:
            # formato val_str "[min-max]"
            try:
                content = val_str.strip("[]")
                # Gestione possibili valori float
                v_min, v_max = map(float, content.split('-'))
                
                # Controllo sovrapposizione
                # Intervallo [v_min, v_max]
                # Query [start, end]
                
                overlap_start = max(v_min, start)
                overlap_end = min(v_max, end)
                
                if overlap_start < overlap_end:
                    # C'è sovrapposizione
                    overlap_len = overlap_end - overlap_start
                    interval_len = v_max - v_min
                    
                    if interval_len == 0:
                        # Valore puntuale
                        est_count += 1
                    else:
                        # Frazione
                        est_count += (overlap_len / interval_len)
            except:
                pass
                
        rel_error = abs(true_count - est_count) / true_count
        total_rel_error += rel_error
        
    avg_rel_error = total_rel_error / n_queries
    print(f"Errore Relativo Medio nelle Range Queries (su {n_queries} run): {avg_rel_error:.4f}")


if __name__ == "__main__":
    main()
