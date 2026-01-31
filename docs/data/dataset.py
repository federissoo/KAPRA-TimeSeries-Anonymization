import numpy as np
import pandas as pd
import os

def generate_structured_work_activity(n_employees=200):
    np.random.seed(42)
    
    first_names = ['Mario', 'Giulia', 'Luca', 'Elena', 'Alessandro', 'Sofia', 'Francesco', 'Anna', 'Matteo', 'Chiara']
    last_names = ['Rossi', 'Bianchi', 'Verdi', 'Russo', 'Ferrari', 'Esposito', 'Romano', 'Gallo', 'Conti', 'Marini']
    
    data = []
    
    # Pattern base (Forma della curva)
    base_rising = np.linspace(10, 40, 8) 
    base_falling = np.linspace(40, 10, 8)
    base_peak = np.array([10, 20, 30, 40, 40, 30, 20, 10])
    base_flat = np.array([25, 25, 25, 25, 25, 25, 25, 25])

    patterns = [base_rising, base_falling, base_peak, base_flat]
    
    for i in range(n_employees):
        name = np.random.choice(first_names)
        surname = np.random.choice(last_names)
        
        # 1. Scelta del pattern (FORMA)
        base_pattern = patterns[np.random.choice(len(patterns))]
        
        # 2. Scelta dell'intensità (QUANTITÀ)
        # Shiftiamo la curva verso l'alto o il basso per simulare chi lavora di più/meno
        # -10 abbassa la media a 15 (totale ~120)
        # +10 alza la media a 35 (totale ~280)
        intensity_shift = np.random.randint(-12, 12) 
        
        # 3. Aggiunta rumore
        noise = np.random.normal(0, 4, size=8) 
        
        # Composizione finale
        time_series = base_pattern + intensity_shift + noise
        
        # Clip per restare in range sensati (0-50)
        time_series = np.clip(time_series, 0, 50).astype(int)
        
        # Calcolo performance
        # Media base 200. 
        # Con shift -10 -> 120. Con shift +10 -> 280.
        total = np.sum(time_series)
        
        # SOGLIE AGGIORNATE
        # Ho stretto i range attorno alla media di 200
        Y = 160  # Sotto 180 è Low (media < 22.5 ore/slot)
        X = 240  # Sopra 220 è High (media > 27.5 ore/slot)
        
        if total < Y: perf = 'Low'
        elif total > X: perf = 'High'
        else: perf = 'Medium'
        
        row = {'ID': i + 1, 'Name': name, 'Surname': surname}
        for h in range(8):
            row[f'H{h+1}'] = time_series[h]
        row['Performance_SD'] = perf
        data.append(row)
        
    return pd.DataFrame(data)

# Generazione e salvataggio
df = generate_structured_work_activity(200)

# Stampa di verifica distribuzione
print("Distribuzione Performance:")
print(df['Performance_SD'].value_counts())

output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "dataset_raw.csv")
df.to_csv(output_path, index=False)