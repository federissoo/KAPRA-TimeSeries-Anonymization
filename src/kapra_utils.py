
import numpy as np
import pandas as pd

def calculate_envelope_and_vl(cluster):
    """
    Calculates the Anonymization Envelope (AE) and Instant Value Loss (VL) 
    for a cluster of time series.

    The envelope consists of:
    - Lower Bound (r_min): Minimum value at each timestamp across the cluster.
    - Upper Bound (r_max): Maximum value at each timestamp across the cluster.

    The Instant Value Loss (VL) is calculated as:
    VL(Q) = sqrt( sum( (r_max_i - r_min_i)^2 ) / n )
    where n is the number of timestamps (length of the sequence).

    Args:
        cluster (array-like): A collection of time series. 
                              Can be a list of lists, a numpy array (m_series, n_timestamps), 
                              or a pandas DataFrame/Series.

    Returns:
        tuple: (lower_bound, upper_bound, vl)
            - lower_bound (np.array): The sequence of minimum values.
            - upper_bound (np.array): The sequence of maximum values.
            - vl (float): The calculated Instant Value Loss.
    """
    # Convert input to numpy array
    if isinstance(cluster, pd.DataFrame):
        data = cluster.values
    elif isinstance(cluster, list):
        data = np.array(cluster)
    else:
        try:
            data = np.array(cluster)
        except Exception as e:
            raise ValueError(f"Could not convert input cluster to numpy array: {e}")

    # Ensure we have a 2D array (m_series, n_timestamps)
    if data.ndim == 1:
        # If a single series is passed, treat it as a cluster of size 1 
        # (though VL will be 0)
        data = data.reshape(1, -1)
    
    # n è il numero di timestamp (colonne)
    n = data.shape[1]
    
    if n == 0:
        return np.array([]), np.array([]), 0.0

    # calcolo Lower Bound e Upper Bound
    # axis=0 significa che riduciamo le righe (serie), trovando min/max per ogni colonna (timestamp)
    lower_bound = np.min(data, axis=0)
    upper_bound = np.max(data, axis=0)

    # calcolo VL
    diff = upper_bound - lower_bound
    squared_diff = diff ** 2
    sum_squared_diff = np.sum(squared_diff)
    
    # evito la divisione per zero se n è 0 (gestito sopra, ma è buona pratica)
    if n > 0:
        vl = np.sqrt(sum_squared_diff / n)
    else:
        vl = 0.0

    return lower_bound, upper_bound, vl
