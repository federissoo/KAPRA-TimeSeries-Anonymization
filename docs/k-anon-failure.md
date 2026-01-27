# The Failure of Traditional k-Anonymity in Time-Series

[cite_start]**Conventional k-anonymity** protects privacy by grouping records into "Anonymization Envelopes" (AE), which are anonymization envelopes defined by value ranges[cite: 88, 181]. [cite_start]However, this model proves inadequate for time-series data due to a critical limitation: the destruction of analytical utility, known as **Pattern Loss**[cite: 9, 44, 91].

## 1. Pattern Destruction (Utility Loss)
[cite_start]In time-series, the utility of the data depends not only on point values but also on the correlations between them over time[cite: 193]. Traditional k-anonymity fails because:
* [cite_start]**Featureless Envelopes**: Grouping based solely on value proximity creates envelopes that "flatten" trends[cite: 88, 148]. [cite_start]If records in a group have opposing trends, the resulting interval will cover the entire range, making the original trend unrecognizable[cite: 91, 192].
* [cite_start]**Unusability for Complex Queries**: The loss of patterns prevents the effective execution of fundamental queries [cite: 86, 188] such as:
    * [cite_start]**PSQ (Pattern matching Similarity Query)**: Searching for series with trends similar to a target sequence[cite: 35, 214].
    * [cite_start]**PRQ (Pattern matching Range Query)**: Selecting records based on trend predicates (e.g., "select those who have grown by at least 50%")[cite: 210, 212].

---

## 2. Case Study: High Value Loss vs. Insufficient Privacy
Let us consider a dataset with Quasi-Identifier (QI) attributes **Department** and **Seniority**. [cite_start]The original data shows distinct trends for two Junior employees in Human Resources[cite: 189, 191].

### [cite_start]Pre k-anon Status (Micro-data) [cite: 176]
| Record | Dept | Seniority | H1 (Value) | H2 (Value) | **Real Trend** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | HR | Junior | 10 | 37 | **Rising** |
| 2 | HR | Junior | 40 | 31 | **Falling** |

### [cite_start]Post k-anon Status (k=2) [cite: 180, 226]
[cite_start]To satisfy k-anonymity, the values of H1 and H2 are generalized into intervals[cite: 179]. [cite_start]This generates a significant **Instant Value Loss (VL)**, calculated based on the width of the intervals[cite: 322, 325]:

$$VL(Q)=\sqrt{\sum_{i=1}^{n}(r_{i}^{+}-r_{i}^{-})^{2}/n}$$

| Record | Dept | Seniority | H1 (QI Range) | H2 (QI Range) | **Perceived Pattern** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | HR | Junior | [10, 40] | [31, 37] | Unknown / Flat |
| 2 | HR | Junior | [10, 40] | [31, 37] | Unknown / Flat |

---

> [cite_start]**Paper Conclusion**: The **(k,P)-anonymity** model is necessary, as it guarantees k-anonymity on values and P-anonymity on patterns, ensuring that each pattern is shared by at least P records[cite: 10, 108, 112, 292].