# Risultati Algoritmo Naive (con Mondrian Clustering)

## Panoramica Approccio
L'algoritmo implementato combina la **K-Anonymity** per gli attributi categorici con una tecnica di clustering **Mondrian (Top-Down Greedy Partitioning)** per le serie temporali.

1.  **Fase 1 (Raggruppamento Ibrido)**:
    *   Identifica i gruppi omogenei per gli attributi categorici (`Dept`, `Seniority`).
    *   All'interno di ogni gruppo categorico, applica ricorsivamente il partizionamento **Mondrian** sulle colonne temporali (`H1`...`H8`).
    *   L'obiettivo è minimizzare la **Value Loss (VL)**, ovvero creare gruppi dove le serie temporali sono il più simili possibile (invarianza euclidea), rispettando il vincolo di cardinalità $k$.
    *   Ogni partizione finale riceve un `GroupID` univoco.

2.  **Fase 2 (Generazione Output)**:
    *   Viene generato un dataset anonimizzato dove ogni serie temporale è sostituita dal suo "envelope" (intervallo min-max) all'interno del gruppo.
    *   I record sono ordinati per `GroupID`.

## Metriche di Performance

Esecuzione su dataset di test (200 record, K=3, P=2):

| Metrica | Valore | Note |
| :--- | :--- | :--- |
| **Tempo di Esecuzione** | ~0.55 sec | Molto rapido, complessità contenuta ($O(N \log N)$ per il sort di Mondrian). |
| **Avg Instant Value Loss (VL)** | **18.08** | Notevolmente ridotta rispetto all'approccio naive puro (~21.7). Indica una maggiore precisione dei dati anonimizzati. |
| **Avg Pattern Loss (PL)** | **0.61** | Bassa distorsione della forma delle serie temporali. |
| **Range Query Error** | **19.01%** | Errore relativo medio su query di intervallo simulate. |

## Struttura Dataset
Il file CSV prodotto (`naive_anonymized.csv`) presenta la seguente struttura:
*   **GroupID**: Identificativo del gruppo di anonimato (K-group).
*   **Dept, Seniority**: Quasi-Identificatori categorici generalizzati.
*   **H1...H8**: Valori delle serie temporali generalizzati come intervalli `[min-max]`.
*   **Performance_SD**: Attributo sensibile (invariato).
*   **Pattern**: Rappresentazione SAX del gruppo (metadato utile per analisi).

## Dataset

- [Raw Dataset](data/remote_work_activity_raw.csv)
- [Anonymized Dataset](data/naive_anonymized.csv)