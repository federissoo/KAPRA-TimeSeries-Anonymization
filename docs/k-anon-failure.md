# The Failure of Traditional k-Anonymity

Traditional k-Anonymity groups $k$ records together so they share the same range of values (Quasi-Identifiers). However, it ignores the **pattern** of the data.

## 🕵️ The Pattern-Linkage Attack
Imagine a group where $k=2$ (Alice and Bob). Their values are hidden within an "Envelope" $[80, 180]$.

| Record | Anonymization Envelope | **Pattern (Trend)** | Sensitive Data |
| :--- | :--- | :--- | :--- |
| **1 (Alice)** | [80 - 180] | **Rising** 📈 | Heart Disease |
| **2 (Bob)** | [80 - 180] | **Falling** 📉 | Healthy |

### Why it fails:
If an adversary knows that Alice's health is **deteriorating** (Rising trend), they can look at the table and see that only Record 1 matches that pattern. 
Even though her values are hidden, her identity is revealed with **100% probability** ($P_{breach} = 1$) because her pattern is unique within the group.

**Conclusion:** k-Anonymity is insufficient for time series because the "shape" of the data acts as a fingerprint.