import pandas as pd
import numpy as np
import sys
import os
from kapra_utils import calculate_envelope_and_vl

# Parametro K richiesto dal modello (k,P)-anonimato
K = 3

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
    # caso base: non posso dividere se ho meno di 2*k dati
    if len(dataset) < 2 * k:
        return [dataset]
    
    # trovo la dimensione da dividere (quella con il range più grande)
    best_col = None
    max_spread = -1
    
    data_df = pd.DataFrame(dataset)
    
    # cerco la colonna con il range più grande
    for col in time_cols:
        try:
            vals = data_df[col].values
            spread = np.max(vals) - np.min(vals)
            if spread > max_spread:
                max_spread = spread
                best_col = col
        except Exception:
            continue
            
    # se non ho trovato una colonna con range maggiore di 0, non posso dividere
    if best_col is None or max_spread == 0:
        return [dataset] 
    
    dataset.sort(key=lambda x: x[best_col]) # ordino i dati per la colonna scelta (lista di dizionari)
    mid = len(dataset) // 2 # divido in due metà
    
    lhs = dataset[:mid] # prima metà (mid escluso)
    rhs = dataset[mid:] # seconda metà (mid incluso)
    
    # controllo se ho abbastanza dati per ogni partizione
    if len(lhs) >= k and len(rhs) >= k:
        return partition_dataset(lhs, k, time_cols) + partition_dataset(rhs, k, time_cols)
    else:
        # se non ho abbastanza dati, non posso dividere
        return [dataset]

def calculate_partition_cost(partitions, time_cols):
    """
    Calculates the average Value Loss (VL) of the partitions.
    """
    total_vl = 0
    total_records = 0
    
    for part in partitions:
        _, _, vl = calculate_envelope_and_vl(pd.DataFrame(part)[time_cols]) # calcolo l'envelope e il value loss per ogni partizione
        total_vl += (vl * len(part)) # peso il value loss per la dimensione del gruppo
        total_records += len(part) # calcolo il numero totale di record
        
    if total_records == 0: return float('inf') # se non ho record, restituisco infinito
    return total_vl / total_records # calcolo il value loss medio

def makeDatasetKAnon(dataset, k, time_cols=None):
    """
    Algorithm to find optimal time-series partitioning.
    Cost Function = (Average_VL / Normalization_Constant)
    """

    # Normalization factor for VL (heuristic: max expected VL approx 40?)
    VL_WEIGHT = 0.5 

    current_dataset = [] # Copio il dataset
    for row in dataset:
        current_dataset.append(row.copy())
    
    df_curr = pd.DataFrame(current_dataset)
    
    # Raggruppo tutti i dati in un unico gruppo
    grouped = [('All', df_curr)]
        
    all_partitions = []
    
    # controllo se ho abbastanza dati
    for _, group in grouped:
        if len(group) < k:
            return None, (None, None)
        
        group_list = group.to_dict('records') # da pandas a lista di dizionari
        partitions = partition_dataset(group_list, k, time_cols) # funzione che implementa la logica di partizionamento Mondrian
        all_partitions.extend(partitions) # estendo la lista di liste di dizionari (partizioni)
    
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