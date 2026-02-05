# Report Ottimizzazione Parametri Naive (k,P)-Anonymity

## Esecuzione
Il test è stato eseguito su un dataset di **3000 record** generati sinteticamente.
Sono state testate le seguenti combinazioni:
*   **K (Initial Partition Groups)**: [5, 10, 20, 50]
*   **P (Privacy Constraint)**: [2, 3, 5, 8]
*   **MAX_LEVEL (SAX Alphabet Size)**: [3, 5, 8, 10, 15, 20]

## Risultati Chiave

### 1. Impatto di MAX_LEVEL e P
Il parametro `MAX_LEVEL` agisce come un "tetto massimo" alla precisione, ma il fattore limitante reale è spesso **P**.

*   **Con P basso (es. P=2)**: L'algoritmo riesce a scendere molto in profondità nall'albero. Aumentare `MAX_LEVEL` da 3 a 10 porta benefici significativi in termini di **Value Loss (VL)** (riduzione errore). Oltre il livello 10, i benefici si appiattiscono (diminishing returns).
*   **Con P alto (es. P=8)**: L'algoritmo si ferma molto presto (spesso a Livello 2) perché non riesce a trovare sottogruppi di dimensione $\ge 8$ che condividano lo stesso pattern più dettagliato. Di conseguenza, aumentare `MAX_LEVEL` oltre 3 è totalmente ininfluente.

### 2. Impatto di K
Sorprendentemente, valori più bassi di **K** (es. 5) hanno prodotto risultati migliori in termini di Value Loss rispetto a K alti (50).
*   **K=5**: Permette di avere gruppi iniziali molto grandi (~600 record), lasciando alla Phase 2 (Naïve Node Splitting) la libertà di trovare la struttura ottimale gerarchica.
*   **K=50**: Frammenta i dati in gruppi piccoli (~60 record) fin dall'inizio, limitando la capacità dell'algoritmo di raggruppare record simili che sono finiti in partizioni diverse.

## Configurazione Ottimale (Best Trade-off)

La configurazione vincente dipende dal livello di privacy richiesto.

### Scenario A: Massima Utility (Privacy base P=2)
La miglior combinazione per avere l'errore minimo:
*   **K**: 5
*   **P**: 2
*   **MAX_LEVEL**: 10 (o 8)
*   *Risultato*: VL ~3.07, PL ~0.06

### Scenario B: Privacy Moderata (P=8)
Se è richiesto P=8, aumentare MAX_LEVEL è inutile.
*   **K**: 5
*   **P**: 8
*   **MAX_LEVEL**: 3 (qualsiasi valore >2 dà lo stesso risultato)
*   *Risultato*: VL ~8.19, PL ~0.0 (pattern troppo generici)

## Grafico Sintetico (Esempio K=5)

| P | MAX_LEVEL | VL (Errore Valori) | PL (Errore Pattern) | Note |
|---|---|---|---|---|
| **2** | 3 | 4.96 | 0.068 | Buono |
| **2** | **10** | **3.07** | **0.060** | **Ottimo** |
| **2** | 20 | 3.07 | 0.059 | Saturo (nessun guadagno extra) |
| **8** | 3 | 8.19 | 0.00* | Pattern generici (livello 2) |
| **8** | 20 | 8.19 | 0.00* | Limitato da P, non raggiunge livelli alti |

*\*PL=0 indica che l'albero si è fermato a livelli < 3 dove la metrica PL non è calcolata (pattern troppo base).*
