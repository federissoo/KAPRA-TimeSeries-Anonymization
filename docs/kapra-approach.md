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

To resist unified attacks, the KAPRA algorithm enforces a dual requirement on the data.

## (k,P)-Anonymity Requirements
A dataset satisfies the KAPRA model if:
1. **k-Requirement:** Every record is indistinguishable from at least $k-1$ others regarding its Quasi-Identifier values (Value Envelopes).
2. **P-Requirement:** Every record within a group shares the same **Pattern Representation (PR)** with at least $P-1$ others.

## Top-down vs Bottom-up
It is possible to adopt a **top-down approach**, in which the dataset is initially partitioned into groups satisfying the k-anonymity requirement and then further refined to meet the P requirement. However, this strategy is not optimal, as it causes a significant loss of patterns and reduces the accuracy of similarity-based queries.

KAPRA instead adopts a **bottom-up approach**, in which records are first grouped according to pattern similarity to satisfy the P requirement and only subsequently aggregated to ensure k-anonymity. Although more complex, this strategy allows for better preservation of temporal structures and achieves a better trade-off between privacy protection and data utility.

## Pattern Representation (PR) via SAX
KAPRA utilizes **Symbolic Aggregate Approximation (SAX)** to convert numerical sequences into symbolic strings (e.g., "aabbc").
- This process reduces dimensionality while preserving the essential "shape" of the data.
- By ensuring at least $P$ records have the same SAX string, we prevent an attacker from using trends to isolate individuals.
- A key parameter in SAX is the **Level**, which controls the granularity of the representation: higher levels produce symbolic sequences that more accurately capture the original temporal shape, while lower levels result in coarser and more abstract descriptions.
- KAPRA aims to keep the Level as high as possible to minimize pattern loss, but dynamically reduces it when necessary to ensure that at least $P$ records share the same pattern representation, thereby satisfying the privacy constraint.

## Breach Probability (BP)
The **Breach Probability** formula quantifies the real-time risk based on an attacker's specific background knowledge, combining both values ($K_v$) and patterns ($K_p$). While the full equation accounts for the distribution of sensitive values across multiple groups, the value $1/P$ represents the **formal upper bound** in the worst-case scenario.

$$P_{breach}(Q) = \frac{b}{P \cdot e[K_v \cup K_p]}$$

By enforcing the **$P$-requirement**, KAPRA guarantees that the re-identification probability never exceeds the $1/P$ threshold, regardless of how much background information the adversary possesses. This bound ensures that even if an attacker isolates a single group ($e = 1$), the target remains indistinguishable from at least $P-1$ other records sharing the same pattern.

## Quality Metrics
The algorithm optimizes for two types of information loss:
- **Instant Value Loss (VL):** The error introduced by the width of the envelopes.
  $$VL(Q) = \sqrt{\sum_{i=1}^{n} \frac{(r_i^+ - r_i^-)^2}{n}}$$
- **Pattern Loss (PL):** The distortion caused by converting numerical data into symbols.



By balancing $k$ and $P$, KAPRA ensures that the probability of identification remains below a predefined threshold for all users.