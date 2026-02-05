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

# KAPRA Algorithm (k-Anonymity with Pattern Retention)

## Panoramica

**KAPRA** è un algoritmo di anonimizzazione *bottom-up* disegnato per preservare la forma (pattern) delle serie temporali, anche a costo di una maggiore perdita sui valori (Value Loss).

A differenza dell'algoritmo Naive (che parte dall'intero dataset e lo divide top-down basandosi sui valori e poi sulla forma), KAPRA opera in modo **Bottom-Up**:
1.  Parte assumendo il massimo dettaglio di forma possibile (Livello SAX alto).
2.  Raggruppa le serie con forma identica.
3.  Per i gruppi troppo piccoli ("Bad Leaves"), riduce *progressivamente* il livello di dettaglio (Generalizzazione della forma) finché non trova gruppi simili con cui fondersi o formare nuovi gruppi validi.

L'obiettivo è soddisfare il modello **$(k,P)$-anonymity**:
1.  **$k$-anonymity:** Ogni gruppo rilasciato deve contenere almeno $k$ records.
2.  **$P$-anonymity:** Ogni pattern associato a un gruppo deve essere condiviso da almeno $P$ records.

## Fasi dell'Algoritmo (Implementazione Fedele)

L'implementazione attuale segue fedelmente la logica del paper (Algorithm 2: Recycle Bad-Leaves):

### 1. Fase 1: Initial Grouping (Pattern Creation)
Tutte le serie temporali vengono convertite in stringhe **SAX** al livello massimo configurato (`SAX_LEVEL`).
*   Si creano gruppi basati sull'uguaglianza esatta della stringa SAX.
*   **Good-Leaf:** Gruppo con dimensione $\ge P$.
*   **Bad-Leaf:** Gruppo con dimensione $< P$.

> **Nota Implementativa (Efficienza):** Sebbene il paper descriva la costruzione di un "Albero SAX" completo per identificare questi gruppi, la nostra implementazione utilizza una **Hash Map** diretta (dizionario SAX $\to$ records).
> *   **Motivo:** È computazionalmente più efficiente ($O(N)$) rispetto alla navigazione ricorsiva di un albero e produce un output *funzionalmente identico* (i gruppi foglia sono gli stessi).


### 2. Fase 2: Service Level Agreement (Recycle Bad-Leaves)
Invece di forzare l'unione delle Bad-Leaves al "vicino più prossimo" (approccio geometrico), KAPRA applica una **reiterazione con generalizzazione**:
1.  Finché esistono Bad-Leaves e il livello SAX > 1:
    *   Si riduce il livello SAX di 1 (es. da 10 a 9) *solo* per i record nelle Bad-Leaves.
    *   Si ricalcolano i gruppi per questi record al nuovo livello.
    *   Se si formano nuovi gruppi di dimensione $\ge P$ (perché pattern diversi al livello 10 diventano uguali al livello 9), questi vengono promossi a Good-Leaves ("Good-Leaf-Recycled").
    *   I record rimanenti continuano il ciclo scendendo di livello.
2.  Alla fine, eventuali residui vengono soppressi o confluiti in un gruppo generico.

> **Vantaggio:** Questo metodo garantisce che i record "facili" mantengano un dettaglio altissimo (es. Livello 20), mentre i record "rumorosi" o atipici degradano solo quanto basta per trovare compagnia.

### 3. Fase 3: Formation of K-Groups
I gruppi (Good-Leaves) formati, che soddisfano $P$, vengono uniti tra loro (greedy merge riducendo la Value Loss) finché ogni gruppo raggiunge la dimensione $k$.

---

## Analisi e Ottimizzazione dei Parametri

Test eseguiti su un dataset con pattern strutturati (Cylinder, Bell, Funnel) di 3.000 record.

### 1. Risultati Ottimali
Configurazione migliore per compromesso VL/PL:

