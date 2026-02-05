import pandas as pd
import numpy as np
import os
import random

def generate_dataset():
    """
    Generate synthetic dataset following docs/dataset-generation.md specifications.
    Schema: ID, Name, Surname, H1-H8 (int 0-50), Performance_SD (Low/Medium/High)
    Patterns: Rising, Falling, Peak, Flat
    """
    
    n_rows = 3000
    n_cols = 8 # H1 to H8
    
    names = ["Francesco", "Alessandro", "Lorenzo", "Mattia", "Leonardo", "Andrea", "Gabriele", "Matteo", 
             "Tommaso", "Edoardo", "Sofia", "Giulia", "Aurora", "Alice", "Ginevra", "Emma", "Giorgia", "Greta", "Beatrice"]
    surnames = ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci", 
                "Marino", "Greco", "Bruno", "Gallo", "Conti", "De Luca", "Mancini", "Costa", "Giordano", "Rizzo"]

    data = []
    
    # 1. Pattern Definitions (Archetypes) used to optimize distinctness
    # "Rising" -> Funnel / Linear Up
    # "Falling" -> Funnel / Linear Down
    # "Peak" -> Bell
    # "Flat" -> Cylinder
    
    def generate_base_pattern(ptype, length=8):
        x = np.linspace(0, 1, length)
        
        if ptype == 'Rising':
            # Start low (e.g. 5-15) end high (e.g. 35-45)
            start = np.random.uniform(5, 15)
            end = np.random.uniform(35, 45)
            # Linear interpolation
            slope = end - start
            return start + slope * x
            
        elif ptype == 'Falling':
             # Start high end low
            start = np.random.uniform(35, 45)
            end = np.random.uniform(5, 15)
            slope = end - start
            return start + slope * x
            
        elif ptype == 'Peak':
            # Bell curve in the middle
            # Center roughly at 0.5 (middle of 8 hours)
            # Use sin(0..pi)
            base_val = np.random.uniform(10, 20)
            amp = np.random.uniform(20, 30)
            s_x = np.linspace(0, np.pi, length)
            return base_val + amp * np.sin(s_x)
            
        elif ptype == 'Flat':
            # Constant value
            val = np.random.uniform(20, 40)
            return np.full(length, val)
            
        return np.zeros(length)

    np.random.seed(42)

    for i in range(1, n_rows + 1):
        # Metadata
        name = np.random.choice(names)
        surname = np.random.choice(surnames)
        
        # 2. Assign Archetype
        ptype = np.random.choice(['Rising', 'Falling', 'Peak', 'Flat'])
        
        # Generate base curve (Float)
        ts = generate_base_pattern(ptype, n_cols)
        
        # 3. Add Variability (Intensity Shift + Noise)
        # Shift: +/- 5 to keep within range 0-50 mostly
        shift = np.random.uniform(-5, 5)
        # Noise: Gaussian
        noise = np.random.normal(0, 2, n_cols) # Sigma=2 creates visible but not destructive noise
        
        ts_final = ts + shift + noise
        
        # Clamp to [0, 50] and Round to Int
        ts_final = np.clip(ts_final, 0, 50).astype(int)
        
        # 4. Calculate Sensitive Attribute (Performance_SD) based on Total Activity
        # Docs: Low (<160), Medium (160-240), High (>240)
        total_activity = np.sum(ts_final)
        if total_activity < 160:
            perf = "Low"
        elif total_activity <= 240:
            perf = "Medium"
        else:
            perf = "High"
            
        row = {
            'ID': i,
            'Name': name,
            'Surname': surname
        }
        for j in range(n_cols):
            row[f'H{j+1}'] = ts_final[j]
        
        # Add sensitive attribute
        row['Performance_SD'] = perf
        
        data.append(row)
        
    df = pd.DataFrame(data)
    
    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'dataset_raw.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated {n_rows} records following {output_path} schema")
    print("Columns: ID, Name, Surname, H1-H8, Performance_SD")

if __name__ == "__main__":
    generate_dataset()