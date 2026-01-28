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

1. **Fase di K-anonimato convenzionale:** Vengono raggruppati i record in **k-group**. In questa fase, ogni record viene reso indistinguibile da almeno altri k-1 record basandosi sui valori dei QI.


2. **Fase create-tree (creazione dell'albero):** Per ogni k-group formato nella prima fase, l'algoritmo esegue una procedura ricorsiva per suddividere ulteriormente il gruppo in **P-subgroup**, garantendo che ogni sottogruppo contenga almeno P record con la stessa rappresentazione del pattern (PR) .

## Funzionamento della Procedura create-tree

Questa è la parte centrale del Naive Algorithm. Per ogni k-group, l'algoritmo cerca di massimizzare il **livello SAX** (la precisione del pattern) rispettando il vincolo P.

### 1. Attributi dei Nodi dell'Albero

Ogni nodo  dell'albero rappresenta un insieme di serie temporali e possiede cinque caratteristiche :

* **Level:** Il livello di granularità SAX attuale del nodo.
* **PR:** La rappresentazione simbolica del pattern (stringa SAX) per quel livello.
* **Members:** Le serie temporali contenute nel nodo che condividono la stessa PR.
* **Size:** Il numero di membri.
* **Label:** Un'etichetta che può essere *intermediate* (nodo interno), *good-leaf* (foglia valida con dimensione $\ge P$) o *bad-leaf* (foglia non valida con dimensione $< P$).

### 2. Processo di Scissione (Node Splitting)

Partendo dalla radice del k-group (livello 1), l'algoritmo decide come dividere i nodi in base alla loro dimensione ($P$):

* **Se la dimensione è $<P$:** Il nodo diventa una **bad-leaf** e la ricorsione si ferma.


* **Se il livello ha raggiunto il massimo consentito:** Diventa una **good-leaf**.


* **Se $P \le N.size < 2P$:** Si massimizza il livello SAX finché tutti i record hanno la stessa PR, poi si etichetta come **good-leaf**. Non si divide ulteriormente per evitare di creare "bad-leaves" .


* **Se $N.size \ge 2P$:** Si esegue una **scissione tentativa**. Se l'incremento del livello SAX produce almeno due nodi validi (o un nodo valido e un gruppo di nodi piccoli che, se uniti, raggiungono la dimensione ), la scissione diventa reale .


### Post-elaborazione delle "Bad-Leaves"

Al termine della ricorsione, potrebbero esserci dei record rimasti in nodi troppo piccoli (**bad-leaves**) per soddisfare il requisito .

* Tutti i nodi etichettati come "bad-leaf" vengono rimossi dall'albero.


* I record contenuti in questi nodi vengono **ri-inseriti** (fusi) nella "good-leaf" più simile in termini di pattern.


* Il nuovo nodo risultante manterrà la rappresentazione del pattern (PR) della "good-leaf" originale per garantire che il requisito di anonimato non venga violato.


## Esempio

Per rendere l'esempio concreto, prendiamo un pezzo di esempio simile al nostro dataset (5 record). Questo ci permetterà di applicare l'algoritmo **Naive** con parametri $k=4$ e $P=2$.

| Record | Dept | Seniority | H1 | H2 | **SAX-PR** |
| --- | --- | --- | --- | --- | --- |
| 1 | HR | Junior | 10 | 40 | **ab** (Crescente) |
| 2 | HR | Junior | 15 | 45 | **ab** (Crescente) |
| 3 | HR | Junior | 40 | 10 | **ba** (Decrescente) |
| 4 | HR | Junior | 45 | 15 | **ba** (Decrescente) |
| 5 | HR | Junior | 12 | 18 | **ac** (Lieve crescita) |

### Fase 1: K-anon

L'algoritmo esegue prima un clustering convenzionale sui QI (Dept, Seniority, H1, H2) per formare dei **k-group** .
Poiché  e abbiamo 5 record simili, vengono tutti inseriti nello stesso **k-group**.
* Dept: HR, Seniority: Junior
* H1: [10, 45] H2: [10, 45] .

### Fase 2: Create-tree

Per il k-group, l'algoritmo costruisce un albero ricorsivo per soddisfare il requisito $P=2$.

1. **Nodo 1 (Radice)**: Contiene i record $\{1, 2, 3, 4, 5\}$. Livello SAX = 1 (pattern molto generico).
2. **Scissione Tentativa (Livello 2)**: L'algoritmo aumenta la precisione del pattern (Livello 2) e divide i record in base alla loro PR:


* **Sotto-nodo A**: Record $\{1, 2\}$ con PR "**ab**". Dimensione = 2 ($\ge P$). Etichetta: *good-leaf*.


* **Sotto-nodo B**: Record $\{3, 4\}$ con PR "**ba**". Dimensione = 2 ($\ge P$). Etichetta: *good-leaf*.


* **Sotto-nodo C**: Record $\{5\}$ con PR "**ac**". Dimensione = 1 ($< P$). Etichetta: **bad-leaf**.





#### Fase 3: Post-processing (Gestione delle Bad-leaves)

Il record 5 è in un nodo troppo piccolo (dimensione $< P$).

* Il nodo "bad-leaf" viene rimosso e il suo record (5) viene **ri-inserito** nel nodo "good-leaf" con il pattern più simile .


* Supponiamo che "**ac**" sia più simile ad "**ab**" (Crescente) che a "**ba**" (Decrescente).
* Il record 5 viene fuso nel Sotto-nodo A e **adotta forzatamente** la PR "**ab**".



---

### 3. Risultato Finale: (4, 2)-Anonymity Status

| Record | Dept | Seniority | H1 | H2 | **SAX-PR** |
| --- | --- | --- | --- | --- | --- |
| 1 | HR | Junior | [10, 45] | [10, 45] | **ab** (Crescente)|
| 2 | HR | Junior | [10, 45] | [10, 45] | **ab** (Crescente)|
| 5 | HR | Junior | [10, 45] | [10, 45] | **ab** (Crescente)|
| 3 | HR | Junior | [10, 45] | [10, 45] | **ba** (Decrescente)|
| 4 | HR | Junior | [10, 45] | [10, 45] | **ba** (Decrescente)|