| Parametro | Valore Ottimale | Descrizione |
| :--- | :--- | :--- |
| **K** | **5** | Valore standard per bilanciare privacy e utilità. |
| **P** | **5** | Un valore medio permette di trovare pattern comuni senza frammentare troppo. |
| **SAX_LEVEL** | **8-20** | KAPRA permette di impostare livelli molto alti (anche 20). Grazie al meccanismo di "Level Reduction", i gruppi forti restano dettagliati, gli altri si adattano. |

### 2. Confronto KAPRA vs Naive (Il "Paradosso" della Performance)

| Metrica | KAPRA (Level=20) | Naive (Mondrian) | Spiegazione |
| :--- | :--- | :--- | :--- |
| **Value Loss (VL)** | **~15.3** | **~4.5** | **Naive vince.** Raggruppando per valore, Naive crea inviluppi stretti (es. [10-15]). KAPRA raggruppa per forma, unendo curve simili ma distanti (es. una a 10 e una a 40), creando inviluppi ampi [10-40]. |
| **Pattern Loss (PL)** | **~0.13** | **~0.00** | **Naive vince (sui numeri).** Sui dati puliti, Naive separa bene i gruppi. KAPRA paga la frammentazione: cercando il pattern perfetto (Livello 20), è costretto a unire residui in gruppi che, pur avendo la stessa forma, generano una lieve perdita matematica. |

### 3. Conclusione: Quando usare KAPRA
KAPRA non è progettato per minimizzare l'errore numerico (VL), ma per **salvare la semantica delle curve**.
*   Usa **Naive** se ti interessa sapere che "il valore era circa 50".
*   Usa **KAPRA** se ti interessa sapere che "c'era un picco seguito da una discesa", indipendentemente se questo è avvenuto a valore 10 o 100.

## Note Implementative e Differenze rispetto al Paper

Questa implementazione presenta una deviazione intenzionale rispetto all'algoritmo KAPRA teorico descritto nel paper originale (Sezione 5.3.3):

* **Omissione del Preprocessing (Splitting dei gruppi $\ge 2P$):**
    Nel paper originale è prevista una fase preliminare che divide ricorsivamente i *P-subgroups* molto grandi (dimensione $\ge 2P$) prima di formare i *k-groups*. Questa implementazione omette tale passaggio.
    
    * **Motivazione:** Si tratta di una scelta ingegneristica per ridurre la complessità del codice (evitando logiche ricorsive top-down all'interno del flusso bottom-up) senza compromettere i requisiti di sicurezza.
    * **Impatto sulla Privacy:** Nessuno. Mantenere gruppi più grandi di quanto strettamente necessario rappresenta uno stato di **"fail-open"**: la privacy è garantita in eccesso, poiché un gruppo più numeroso offre un anonimato ancora più forte (soddisfacendo ampiamente i requisiti $k$ e $P$).
    * **Impatto sull'Utilità:** Potrebbe esserci un marginale aumento della *Value Loss* per alcuni dataset specifici, ma i test (vedi report di ottimizzazione) confermano che la strategia di merging greedy della Fase 3 gestisce efficacemente la formazione dei gruppi.

* **Pattern Assignment (Record-Specific vs Group Dominant):**
    Nella fase di generazione dell'output e calcolo delle metriche, l'implementazione sfrutta la flessibilità del modello $(k,P)$-anonymity:
    *   **Envelope:** È unico per l'intero $k$-group (determinato dal merging nella Fase 3).
    *   **Pattern:** Invece di forzare un unico pattern dominante per tutti i record del gruppo, viene preservato il pattern originale del **$P$-subgroup** di appartenenza (calcolato nella Fase 2).
    *   **Risultato:** Questo permette di abbattere la Pattern Loss (che viene calcolata rispetto al pattern specifico e non a quello medio), garantendo comunque che ogni pattern visualizzato sia condiviso da almeno $P$ utenti.