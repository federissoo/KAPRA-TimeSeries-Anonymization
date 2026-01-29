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

# Naive Algorithm

## Le Due Fasi dell'Algoritmo

Il processo si divide in due macro-fasi distinte:

1. **Fase di partizionamento (Mondrian):** Vengono raggruppati i record in **k-group** basandosi esclusivamente sulle serie temporali. L'algoritmo Mondrian divide ricorsivamente il dataset cercando di minimizzare l'ampiezza dell'envelope (Value Loss) finché i gruppi hanno dimensione almeno $k$.


2. **Fase di raffinamento (Node Splitting):** Per ogni k-group formato, l'algoritmo esegue una procedura ricorsiva per suddividere ulteriormente il gruppo in **P-subgroup**, garantendo che ogni sottogruppo contenga almeno P record con la stessa rappresentazione del pattern (PR).

## Funzionamento della Procedura "create-tree"

Questa è la parte centrale del Naive Algorithm. Per ogni k-group, l'algoritmo cerca di massimizzare il **livello SAX** (la precisione del pattern) rispettando il vincolo P.

### 1. Attributi dei Nodi dell'Albero

Ogni nodo dell'albero rappresenta un insieme di serie temporali e possiede cinque caratteristiche:

* **Level:** Il livello di granularità SAX attuale del nodo.
* **PR:** La rappresentazione simbolica del pattern (stringa SAX) per quel livello.
* **Members:** Le serie temporali contenute nel nodo che condividono la stessa PR.
* **Size:** Il numero di membri.
* **Label:** Un'etichetta che può essere *intermediate*, *good-leaf* (valida) o *bad-leaf* (non valida).

### 2. Processo di Scissione (Node Splitting)

Partendo dalla radice del k-group (inizializzata a livello SAX 1, es. "aaaa"), l'algoritmo decide come dividere i nodi:

* **Se la dimensione è $<P$:** Il nodo diventa una **bad-leaf**.
* **Se il livello ha raggiunto il massimo consentito:** Diventa una **good-leaf**.
* **Se $P \le N.size < 2P$:** Si massimizza il livello SAX finché tutti i record hanno la stessa PR, poi si etichetta come **good-leaf**.
* **Se $N.size \ge 2P$:** Si esegue una **scissione tentativa**. Se l'incremento del livello SAX produce almeno due nodi validi (o un nodo valido e un gruppo di nodi piccoli unificabili), la scissione procede.

### Post-elaborazione delle "Bad-Leaves"

Al termine della ricorsione, i record in nodi troppo piccoli (**bad-leaves**) vengono **ri-inseriti** (fusi) nella "good-leaf" più simile in termini di pattern, adottando il pattern di destinazione.

## Esempio

Prendiamo un esempio semplificato con 5 record ($k=4, P=2$).

| Record | H1 | H2 | **SAX-PR (Level 2)** |
| --- | --- | --- | --- |
| 1 | 10 | 40 | **ab** (Crescente) |
| 2 | 15 | 45 | **ab** (Crescente) |
| 3 | 40 | 10 | **ba** (Decrescente) |
| 4 | 45 | 15 | **ba** (Decrescente) |
| 5 | 12 | 18 | **ac** (Lieve crescita) |

### Fase 1: Mondrian Partitioning

Tutti i 5 record sono simili e finiscono nello stesso **k-group** (dimensione 5 $\ge$ 4).

### Fase 2: Node Splitting

1. **Radice**: $\{1, 2, 3, 4, 5\}$. Livello 1 ("aa").
2. **Scissione a Livello 2**:
    *   Gruppo **ab**: $\{1, 2\}$. Dimensione 2 ($\ge P$). -> **Good-leaf**.
    *   Gruppo **ba**: $\{3, 4\}$. Dimensione 2 ($\ge P$). -> **Good-leaf**.
    *   Gruppo **ac**: $\{5\}$. Dimensione 1 ($< P$). -> **Bad-leaf**.

### Fase 3: Post-processing

Il record 5 ("ac") viene fuso nel gruppo più simile.
Supponiamo sia il gruppo **ab**. Il record 5 viene aggiunto a quel gruppo e "adotta" il pattern **ab**.

### Risultato Finale

| Record | H1 | H2 | **Pattern Finale** |
| --- | --- | --- | --- |
| 1 | [10-15] | [18-45] | **ab** |
| 2 | [10-15] | [18-45] | **ab** |
| 5 | [10-15] | [18-45] | **ab** |
| 3 | [40-45] | [10-15] | **ba** |
| 4 | [40-45] | [10-15] | **ba** |

