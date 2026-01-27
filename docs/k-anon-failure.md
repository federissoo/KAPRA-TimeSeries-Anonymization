# The Failure of Traditional k-Anonymity in Time-Series

**Conventional k-anonymity** protects privacy by grouping records into "Anonymization Envelopes" (AE), which are anonymization envelopes defined by value ranges. However, this model proves inadequate for time-series data due to a critical limitation: the destruction of analytical utility, known as **Pattern Loss**.

## 1. Pattern Destruction (Utility Loss)
In time-series, the utility of the data depends not only on point values but also on the correlations between them over time. Traditional k-anonymity fails because:

* **Featureless Envelopes**: Grouping based solely on value proximity creates envelopes that "flatten" trends. If records in a group have opposing trends, the resulting interval will cover the entire range, making the original trend unrecognizable.

* **Unusability for Complex Queries**: The loss of patterns prevents the effective execution of fundamental queries such as:
    * **PSQ (Pattern matching Similarity Query)**: Searching for series with trends similar to a target sequence.
    * **PRQ (Pattern matching Range Query)**: Selecting records based on trend predicates (e.g., "select those who have grown by at least 50%").

## 2. Example
Let us consider a micro-example of the project's dataset with Quasi-Identifier (QI) attributes **Department** and **Seniority**. The original data shows distinct trends for two Junior employees in Human Resources.

### Pre k-anon Status (Micro-data)

| Record | Dept | Seniority | H1 (Value) | H2 (Value) | **Real Trend** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | HR | Junior | 10 | 37 | **Rising** |
| 2 | HR | Junior | 40 | 31 | **Falling** |

### Post k-anon Status (k=2)

| Record | Dept | Seniority | H1 (QI Range) | H2 (QI Range) | **Perceived Pattern** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | HR | Junior | [10, 40] | [31, 37] | Unknown |
| 2 | HR | Junior | [10, 40] | [31, 37] | Unknown |

The **(k,P)-anonymity** model is necessary, as it guarantees k-anonymity on values and P-anonymity on patterns, ensuring that each pattern is shared by at least P records.