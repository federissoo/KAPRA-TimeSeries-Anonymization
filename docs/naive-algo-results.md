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

# Risultati Algoritmo Naive (con Mondrian Clustering)

## Panoramica Approccio
L'algoritmo implementato utilizza una tecnica di clustering **Mondrian (Top-Down Greedy Partitioning)** per le serie temporali, combinata con un algoritmo **Naive (k,P)-anonymity** basato su SAX.

1.  **Fase 1 (Partizionamento)**:
    *   Applica il partizionamento **Mondrian** sulle colonne temporali (`H1`...`H8`) per creare gruppi preliminari che soddisfano $k$.
    *   L'obiettivo è minimizzare la **Value Loss (VL)** (invarianza euclidea).

2.  **Fase 2 (Raffinamento SAX)**:
    *   Per ogni gruppo, costruisce un albero di raffinamento basato su rappresentazioni SAX.
    *   Parte dal livello SAX 1 ("aaaa") e tenta di aumentare granularità finché il vincolo $P$ è soddisfatto.
    *   Assicura che ogni sottogruppo finale (foglia) condivida lo stesso pattern SAX valido.

## Metriche di Performance

Esecuzione su dataset strutturato (200 record, K=8, P=2):

| Metrica | Valore | Note |
| :--- | :--- | :--- |
| **Tempo di Esecuzione** | Rapido | Complessità contenuta. |
| **Avg Instant Value Loss (VL)** | ~8.4 | Molto bassa grazie ai pattern strutturati. |
| **Avg Pattern Loss (PL)** | ~0.09 | Bassissima distorsione della forma. |
| **Range Query Error** | ~8% | Errore relativo contenuto. |

## Struttura Dataset
Il file CSV prodotto (`naive_anonymized.csv`) presenta la seguente struttura:
*   **GroupID**: Identificativo del gruppo di anonimato.
*   **H1...H8**: Valori delle serie temporali generalizzati come intervalli `[min-max]`.
*   **Performance_SD**: Attributo sensibile (invariato).
*   **Pattern**: Rappresentazione SAX del gruppo (es. "aaaa", "aabc").
*   **Performance_SD**: Attributo sensibile (invariato).
*   **Pattern**: Rappresentazione SAX del gruppo (metadato utile per analisi).

## Dataset

- [Raw Dataset](data/remote_work_activity_raw.csv)
- [Anonymized Dataset](data/naive_anonymized.csv)