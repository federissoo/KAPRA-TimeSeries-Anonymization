import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kapra_path = os.path.join(base_dir, "../docs/data/kapra_optimization_results.csv")
    naive_path = os.path.join(base_dir, "../docs/data/naive_optimization_results.csv") # Assuming this will differ
    
    try:
        df_kapra = pd.read_csv(kapra_path)
        df_kapra['Algorithm'] = 'KAPRA'
    except FileNotFoundError:
        print(f"Warning: {kapra_path} not found.")
        df_kapra = pd.DataFrame()

    try:
        df_naive = pd.read_csv(naive_path)
        df_naive['Algorithm'] = 'Naive'
    except FileNotFoundError:
        print(f"Warning: {naive_path} not found.")
        df_naive = pd.DataFrame()
        
    return df_kapra, df_naive

def plot_metrics(df_kapra, df_naive):
    if df_kapra.empty and df_naive.empty:
        print("No data to plot.")
        return

    # Combine for easier plotting
    df = pd.concat([df_kapra, df_naive], ignore_index=True)
    
    # Filter for a common representative configuration if possible, or aggregate
    # Let's plot VL vs K for a fixed P and Sax Level (e.g., P=2, Level=8)
    
    p_val = 2
    level_val = 8
    
    subset = df[(df['P'] == p_val) & ((df['SAX_LEVEL'] == level_val) | (df.get('MAX_LEVEL') == level_val))]
    
    if subset.empty:
        print(f"No data for P={p_val}, Level={level_val}. Plotting all.")
        subset = df
        
    # Setup plots
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # VL Plot
    sns.lineplot(data=subset, x='K', y='VL', hue='Algorithm', marker='o', ax=axes[0])
    axes[0].set_title(f'Value Loss vs K (P={p_val}, Level={level_val})')
    axes[0].set_ylabel('Average Value Loss')
    axes[0].grid(True)
    
    # PL Plot
    sns.lineplot(data=subset, x='K', y='PL', hue='Algorithm', marker='o', ax=axes[1])
    axes[1].set_title(f'Pattern Loss vs K (P={p_val}, Level={level_val})')
    axes[1].set_ylabel('Average Pattern Loss')
    axes[1].grid(True)
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../docs/data/metrics_comparison.png')
    plt.savefig(output_path)
    print(f"Saved metrics plot to {output_path}")
    plt.close()

def plot_cluster_example():
    # Load anonymized data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kapra_anon_path = os.path.join(base_dir, "../docs/data/kapra_anonymized.csv")
    
    if not os.path.exists(kapra_anon_path):
        print("KAPRA anonymized file not found.")
        return
        
    df = pd.read_csv(kapra_anon_path)
    
    # Pick a random group
    if 'GroupID' not in df.columns:
        print("GroupID not found in columns.")
        return
        
    group_ids = df['GroupID'].unique()
    if len(group_ids) == 0:
        return
        
    # Select a group with decent size
    selected_group = group_ids[0]
    for gid in group_ids:
        if len(df[df['GroupID'] == gid]) >= 3:
            selected_group = gid
            break
            
    group_data = df[df['GroupID'] == selected_group]
    
    # Parse H columns
    h_cols = [c for c in df.columns if c.startswith('H')]
    
    plt.figure(figsize=(10, 6))
    
    # Plot Envelope
    # Data is in format "[min-max]"
    
    lowers = []
    uppers = []
    
    for col in h_cols:
        val_str = group_data.iloc[0][col] # Envelope is same for all in group usually? 
        # Actually in the CSV strictly speaking it puts the same envelope for all? YES.
        # Format "[min-max]"
        val_str = val_str.strip("[]")
        parts = val_str.split('-')
        if len(parts) == 2: # Simple positive range
             l, u = float(parts[0]), float(parts[1])
        elif len(parts) > 2: # Negative numbers case? e.g. -5--2
             # This parsing is naive, assume positive for now or use regex if needed
             # Based on previous files, data seems positive/normalized? 
             # Let's simple parse:
             # Just use the string split logic carefully or regex
             import re
             matches = re.findall(r"[-+]?\d*\.\d+|\d+", val_str)
             if len(matches) >= 2:
                 l, u = float(matches[0]), float(matches[1])
             else:
                 l, u = 0, 0
        else:
             l, u = 0, 0
             
        lowers.append(l)
        uppers.append(u)
        
    x_axis = range(len(h_cols))
    
    plt.fill_between(x_axis, lowers, uppers, color='gray', alpha=0.3, label='Anonymization Envelope')
    plt.plot(x_axis, lowers, color='black', linestyle='--', linewidth=0.5)
    plt.plot(x_axis, uppers, color='black', linestyle='--', linewidth=0.5)
    
    plt.title(f'Cluster {selected_group} Visualization (KAPRA)')
    plt.xlabel('Time Points')
    plt.ylabel('Value')
    plt.legend()
    
    output_path = os.path.join(base_dir, '../docs/data/cluster_visualization.png')
    plt.savefig(output_path)
    print(f"Saved cluster plot to {output_path}")
    plt.close()

if __name__ == "__main__":
    df_k, df_n = load_data()
    plot_metrics(df_k, df_n)
    plot_cluster_example()
