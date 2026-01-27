# KAPRA: Strategic (k,P)-Anonymity for Time Series Data

This repository contains an implementation of the **KAPRA** (k-Anonymity with Pattern Representation) algorithm, based on the research paper: [*"Supporting Pattern-Preserving Anonymization For Time-Series Data"*](http://chaozhang.org/papers/2013-tkde-privacy.pdf).

## The Problem: Unified Attacks
Traditional k-Anonymity focuses solely on hiding numerical values (QI values, $K_v$). However, time series data is vulnerable to **Pattern-based Linkage Attacks** ($K_p$). 

An adversary knowing a partial trend of a target (e.g., "the subject's heart rate spiked on Tuesday") can identify an individual even if their exact values are hidden within an envelope.

## The Solution: (k,P)-Anonymity
KAPRA protects data by ensuring every published record satisfies two constraints:
1. **k-Anonymity**: At least $k$ records share the same **Anonymization Envelope** (Value Range).
2. **P-Anonymity**: At least $P$ records within each group share the same **Pattern Representation (PR)**.

This prevents "Unified Attacks" by making users indistinguishable by both their values and their data trends.

## Core Concepts

### 1. Pattern Representation (SAX)
We use **Symbolic Aggregate Approximation (SAX)** to transform complex time series into concise strings (e.g., "aabbc").
- **High alphabet size**: Lower **Pattern Loss (PL)** but harder to satisfy P-anonymity.
- **Low alphabet size**: Higher PL but easier to group records.

### 2. Information Loss Metrics
The algorithm aims to minimize:
- **Instant Value Loss (VL)**: Measured as the width of the envelopes.
  $$VL(Q) = \sqrt{\sum_{i=1}^{n} \frac{(r_i^+ - r_i^-)^2}{n}}$$
- **Pattern Loss (PL)**: The distortion introduced by symbolization.

## Algorithm Workflow
The implementation follows a **Bottom-Up** strategy:
1. **Pattern Grouping**: Cluster series with similar SAX representations.
2. **k-Anonymization**: Merge clusters to satisfy the $k$ requirement while minimizing $VL$.
3. **Recycling Bad-Leaves**: Handles "outlier" patterns by generalizing their PR to avoid data suppression.

## Getting Started
(Add your installation and usage instructions here once the code is ready!)