import pandas as pd
import numpy as np

def generate_work_activity(n_employees=200):
    np.random.seed(44)
    
    # Liste per Identificatori Espliciti (EI)
    first_names = ['Mario', 'Giulia', 'Luca', 'Elena', 'Alessandro', 'Sofia', 'Francesco', 'Anna', 'Matteo', 'Chiara']
    last_names = ['Rossi', 'Bianchi', 'Verdi', 'Russo', 'Ferrari', 'Esposito', 'Romano', 'Gallo', 'Conti', 'Marini']
    
    departments = ['IT', 'Sales', 'HR', 'Marketing']
    seniority = ['Junior', 'Mid', 'Senior']
    performance_levels = ['Low', 'Medium', 'High']
    
    # Thresholds for performance
    # Low < Y, High > X
    Y = 100
    X = 180
    
    data = []
    for i in range(n_employees):
        # Selezione casuale di Nome e Cognome (EI)
        name = np.random.choice(first_names)
        surname = np.random.choice(last_names)
        
        dept = np.random.choice(departments)
        level = np.random.choice(seniority)
        
        # Random generation 0-40, independent of role
        time_series = np.random.randint(0, 41, size=8)
        
        # Performance determined by total activity
        total = np.sum(time_series)
        if total < Y:
            perf = 'Low'
        elif total > X:
            perf = 'High'
        else:
            perf = 'Medium'
        
        # Costruzione della riga con EI all'inizio
        row = {
            'Name': name, 
            'Surname': surname, 
            'Dept': dept, 
            'Seniority': level
        }
        
        for h in range(8):
            row[f'H{h+1}'] = time_series[h]
            
        row['Performance_SD'] = perf
        data.append(row)
        
    return pd.DataFrame(data)

# Generazione e salvataggio
df = generate_work_activity(200)
df.to_csv('remote_work_activity_raw.csv', index=False)

print("Dataset 'RAW' generato con successo!")
print(df.head())