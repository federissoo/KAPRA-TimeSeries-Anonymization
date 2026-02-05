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

## Generazione del Dataset Sintetico

### Panoramica

Il dataset utilizzato per testare l'algoritmo di anonimizzazione simula i carichi di lavoro orari di un gruppo di dipendenti aziendali. L'obiettivo è fornire una base di dati realistica che contenga **pattern temporali riconoscibili** (es. chi inizia piano e accelera, chi ha un picco a metà giornata, ecc.) per verificare la capacità dell'algoritmo di preservare queste forme anche dopo l'anonimizzazione.

### Metodologia di Generazione

Lo script di generazione (`dataset.py`) crea dati sintetici combinando pattern comportamentali predefiniti con elementi di casualità per simulare la variabilità umana.

#### 1. Pattern Base (Forma)
Ogni dipendente viene assegnato casualmente a uno dei 4 profili di attività base ("Archetipi"):

*   **Rising (Crescente):** Inizia con bassa attività e aumenta progressivamente verso fine giornata.
    *   *Esempio:* Chi carbura lentamente e finisce "in sprint".
*   **Falling (Decrescente):** Parte forte e cala l'intensità nel corso delle 8 ore.
    *   *Esempio:* Chi smaltisce il grosso del lavoro al mattino.
*   **Peak (Picco Centrale):** Attività bassa all'inizio e alla fine, con un picco massimo nelle ore centrali.
    *   *Esempio:* Chi concentra il lavoro intenso prima/dopo la pausa pranzo.
*   **Flat (Costante):** Livello di attività pressoché costante per tutto il turno.
    *   *Esempio:* Lavoro di routine o monitoraggio.

#### 2. Variabilità Individuale (Intensità e Rumore)
Per evitare che i dati siano identici per chi ha lo stesso pattern, vengono applicate due trasformazioni:

*   **Intensity Shift (Quantità):** Viene aggiunto/sottratto un valore casuale (es. $\pm 12$) all'intera curva. Questo simula dipendenti più o meno produttivi (o carichi di lavoro diversi) pur mantenendo la stessa "forma" comportamentale.
*   **Noise (Rumore Gaussiano):** Ad ogni singola ora viene aggiunto un piccolo rumore casuale (distribuzione normale) per simulare le fluttuazioni naturali momento per momento.

#### 3. Attributo Sensibile (Performance_SD)
Al termine della generazione, viene calcolata la somma totale dell'attività per le 8 ore. In base a questo totale, il dipendente viene classificato in una fascia di performance. Questo agisce come **Attributo Sensibile** (o Quasi-Identifier aggiuntivo) nel dataset.

*   **Low:** Totale attività < 160 (Media < 20/ora)
*   **Medium:** 160 $\le$ Totale $\le$ 240
*   **High:** Totale > 240 (Media > 30/ora)

### Struttura del File CSV

Il file generato (`dataset_raw.csv`) contiene 200 record con le seguenti colonne:

| Colonna | Tipo | Descrizione |
| --- | --- | --- |
| **ID** | `int` | Identificativo univoco del dipendente. |
| **Name** | `string` | Nome (casuale). |
| **Surname** | `string` | Cognome (casuale). |
| **H1 ... H8** | `int` | **Serie Temporale**. Intensità dell'attività lavorativa (task completati, effort, ecc.) per ciascuna delle 8 ore del turno. Valori nel range [0-50]. |
| **Performance_SD** | `Category` | Classificazione della produttività complessiva (Low, Medium, High). |

#### Esempio di Record

```csv
ID,Name,Surname,H1,H2,H3,H4,H5,H6,H7,H8,Performance_SD
1,Francesco,Russo,14,22,19,23,35,36,35,44,Medium
3,Alessandro,Verdi,16,27,38,50,47,37,25,14,High
```

*   **Francesco Russo** mostra un trend *Crescente* (da 14 a 44).
*   **Alessandro Verdi** mostra un trend a *Picco* (sale fino a 50 in H4 e poi scende).

### File Correlati

*   **Script Generatore:** [`src/dataset.py`](src/dataset.py)
*   **Dataset CSV:** [`docs/data/dataset_raw.csv`](data/dataset_raw.csv)

## Documentation Structure