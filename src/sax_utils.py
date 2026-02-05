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
    2: [0],
    3: [-0.43, 0.43],
    4: [-0.67, 0, 0.67],
    5: [-0.84, -0.25, 0.25, 0.84],
    6: [-0.97, -0.43, 0, 0.43, 0.97],
    7: [-1.07, -0.57, -0.18, 0.18, 0.57, 1.07],
    8: [-1.15, -0.67, -0.32, 0, 0.32, 0.67, 1.15],
    9: [-1.22, -0.76, -0.43, -0.14, 0.14, 0.43, 0.76, 1.22],
    10: [-1.28, -0.84, -0.52, -0.25, 0, 0.25, 0.52, 0.84, 1.28],
    11: [-1.34, -0.91, -0.6, -0.35, -0.11, 0.11, 0.35, 0.6, 0.91, 1.34],
    12: [-1.38, -0.97, -0.67, -0.43, -0.21, 0.0, 0.21, 0.43, 0.67, 0.97, 1.38],
    13: [-1.43, -1.02, -0.74, -0.5, -0.29, -0.1, 0.1, 0.29, 0.5, 0.74, 1.02, 1.43],
    14: [-1.47, -1.07, -0.79, -0.57, -0.37, -0.18, 0.0, 0.18, 0.37, 0.57, 0.79, 1.07, 1.47],
    15: [-1.5, -1.11, -0.84, -0.62, -0.43, -0.25, -0.08, 0.08, 0.25, 0.43, 0.62, 0.84, 1.11, 1.5],
    16: [-1.53, -1.15, -0.89, -0.67, -0.49, -0.32, -0.16, 0.0, 0.16, 0.32, 0.49, 0.67, 0.89, 1.15, 1.53],
    17: [-1.56, -1.19, -0.93, -0.72, -0.54, -0.38, -0.22, -0.07, 0.07, 0.22, 0.38, 0.54, 0.72, 0.93, 1.19, 1.56],
    18: [-1.59, -1.22, -0.97, -0.76, -0.59, -0.43, -0.28, -0.14, 0.0, 0.14, 0.28, 0.43, 0.59, 0.76, 0.97, 1.22, 1.59],
    19: [-1.62, -1.25, -1.0, -0.8, -0.63, -0.48, -0.34, -0.2, -0.07, 0.07, 0.2, 0.34, 0.48, 0.63, 0.8, 1.0, 1.25, 1.62],
    20: [-1.64, -1.28, -1.04, -0.84, -0.67, -0.52, -0.39, -0.25, -0.13, 0.0, 0.13, 0.25, 0.39, 0.52, 0.67, 0.84, 1.04, 1.28, 1.64]
}

# Cerca la funzione ts_to_sax
def ts_to_sax(series, level, n_segments=4): 
    """
    Convert a time series to a SAX string.
    """
    # Z-normalization
    zn_series = z_normalization(series)
    
    # PAA - da 8 dati a 4
    paa_rep = paa(zn_series, n_segments)
    
    # Discretization
    if level not in SAX_BREAKPOINTS:
        # per livello 1
        if level < 3: return "a" * n_segments
        raise ValueError(f"Alphabet size {level} unsupported")
        
    breakpoints = SAX_BREAKPOINTS[level]
    
    sax_string = []
    for val in paa_rep:
        idx = np.searchsorted(breakpoints, val)
        sax_string.append(chr(97 + idx)) # A + idx
        
    return "".join(sax_string)

def sax_to_values(sax_string, alphabet_size, original_length):
    """
    Reconstruct a time series (z-normalized) from a SAX string.
    Maps each symbol to the centroid of its Gaussian bin.
    """
    if alphabet_size not in SAX_BREAKPOINTS:
        raise ValueError(f"Alphabet size {alphabet_size} not supported.")
        
    breakpoints = SAX_BREAKPOINTS[alphabet_size]
    
    # Simple midpoint approximation (clamped at +/- 3 sigma)
    # This rebuilds the 'reconstructed' values based on the SAX string
    extended_bps = [-3] + list(breakpoints) + [3]
    
    values = []
    for char in sax_string:
        idx = ord(char) - 97
        if 0 <= idx < len(extended_bps) - 1:
            low = extended_bps[idx]
            high = extended_bps[idx+1]
            centroid = (low + high) / 2
            values.append(centroid)
        else:
            # Should not happen if char is valid
            values.append(0)
            
    # Since n_segments might be < original_length, we need to expand PAA
    values = np.array(values)
    if len(values) != original_length:
        # Repeat values to match original length
        # Assuming equal sized segments (approx)
        return np.repeat(values, np.ceil(original_length / len(values)))[:original_length]
    return values

def calculate_feature_vector(series):
    """
    Construct the feature vector p(Q) as the set of all differentials
    between every pair of attributes: q_i - q_j.
    """
    series = np.array(series)
    n = len(series)
    features = []
    for i in range(n):
        for j in range(n):
            if i != j:
                features.append(series[i] - series[j])
    return np.array(features)

def calculate_pattern_loss(series, sax_string, alphabet_size):
    """
    Calculate Pattern Loss (PL) as the cosine distance between the 
    feature vector of the original series and the reconstructed series.
    
    PL(Q, P) = CosineDistance(p(Q), p*(Q))
             = 1 - CosineSimilarity
    """
    # Original Z-normalized series
    zn = z_normalization(series)
    
    # Reconstructed series from SAX
    rec = sax_to_values(sax_string, alphabet_size, len(series))
    
    # Feature Vectors
    fv_orig = calculate_feature_vector(zn)
    fv_rec = calculate_feature_vector(rec)
    
    # Cosine Similarity
    # sim = (A . B) / (||A|| * ||B||)
    
    dot_product = np.dot(fv_orig, fv_rec)
    norm_orig = np.linalg.norm(fv_orig)
    norm_rec = np.linalg.norm(fv_rec)
    
    if norm_orig == 0 or norm_rec == 0:
        # If one vector is zero, similarity is undefined (or 0).
        # Loss is max (1.0 or high?)
        # If both are zero (flat series), they are identical -> Loss 0.
        if norm_orig == 0 and norm_rec == 0:
            return 0.0
        return 1.0
        
    cosine_sim = dot_product / (norm_orig * norm_rec)
    
    # Cosine Distance
    # Strictly, distance = 1 - similarity
    # Similarity is in [-1, 1]. Distance in [0, 2].
    # Usually normalized to [0,1] or just raw distance.
    # Paper implies distance.
    
    return 1.0 - cosine_sim
