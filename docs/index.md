<script>
  window.MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']]
    }
  };
</script>
<script id="MathJax-script" async 
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
</script>

# KAPRA: Strategic (k,P)-Anonymity for Time Series Data

This project implements the KAPRA algorithm, as described in the paper [*"Supporting Pattern-Preserving Anonymization For Time-Series Data"*](http://chaozhang.org/papers/2013-tkde-privacy.pdf), to address privacy issues in the publishing of time-series data.

## The Privacy Challenge: Unified Attacks
In time series datasets, an individual's identity is exposed through two main channels:
- **Value Knowledge ($K_v$):** Specific numerical data points at certain timestamps (QIs).
- **Pattern Knowledge ($K_p$):** The shape, trend, or "signature" of the data over time (Patterns).

When an adversary combines both, they perform a **Unified Attack**, which can identify individuals even when their data is partially obscured.

## Documentation Structure
- [Why k-Anonymity Fails](k-anon-failure.md)
- [Naive Algorithm](naive-algo.md)
- [KAPRA Algorithm](kapra-algo.md)

## Technical Implementation
The current implementation uses Python and Poetry, processing Quasi-Identifiers (QI) that focus on temporal sequences (H1 to H8).