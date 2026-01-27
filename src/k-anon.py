import pandas as pd
import numpy as np
import sys
import os
# Importiamo la logica matematica dal tuo file utility
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

def makeDatasetKAnon(dataset, k, QI):
    """Algoritmo brute-force per trovare la generalizzazione minima dei QI categorici."""
    best_generalization = None
    best_dataset = None
    min_info_loss = float('inf')

    # Livelli massimi: Dept (0->1->2), Seniority (0->1->2)
    for dept_level in range(3):
        for seniority_level in range(3):
            current_dataset = []
            for row in dataset:
                new_row = row.copy()
                new_row['Dept'] = generalizeCategorical(row['Dept'], dept_level, dept_mapping)
                new_row['Seniority'] = generalizeCategorical(row['Seniority'], seniority_level, seniority_mapping)
                current_dataset.append(new_row)
            
            if isKAnon(current_dataset, k, QI):
                loss = dept_level + seniority_level
                if best_generalization is None or loss < min_info_loss:
                    min_info_loss = loss
                    best_generalization = (dept_level, seniority_level)
                    best_dataset = current_dataset
                    if loss == 0: return best_dataset, best_generalization

    return best_dataset, best_generalization

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "../data/remote_work_activity_raw.csv")
    output_path = os.path.join(base_dir, "../data/k-anon.csv")
    
    print(f"--- KAPRA Step 1: k-Anonymization ---")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: {input_path} not found."); sys.exit(1)

    # 1. Rimozione Identificatori Espliciti (EI)
    eis = ['Name', 'Surname']
    df_clean = df.drop(columns=[c for c in eis if c in df.columns])

    # 2. Definizione Quasi-Identificatori (QI)
    qi_cat = ['Dept', 'Seniority'] # QI Categorici
    # Identifichiamo le colonne delle serie temporali (H1...H8) come QI
    time_cols = [c for c in df.columns if c.startswith('H')] 
    
    # 3. Anonimizzazione degli attributi categorici
    print(f"Generalizing categorical QI {qi_cat} for K={K}...")
    dataset_dict = df_clean.to_dict('records')
    anon_dataset, levels = makeDatasetKAnon(dataset_dict, K, qi_cat)

    if anon_dataset:
        # Convertiamo in DataFrame per elaborare le serie temporali
        df_anon = pd.DataFrame(anon_dataset)
        
        # 4. Creazione delle Anonymization Envelopes (AE)
        print(f"Calculating Envelopes and Value Loss (VL) for {len(time_cols)} timestamps...")
        
        # Raggruppiamo per i QI già anonimizzati
        grouped = df_anon.groupby(qi_cat)
        final_rows = []

        for _, group in grouped:
            # Calcoliamo l'inviluppo [min-max] e la VL per il gruppo
            cluster_data = group[time_cols]
            lower, upper, vl = calculate_envelope_and_vl(cluster_data)
            
            # Applichiamo i risultati a ogni record del gruppo
            for _, row in group.iterrows():
                new_row = row.to_dict()
                for i, col in enumerate(time_cols):
                    # Pubblichiamo l'intervallo invece del valore puntuale
                    new_row[col] = f"[{lower[i]}-{upper[i]}]"
                
                # Aggiungiamo la metrica di errore calcolata
                new_row['Value_Loss'] = round(vl, 4)
                final_rows.append(new_row)

        # Salvataggio
        df_final = pd.DataFrame(final_rows)
        # Ordiniamo per mantenere consistenza
        df_final = df_final.sort_values(by=qi_cat)
        df_final.to_csv(output_path, index=False)
        
        print(f"\nSUCCESS!")
        print(f"Categorical Levels: Dept={levels[0]}, Seniority={levels[1]}")
        print(f"Temporal Data: Anonymized using Envelopes")
        print(f"Output saved to: {output_path}")
    else:
        print("Error: Could not satisfy K-anonymity.")