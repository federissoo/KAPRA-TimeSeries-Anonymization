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

# The KAPRA Solution: (k,P)-Anonymity

To resist unified attacks, the KAPRA framework enforces a dual requirement on the published database.

## (k,P)-Anonymity Requirements
A dataset satisfies the KAPRA model if:
1. **k-Requirement:** Every record is indistinguishable from at least $k-1$ others regarding its Quasi-Identifier values (Value Envelopes).
2. **P-Requirement:** Every record within a group shares the same **Pattern Representation (PR)** with at least $P-1$ others.

## Pattern Representation (PR) via SAX
KAPRA utilizes **Symbolic Aggregate Approximation (SAX)** to convert numerical sequences into symbolic strings (e.g., "aabbc").
- This process reduces dimensionality while preserving the essential "shape" of the data.
- By ensuring at least $P$ records have the same SAX string, we prevent an attacker from using trends to isolate individuals.

## Quality Metrics
The algorithm optimizes for two types of information loss:
- **Instant Value Loss (VL):** The error introduced by the width of the envelopes.
  $$VL(Q) = \sqrt{\sum_{i=1}^{n} \frac{(r_i^+ - r_i^-)^2}{n}}$$
- **Pattern Loss (PL):** The distortion caused by converting numerical data into symbols.



By balancing $k$ and $P$, KAPRA ensures that the probability of identification remains below a predefined threshold for all users.