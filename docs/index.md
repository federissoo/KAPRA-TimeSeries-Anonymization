# KAPRA: Protecting Time Series Privacy

This project explores the challenges of anonymizing time series data while preserving its utility for pattern-based analysis.

## The Core Problem: Beyond Numerical Values
In time series data, privacy is not just about hiding numbers. An individual's identity is tied to two facets:
1. **Values ($K_v$):** The exact numerical data (e.g., a specific salary or heart rate).
2. **Patterns ($K_p$):** The shape or trend of the data over time (e.g., "rapid growth" or "seasonal spikes").

Traditional methods like **k-Anonymity** only protect values. If an attacker knows even a small part of your data trend, they can identify you even in a crowd. This is known as a **Unified Attack**.

## Documentation Sections
To understand how KAPRA solves this, explore the following sections:

### 1. [Why k-Anonymity Fails for Time Series](k-anon-failure.md)
A practical demonstration of how traditional k-Anonymity leaves users vulnerable to pattern-based tracking.

### 2. [The KAPRA Solution: (k,P)-Anonymity](kapra-approach.md)
How the KAPRA framework integrates both Value and Pattern protection to ensure robust privacy.