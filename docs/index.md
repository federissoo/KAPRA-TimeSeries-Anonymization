# KAPRA: Strategic (k,P)-Anonymity for Time Series Data

This project implements the KAPRA framework to address privacy concerns in time series publishing. While traditional methods focus on hiding numerical values, KAPRA introduces a dual protection model to defend against sophisticated linkage attacks.

## The Privacy Challenge: Unified Attacks
In time series datasets, an individual's identity is exposed through two main channels:
- **Value Knowledge ($K_v$):** Specific numerical data points at certain timestamps.
- **Pattern Knowledge ($K_p$):** The shape, trend, or "signature" of the data over time.

When an adversary combines both, they perform a **Unified Attack**, which can identify individuals even when their data is partially obscured.

## Documentation Structure
- [Why k-Anonymity Fails](k-anon-failure.md): Analysis of how pattern-based linkage breaks traditional value-based anonymity.
- [The KAPRA Solution](kapra-approach.md): Detailed explanation of the (k,P)-Anonymity model and SAX transformation.

## Technical Implementation
The current implementation uses Python and Poetry, processing Quasi-Identifiers (QI) that include both categorical attributes (Dept, Seniority) and temporal sequences (H1 to H8).