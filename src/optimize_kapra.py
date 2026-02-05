import pandas as pd
from kapra_anonymization import run_kapra_anonymization
import os
import sys

def optimize():
    # results file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv = os.path.join(base_dir, "../docs/data/kapra_optimization_results.csv")
    
    k_values = [5, 10, 20, 50]
    p_values = [2, 3, 5, 8]
    # Reduce max levels slightly as KAPRA is generally slower or higher levels might not be needed
    # But for consistency with naive, we keep same range.
    max_levels = [3, 5, 8, 10, 15, 20]
    
    results = []
    
    total = len(k_values) * len(p_values) * len(max_levels)
    count = 0
    
    print(f"Starting KAPRA optimization with {total} combinations...")
    
    for k in k_values:
        for p in p_values:
            for ml in max_levels:
                count += 1
                print(f"[{count}/{total}] Running K={k}, P={p}, SAX_LEVEL={ml}...", end="\r")
                try:
                    res = run_kapra_anonymization(K=k, P=p, SAX_LEVEL=ml, verbose=False)
                    if res:
                        results.append(res)
                except Exception as e:
                    print(f"\nError with K={k}, P={p}, ML={ml}: {e}")
    
    print("\n")                
    df = pd.DataFrame(results)
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Optimization complete. Results saved to {output_csv}")
    
    # Simple Analysis
    if not df.empty:
        # Normalize to find 'best' compromise
        min_vl, max_vl = df['VL'].min(), df['VL'].max()
        min_pl, max_pl = df['PL'].min(), df['PL'].max()
        
        # Max-Min normalization (0 is best, 1 is worst)
        if max_vl != min_vl:
            df['norm_VL'] = (df['VL'] - min_vl) / (max_vl - min_vl)
        else:
            df['norm_VL'] = 0
            
        if max_pl != min_pl:
            df['norm_PL'] = (df['PL'] - min_pl) / (max_pl - min_pl)
        else:
            df['norm_PL'] = 0
            
        df['score'] = df['norm_VL'] + df['norm_PL']
        
        best = df.sort_values(by='score').iloc[0]
        print("\nBest Configuration (balanced VL/PL):")
        print(best)
        
        print("\nTop 5 Configs:")
        print(df.sort_values(by='score').head(5)[['K', 'P', 'SAX_LEVEL', 'VL', 'PL', 'score']])

if __name__ == "__main__":
    optimize()
