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

# Risultati Algoritmo Naive (con Mondrian Clustering)

## Panoramica Approccio

L'algoritmo implementato combina una tecnica di partizionamento **Mondrian (Top-Down Greedy Partitioning)** per i valori, con un algoritmo **Naive (k,P)-anonymity** per la protezione dei pattern.

1. **Fase 1 (Partizionamento Valori)**:
* Applica il partizionamento **Mondrian** sulle colonne temporali (`H1`...`H8`) per creare gruppi preliminari che soddisfano il vincolo dimensionale .
* L'obiettivo è minimizzare la **Instant Value Loss (VL)** riducendo l'ampiezza degli intervalli pubblicati.


2. **Fase 2 (Raffinamento Pattern SAX)**:
* Per ogni gruppo, costruisce un albero di raffinamento basato su rappresentazioni SAX.
* **Pre-processing (PAA):** Le serie temporali (8 ore) vengono ridotte a **4 segmenti** tramite *Piecewise Aggregate Approximation* per mitigare il rumore.
* **Node Splitting:** Parte dal livello SAX 1 ("aaaa") e tenta di aumentare la granularità (dimensione alfabeto) finché il vincolo  è soddisfatto.
* **Fallback:** Se un gruppo non raggiunge la dimensione  per un pattern specifico, viene unificato e riportato al livello del genitore ("aaaa" o livello inferiore), garantendo la *pattern indistinguishability*.



## Metriche di Performance

Esecuzione su dataset strutturato (200 record, ):

| Metrica | Valore | Note |
| --- | --- | --- |
| **Tempo di Esecuzione** | Rapido | < 0.1s (Complessità lineare rispetto al numero di nodi). |
| **Avg Instant Value Loss (VL)** | ~8.42 | Molto bassa grazie alla coerenza dei profili generati. |
| **Avg Pattern Loss (PL)** | ~0.09 | Bassissima distorsione della forma (i pattern 4-lettere sono fedeli). |
| **Range Query Error** | ~8.1% | Errore relativo contenuto sulle query di intervallo. |

## Struttura Dataset

Il file CSV prodotto (`naive_anonymized.csv`) presenta la seguente struttura:

* **GroupID**: Identificativo numerico del gruppo di anonimato (-group).
* **H1...H8**: Valori delle serie temporali generalizzati come intervalli stringa `[min-max]`.
* **Performance_SD**: Attributo sensibile (Quasi-Identifier categoriale o Sensibile, lasciato invariato).
* **Pattern**: Rappresentazione SAX finale del gruppo (es. "aaaa", "aabc", "edca"). Rappresenta la forma media del gruppo su 4 segmenti temporali.

## Dataset Files

* [Raw Dataset](docs/data/dataset_raw.csv)
* [Anonymized Dataset](docs/data/naive_anonymized.csv)
