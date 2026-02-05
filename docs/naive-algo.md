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

# Naive Algorithm (k,P)-Anonymity

## Panoramica

L'algoritmo Naive è un approccio *top-down* per l'anonimizzazione di serie temporali che mira a soddisfare il modello $(k,P)$-anonymity. L'obiettivo è pubblicare dati che proteggano l'identità (tramite $k$) e garantiscano che ogni pattern pubblicato sia condiviso da almeno $P$ individui.

## Fasi dell'Algoritmo

### 1. Fase 1: Partizionamento Valori (Mondrian)

Vengono raggruppati i record in **k-group** basandosi sui valori delle serie temporali (Value Domain). L'algoritmo Mondrian divide ricorsivamente il dataset cercando di minimizzare l'ampiezza dell'envelope (Instant Value Loss) finché i gruppi non possono più essere divisi senza violare la dimensione minima $k$ (quindi $size \ge k$).

![alt text](imgs/split_example.png)

Una volta creati i gruppi, l'algoritmo valuta la qualità dell'anonimizzazione calcolando la **Value Loss (VL)**. Per ogni gruppo, viene definito un "Envelope" (una fascia che racchiude tutte le serie temporali del gruppo tra un limite minimo e massimo). La VL quantifica l'ampiezza media di questa fascia: più il valore è basso, più le serie nel gruppo sono simili tra loro e minore è la perdita di precisione dei dati.

![alt text](imgs/vl_example.png)

### 2. Fase 2: Raffinamento del Pattern (Naive Node Splitting)

Una volta ottenuti i k-group basati sui valori, l'algoritmo esegue una procedura ricorsiva per suddividere ulteriormente ogni gruppo in P-subgroups, cercando di massimizzare il dettaglio della forma della curva (Pattern SAX).

* **Pre-processing (PAA):** Le serie temporali vengono ridotte a segmenti tramite Piecewise Aggregate Approximation (PAA).
* **Discretizzazione Gerarchica (SAX Level):** L'algoritmo tenta di descrivere le curve con una precisione crescente, aumentando progressivamente il parametro *level* (cardinalità dell'alfabeto SAX).
* **Il Ruolo del MAX_LEVEL:** È imposto un tetto massimo di raffinamento (es. `MAX_LEVEL = 10`). La ricorsione si ferma quando si raggiunge questo limite o quando non è possibile aumentare il livello senza violare il vincolo $P$.
* **Ottimizzazione "In-Place":** Se un gruppo ha dimensioni $P \le Size < 2P$, l'algoritmo prova ad aumentare il livello SAX per l'intero gruppo senza dividerlo, riducendo il Pattern Loss se i record rimangono omogenei.

![alt text](imgs/sax_2.png)

### 3. Fase 3: Post-processing e Gestione delle "Bad Leafs"

Durante la suddivisione ricorsiva, è possibile che vengano generati nodi foglia con meno di $P$ record (*Bad Leafs*).

#### Flusso di Esecuzione
1.  **Raccolta:** Tutte le *bad leafs* vengono rimosse dall'albero e inserite in una coda di priorità.
2.  **Merging:** L'algoritmo unisce ogni *bad leaf* a una "Good Leaf" ($size \ge P$) esistente basandosi sulla **massima similitudine del pattern**.
3.  **Sovrascrittura:** Una volta uniti, i record della *bad leaf* assumono la rappresentazione del pattern (PR) della *good leaf* ospitante.

#### Nota di Implementazione: Ottimizzazione sui Dati Reali
Mentre il paper teorico suggerisce di confrontare la rappresentazione del pattern della Bad Leaf ($PR_{bad}$) con quella della Good Leaf ($PR_{good}$), l'implementazione attuale adotta una strategia più precisa per preservare la qualità dei dati:

* **Metodo Implementato:** Confronta il Feature Vector dei **Dati Reali** della Bad Leaf vs il Feature Vector del **Pattern SAX** della Good Leaf.
* **Motivazione:** Una Bad Leaf contiene spesso pochissimi record (es. 1 solo). Convertire questo singolo record in una stringa SAX introdurrebbe un errore di approssimazione. Utilizzando invece la media dei dati grezzi (Ground Truth), eliminiamo l'errore iniziale di quantizzazione e troviamo il gruppo di destinazione che meglio accoglie la forma *reale* della curva.

---

## Analisi e Ottimizzazione dei Parametri

