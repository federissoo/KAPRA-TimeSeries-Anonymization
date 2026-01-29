import numpy as np
import pandas as pd
import os

def generate_structured_work_activity(n_employees=200):
    np.random.seed(42)
    
    first_names = ['Mario', 'Giulia', 'Luca', 'Elena', 'Alessandro', 'Sofia', 'Francesco', 'Anna', 'Matteo', 'Chiara']
    last_names = ['Rossi', 'Bianchi', 'Verdi', 'Russo', 'Ferrari', 'Esposito', 'Romano', 'Gallo', 'Conti', 'Marini']
    
    data = []
    
    # 3 pattern base (Profili)
    # 1. inizia basso, finisce alto
    base_rising = np.linspace(10, 40, 8) 
    # 2. inizia alto, finisce basso
    base_falling = np.linspace(40, 10, 8)
    # 3. basso agli estremi, alto al centro (es. pausa pranzo lunga o meeting)
    base_peak = np.array([10, 20, 30, 40, 40, 30, 20, 10])
    # 4. lavoro costante
    base_flat = np.array([25, 25, 25, 25, 25, 25, 25, 25])

    patterns = [base_rising, base_falling, base_peak, base_flat]
    
    for i in range(n_employees):
        name = np.random.choice(first_names)
        surname = np.random.choice(last_names)
        
        # Scegliamo un pattern a caso per questo impiegato
        base_pattern = patterns[np.random.choice(len(patterns))]
        
        # rumore casuale (ma non troppo)
        # noise scale = 5 garantisce forma rimanga simile
        noise = np.random.normal(0, 5, size=8) 
        time_series = base_pattern + noise
        
        time_series = np.clip(time_series, 0, 50).astype(int)
        
        # Calcolo performance
        total = np.sum(time_series)
        Y, X = 150, 250
        if total < Y: perf = 'Low'
        elif total > X: perf = 'High'
        else: perf = 'Medium'
        
        row = {'ID': i + 1, 'Name': name, 'Surname': surname}
        for h in range(8):
            row[f'H{h+1}'] = time_series[h]
        row['Performance_SD'] = perf
        data.append(row)
        
    return pd.DataFrame(data)

df = generate_structured_work_activity(200)

output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "dataset_raw.csv")

df.to_csv(output_path, index=False)
print(f"Dataset salvato in: {output_path}")