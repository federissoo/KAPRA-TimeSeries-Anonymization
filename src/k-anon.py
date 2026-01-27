
import pandas as pd
import numpy as np
import sys
import os

# Parametro K modificabile
K = 3

# Mappings for generalization
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
    """
    Check if dataset is k-anonymous with respect to QI.
    Dataset can be a list of dicts or a DataFrame.
    """
    if isinstance(dataset, list):
        df = pd.DataFrame(dataset)
    else:
        df = dataset
        
    if df.empty:
        return False
        
    # Group by Quasi Identifiers and count size of each group
    if not all(q in df.columns for q in QI):
        # If QIs are not in columns, we can't check. 
        # This acts as a fallback or error check.
        return False
        
    # Convert all QI columns to string to ensure grouping works
    df_check = df.copy()
    for col in QI:
        df_check[col] = df_check[col].astype(str)
        
    group_sizes = df_check.groupby(QI).size()
    min_size = group_sizes.min()
    
    return min_size >= k

def generalizeCategorical(value, level, mapping):
    """
    Generalize a categorical value 'level' times using the mapping.
    """
    for _ in range(level):
        if value in mapping:
            value = mapping[value]
        else:
            # If value not in mapping, maybe it's already top level or unknown
            # For this script, we assume mappings cover all necessary transitions
            pass 
    return value

def makeDatasetKAnon(dataset, k, QI):
    """
    Brute-force algorithm to find minimal generalization to satisfy k-anonymity.
    """
    best_generalization = None
    best_dataset = None
    min_info_loss = float('inf')

    # Define max levels for our specific attributes
    # Dept: 0 -> 1 -> 2
    # Seniority: 0 -> 1 -> 2
    max_dept_level = 2
    max_seniority_level = 2

    # Iterate through all combinations of generalization levels
    for dept_level in range(max_dept_level + 1):
        for seniority_level in range(max_seniority_level + 1):
            
            # Create a generalized version of the dataset
            current_dataset = []
            for row in dataset:
                new_row = row.copy()
                new_row['Dept'] = generalizeCategorical(row['Dept'], dept_level, dept_mapping)
                new_row['Seniority'] = generalizeCategorical(row['Seniority'], seniority_level, seniority_mapping)
                current_dataset.append(new_row)
            
            # Check if this generalization satisfies K-anonymity
            if isKAnon(current_dataset, k, QI):
                # Calculate information loss (simple sum of levels)
                loss = dept_level + seniority_level
                
                if best_generalization is None or loss < min_info_loss:
                    min_info_loss = loss
                    best_generalization = (dept_level, seniority_level)
                    best_dataset = current_dataset
                    
                    # Optimization: if loss is 0, we can stop (original data is k-anon)
                    if loss == 0:
                        return best_dataset, best_generalization

    return best_dataset, best_generalization

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "../data/remote_work_activity_raw.csv")
    output_path = os.path.join(base_dir, "../data/k-anon.csv")
    
    print(f"Loading data from {input_path}...")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: File {input_path} not found.")
        sys.exit(1)

    # 1. Remove Explicit Identifiers (EI)
    # EIs are Name and Surname
    eis = ['Name', 'Surname']
    df_clean = df.drop(columns=[c for c in eis if c in df.columns])
    print(f"Removed Explicit Identifiers: {eis}")

    # 2. Define Quasi Identifiers (QI)
    qi = ['Dept', 'Seniority']
    print(f"Quasi Identifiers: {qi}")
    print(f"Target K: {K}")

    # Convert to list of dicts for processing
    dataset = df_clean.to_dict('records')

    # 3. Anonymize
    anon_dataset, levels = makeDatasetKAnon(dataset, K, qi)

    if anon_dataset:
        print(f"Anonymization successful!")
        print(f"Generalization Levels: Dept={levels[0]}, Seniority={levels[1]}")
        
        # Save to CSV
        df_anon = pd.DataFrame(anon_dataset)
        df_anon.to_csv(output_path, index=False)
        print(f"Saved anonymized dataset to {output_path}")
        
        # Verify
        actual_k = df_anon.groupby(qi).size().min()
        print(f"Verification: Actual minimum group size is {actual_k}")
    else:
        print("Failed to anonymize dataset with the given generalization hierarchies.")
