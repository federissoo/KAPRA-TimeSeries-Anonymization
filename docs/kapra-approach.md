# The KAPRA Approach: (k,P)-Anonymity

KAPRA (k-Anonymity with Pattern Representation) is designed to resist unified attacks by enforcing a dual constraint: **(k,P)-Anonymity**.

## 🛡️ Dual Protection
A dataset is $(k,P)$-anonymous if:
1. **k-Constraint**: Each record is indistinguishable from at least $k-1$ others regarding their values (Envelopes).
2. **P-Constraint**: Each record shares the same **Pattern Representation (PR)** with at least $P-1$ other records in its group.

## 🛠️ How it Works: SAX & Bottom-Up Strategy
KAPRA uses **Symbolic Aggregate Approximation (SAX)** to convert complex graphs into simple strings (e.g., "abc").

### The Strategy:
1. **Cluster by Pattern**: First, the algorithm groups series that have the same shape (SAX string).
2. **Refine by Value**: It then ensures these groups satisfy the $k$ requirement with minimal **Value Loss (VL)**.
3. **Handle Outliers**: If a pattern is too rare to meet the $P$ requirement, KAPRA "recycles" it by generalizing the SAX string until a group can be formed.

By ensuring that at least $P$ people have the same trend, the probability of identification drops to $1/P$.