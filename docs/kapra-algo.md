<script>
window.MathJax = {
tex: {
inlineMath: [[''], ['\(', '\)']],
displayMath: [['

'], ['

']]
}
};
</script>

<script id="MathJax-script" async
src="[https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js](https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js)">
</script>

# KAPRA Algorithm

## Introduzione
**KAPRA** (k-Anonymity with Pattern Retention Algorithm) è un algoritmo di anonimizzazione progettato specificamente per le serie temporali. A differenza degli approcci tradizionali basati sul partizionamento dei valori (come Mondrian), KAPRA adotta un approccio **bottom-up** guidato dalla forma (pattern) dei dati.

L'obiettivo è soddisfare il modello **$(k,P)$-anonymity**, garantendo che:
1.  Ogni gruppo contenga almeno $k$ individui (privacy dell'identità).
2.  Ogni pattern pubblicato sia condiviso da almeno $P$ individui (privacy del pattern).

## Architettura dell'Algoritmo

L'algoritmo si struttura in tre fasi sequenziali fondamentali.

### Fase 1: Initial Grouping (Creazione dei Pattern)
In questa fase, ogni serie temporale viene convertita in una stringa simbolica **SAX (Symbolic Aggregate approXimation)**.
* Si applica la normalizzazione Z-score.
* Si riduce la dimensionalità (PAA).
* Si discretizza in simboli (es. "abc", "cba").

Le serie con la **stessa identica stringa SAX** vengono raggruppate.
* **Good-Leaf:** Un gruppo con dimensione $\ge P$.
* **Bad-Leaf:** Un gruppo con dimensione $< P$.

### Fase 2: Recycle Bad-Leaves (Il cuore di KAPRA)
Questa è la differenza principale rispetto all'algoritmo Naive. Invece di sopprimere i dati o generalizzare verso l'alto (appiattendo il pattern), KAPRA **ricicla** le Bad-Leaves.

1.  Per ogni **Bad-Leaf**, si cerca la **Good-Leaf più simile** (distanza Euclidea minima tra i profili medi).
2.  I record della Bad-Leaf vengono spostati nella Good-Leaf.
3.  **Adattamento:** I record spostati assumono il pattern della Good-Leaf ospitante.

> **Risultato:** Alla fine di questa fase, esistono solo gruppi con dimensione $\ge P$ e con pattern molto dettagliati (livello SAX alto), minimizzando la perdita di informazione sulla forma.

### Fase 3: Formation of K-Groups
I gruppi formati nella Fase 2 soddisfano il vincolo $P$, ma potrebbero non soddisfare ancora il vincolo $k$.
L'algoritmo unisce i gruppi (P-groups) tra loro per formare i gruppi finali (K-groups):
* Si usa un approccio **Greedy**.
* Si uniscono i gruppi che minimizzano l'aumento della **Instant Value Loss (VL)** (ovvero l'ampiezza dell'intervallo `[min-max]`).

## Confronto Teorico: KAPRA vs Naive

| Caratteristica | Naive (Top-Down) | KAPRA (Bottom-Up) |
| :--- | :--- | :--- |
| **Priorità** | Vicinanza dei Valori | Somiglianza dei Pattern |
| **Gestione Outlier** | Generalizzazione (ritorno alla radice) | Riciclo (spostamento nel gruppo vicino) |
| **Livello SAX** | Basso (spesso 1 o 2) | Alto (massimo dettaglio possibile) |
| **Qualità Intervalli** | Stretti (VL Bassa) | Larghi (VL Alta) |