Sulla base di test estensivi effettuati su un dataset di **3.000 record**, sono state individuate le relazioni chiave tra i parametri per ottenere il miglior trade-off tra privacy e utilità.

### 1. Impatto di K (Dimensione Partizione Iniziale)
Contrariamente all'intuizione classica della k-anonymity, **valori bassi di K (es. $K=5$) offrono prestazioni migliori**.
* **K Basso ($K=5$):** Genera partizioni iniziali molto ampie (es. ~600 record), lasciando alla *Fase 2 (Node Splitting)* la massima libertà di organizzare la gerarchia dei pattern in modo naturale.
* **K Alto ($K=50$):** Frammenta prematuramente i dati in gruppi piccoli, impedendo all'algoritmo di raggruppare serie temporali simili che sono state separate forzatamente nella Fase 1.

### 2. Impatto di MAX_LEVEL e P
Il parametro `MAX_LEVEL` è un limite teorico, ma il vero collo di bottiglia è il vincolo $P$.
* **Con P Basso ($P=2$):** L'algoritmo riesce a scendere in profondità. Aumentare `MAX_LEVEL` fino a 10 porta benefici significativi riducendo l'errore.
* **Con P Alto ($P=8$):** L'algoritmo si ferma presto (spesso a Livello 2 o 3) perché è difficile trovare 8 curve identiche ad alta risoluzione. Qui un `MAX_LEVEL` elevato è superfluo.

### Scenari di Configurazione Consigliati

| Scenario | Configurazione | Risultato Atteso |
| :--- | :--- | :--- |
| **Massima Utility** (Privacy Base) | **$K=5, P=2, \text{Level}=10$** | **VL Minimo (~3.07)**, PL Ottimo. Ideale per analisi dati dettagliate. |
| **Privacy Moderata** | **$K=5, P=8, \text{Level}=3$** | Pattern più generici, ma garanzia di anonimato più forte. Inutile alzare il Level oltre 3. |

---

## Metriche di Performance (Benchmark)

I seguenti risultati fanno riferimento al **Best Trade-off Scenario** ($K=5, P=2, \text{MaxLevel}=10$) sul dataset sintetico di 3.000 record.

| Metrica | Valore | Descrizione e Note Tecniche |
| --- | --- | --- |
| **Tempo di Esecuzione** | **Rapido** | L'algoritmo scala efficientemente grazie alla struttura ad albero. |
| **Avg Instant Value Loss (VL)** | **~3.07** | Errore medio sui valori molto contenuto grazie alla libertà di partizionamento data da $K=5$. |
| **Avg Pattern Loss (PL)** | **~0.35** | Distorsione della forma più elevata rispetto a KAPRA, poiché l'algoritmo ottimizza per valori (VL) ignorando parzialmente la forma. |
| **Range Query Error** | **< 10%** | La precisione nelle query di intervallo rimane alta grazie alla bassa Value Loss. |

### Dettaglio delle Formule Utilizzate

**1. Instant Value Loss (VL)**
Misura la "sfocatura" dei dati causata dalla generalizzazione. Per ogni serie temporale, viene calcolata la radice quadrata della media dei quadrati delle differenze tra i limiti superiori ($U_t$) e inferiori ($L_t$) dell'envelope su tutti i punti temporali $T$:

$$VL = \sqrt{\frac{1}{T} \sum_{t=1}^{T} (U_t - L_t)^2}$$

**2. Pattern Loss (PL)**
Misura quanto la forma della serie ricostruita ($Q'$) differisce dall'originale ($Q$). È calcolata utilizzando la distanza nello spazio delle caratteristiche (Feature Space). Come specificato nel paper, si utilizza la distanza basata sul coseno:

$$PL(Q, Q') = 1 - \text{CosineSimilarity}(FV_Q, FV_{Q'})$$

Dove $FV$ è il vettore delle caratteristiche composto dalle differenze a coppie tra gli attributi.

## Struttura Dataset Output

Il file CSV prodotto (`naive_anonymized.csv`) presenta la seguente struttura:

* **GroupID**: Identificativo numerico del gruppo di anonimato ($k$-group).
* **H1...Hn**: Valori delle serie temporali generalizzati come intervalli stringa `[min-max]`.
* **Performance_SD**: Attributo sensibile (Quasi-Identifier categoriale o Sensibile, lasciato invariato).
* **Pattern**: Rappresentazione SAX finale del gruppo (es. "aabcc...").