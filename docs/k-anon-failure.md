# The Failure of Traditional k-Anonymity

Traditional k-anonymity protects data by grouping records into **Anonymization Envelopes**. However, as demonstrated in our experiments, protecting values alone is insufficient for time series.

## Pattern-Linkage Attack
Even if $k$ records are grouped to share the same range of values, their individual trends can remain unique within that group.

### Case Study: High Value Loss vs. Low Privacy
In our latest experiment, we processed a group categorized as **HR, Junior**. The data was obscured using intervals, resulting in a **Value Loss (VL)** of **37.6812**.

| Record | Dept | Seniority | H1 | H2 | Trend |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | HR | Junior | [0-40] | [3-37] | Rising |
| 2 | HR | Junior | [0-40] | [3-37] | Falling |



Despite the high Value Loss, the identity is not secure:
1. **Adversary Knowledge:** The attacker knows the target is a Junior in HR and has a "Rising" activity trend.
2. **Identification:** By observing the trends within the [0-40] envelope, the attacker can distinguish Alice (Rising) from Bob (Falling).
3. **Breach:** The identity is revealed with a probability of 1 ($P_{breach} = 1$), rendering the k-anonymity useless against pattern knowledge.

## Partial Pattern Knowledge
The vulnerability is exacerbated by **Partial Pattern Knowledge**. An adversary only needs to know a segment of the series (e.g., a spike at H4) to successfully link a record to an individual, even if the rest of the sequence is anonymous.