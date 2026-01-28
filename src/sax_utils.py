import numpy as np


def z_normalization(series):
    """
    Apply Z-normalization to a time series: (x - mu) / sigma.
    If standard deviation is 0, returns array of zeros.
    """
    series = np.array(series)
    mean = np.mean(series)
    std = np.std(series)
    if std < 1e-6:
        return np.zeros_like(series)
    return (series - mean) / std

def paa(series, n_segments):
    """
    Piecewise Aggregate Approximation (PAA).
    Dimensionality reduction: reduces series length to n_segments.
    Each segment value is the mean of the points in that segment.
    """
    series = np.array(series)
    n = len(series)
    
    if n == n_segments:
        return series
    
    if n % n_segments == 0:
        # Simple reshaping if divisible
        return np.mean(series.reshape(n_segments, -1), axis=1)
    else:
        # Handling non-divisible lengths (more complex, but standard PAA)
        # For simplicity in this project (H1..H8), we usually use n_segments that divides length or roughly equal
        # Let's try a simple split approach using array_split
        splits = np.array_split(series, n_segments)
        return np.array([np.mean(segment) for segment in splits])

# Breakpoints for N(0,1) from SAX literature
# Keys are alphabet sizes
SAX_BREAKPOINTS = {
    3: [-0.43, 0.43],
    4: [-0.67, 0, 0.67],
    5: [-0.84, -0.25, 0.25, 0.84],
    6: [-0.97, -0.43, 0, 0.43, 0.97],
    7: [-1.07, -0.57, -0.18, 0.18, 0.57, 1.07],
    8: [-1.15, -0.67, -0.32, 0, 0.32, 0.67, 1.15],
    9: [-1.22, -0.76, -0.43, -0.14, 0.14, 0.43, 0.76, 1.22],
    10: [-1.28, -0.84, -0.52, -0.25, 0, 0.25, 0.52, 0.84, 1.28]
}

def ts_to_sax(series, n_segments, alphabet_size):
    """
    Convert a time series to a SAX string.
    Steps:
    1. Z-normalization
    2. PAA (reduce to n_segments)
    3. Discretization using Gaussian breakpoints
    """
    # 1. Z-normalization
    zn_series = z_normalization(series)
    
    # 2. PAA
    paa_rep = paa(zn_series, n_segments)
    
    # 3. Discretization
    if alphabet_size not in SAX_BREAKPOINTS:
        raise ValueError(f"Alphabet size {alphabet_size} not supported in efficient implementation. Supported: {list(SAX_BREAKPOINTS.keys())}")
        
    breakpoints = SAX_BREAKPOINTS[alphabet_size]
    
    # Map PAA values to symbols
    # ASCII 'a' is 97
    sax_string = []
    for val in paa_rep:
        # Find the interval index
        # searchsorted returns the index where val would be inserted to maintain order
        # For breakpoints [-0.67, 0, 0.67]:
        # val < -0.67 -> idx 0 ('a')
        # -0.67 <= val < 0 -> idx 1 ('b')
        # 0 <= val < 0.67 -> idx 2 ('c')
        # val >= 0.67 -> idx 3 ('d')
        idx = np.searchsorted(breakpoints, val)
        sax_string.append(chr(97 + idx))
        
    return "".join(sax_string)

def sax_to_values(sax_string, alphabet_size, original_length):
    """
    Reconstruct a time series (z-normalized) from a SAX string.
    Maps each symbol to the centroid of its Gaussian bin.
    """
    if alphabet_size not in SAX_BREAKPOINTS:
        raise ValueError(f"Alphabet size {alphabet_size} not supported.")
        
    breakpoints = SAX_BREAKPOINTS[alphabet_size]
    # Add -inf and +inf for first and last bins logic
    # But usually we just use the breakpoints.
    # The bins are: (-inf, b0), [b0, b1), [b1, b2), ... [bk, +inf)
    # We need centroids. 
    # For standard normal, we can precompute centroids or just take midpoints of breakpoints (clamping ends).
    
    # Simple midpoint approximation (clamped at +/- 3 sigma)
    extended_bps = [-3] + list(breakpoints) + [3]
    
    values = []
    for char in sax_string:
        idx = ord(char) - 97
        # Bin is extended_bps[idx] to extended_bps[idx+1]
        low = extended_bps[idx]
        high = extended_bps[idx+1]
        centroid = (low + high) / 2
        values.append(centroid)
        
    # values is now a PAA vector of length len(sax_string)
    # We need to expand it to original_length
    n_segments = len(sax_string)
    segment_size = original_length // n_segments
    remainder = original_length % n_segments
    
    reconstructed = []
    for i, val in enumerate(values):
        count = segment_size + (1 if i < remainder else 0)
        reconstructed.extend([val] * count)
        
    return np.array(reconstructed)

def calculate_pattern_loss(series, sax_string, alphabet_size):
    """
    Calculate Pattern Loss: Euclidean distance between Z-normalized series 
    and its SAX reconstruction.
    """
    zn = z_normalization(series)
    rec = sax_to_values(sax_string, alphabet_size, len(series))
    
    # Euclidean Distance
    dist = np.linalg.norm(zn - rec)
    
    # Normalize by Length? Usually just distance.
    # Or RMSE? "Misura la distorsione".
    # Let's use RMSE to be comparable across different lengths/datasets.
    rmse = dist / np.sqrt(len(series))
    return rmse
