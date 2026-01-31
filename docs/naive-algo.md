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

# Naive Algorithm (k,P)-Anonymity

## Panoramica

L'algoritmo Naive è un approccio *top-down* per l'anonimizzazione di serie temporali che mira a soddisfare il modello -anonymity. L'obiettivo è pubblicare dati che proteggano l'identità (tramite ) e garantiscano che ogni pattern pubblicato sia condiviso da almeno  individui.

## Le Due Fasi dell'Algoritmo

Il processo si divide in due macro-fasi sequenziali:

1. **Fase 1: Partizionamento (Mondrian)**
Vengono raggruppati i record in **k-group** basandosi sui valori delle serie temporali (Value Domain). L'algoritmo Mondrian divide ricorsivamente il dataset cercando di minimizzare l'ampiezza dell'envelope (Instant Value Loss) finché i gruppi non possono più essere divisi senza violare la dimensione minima  (quindi ).
![alt text](split_example.png)

2. Una volta creati i gruppi, l'algoritmo valuta la qualità dell'anonimizzazione calcolando la Value Loss (VL). Per ogni gruppo, viene definito un "Envelope" (una fascia che racchiude tutte le serie temporali del gruppo tra un limite minimo e massimo). La VL quantifica l'ampiezza media di questa fascia: più il valore è basso, più le serie nel gruppo sono simili tra loro e minore è la perdita di precisione dei dati.
![alt text](vl_example.png)

2. **Fase 2: Raffinamento del Pattern (Naive Node Splitting)**
Per ogni *k-group* formato, l'algoritmo esegue una procedura ricorsiva per suddividere ulteriormente il gruppo in **P-subgroup**, cercando di massimizzare il dettaglio del pattern (Livello SAX).

---

## Funzionamento della Procedura "create-tree"

Questa procedura costruisce un albero di pattern per ogni k-group. La radice rappresenta l'intero gruppo al livello di granularità più basso (Livello 1, pattern piatto).

### 1. Attributi dei Nodi

Ogni nodo  dell'albero possiede le seguenti caratteristiche:

* **Level:** Il livello SAX corrente (lunghezza dell'alfabeto).
* **PR (Pattern Representation):** La stringa SAX che descrive il nodo a quel livello.
* **Members:** L'insieme delle serie temporali nel nodo.
* **Size:** Numero di membri ().
* **Status:** Può essere *Good-Leaf* (nodo definitivo) o nodo intermedio.

### 2. Logica di Scissione (Node Splitting)

L'algoritmo tenta ricorsivamente di aumentare il **Level** (da  a ) per ottenere pattern più precisi.

1. **Calcolo dei Pattern:** Si calcolano le stringhe SAX al livello  per tutti i membri del nodo.
2. **Raggruppamento:** I membri vengono divisi in sottogruppi basati sulla *Strict Equality* (uguaglianza esatta) del pattern.
3. **Classificazione dei Figli:**
* **Large Children ():** Sono gruppi validi. Diventano nuovi nodi su cui continuare la ricorsione.
* **Small Children / TB-Nodes ():** Sono gruppi non validi ("To-Be-merged").


4. **Gestione dei Nodi Piccoli (Child Merge):**
A differenza di KAPRA, il Naive **non** sposta i nodi piccoli verso altri gruppi.
* Si calcola la somma delle dimensioni di tutti i *Small Children*.
* Se la somma è , questi vengono **uniti** (merged) in un unico nodo.
* **Importante:** Il nodo unito **regredisce al livello del genitore** (), poiché i membri non condividono un pattern comune al livello .
* Questo nodo diventa una *Good-Leaf* (non viene splittato ulteriormente).



### 3. Caso di Fallimento

Se, dopo il tentativo di split e merge, rimangono record (TB-nodes residui) la cui somma è inferiore a , lo split viene considerato fallito per l'intero ramo o parzialmente annullato, e il nodo genitore diventa una foglia al livello inferiore ().

---

## Esempio Pratico

Consideriamo un k-group con 5 record ().
**Configurazione:** PAA a 4 segmenti.

| Record | Serie Reale (H1..H4) | Pattern Livello 2 (a,b) | Pattern Livello 1 (a) |
| --- | --- | --- | --- |
| **R1** | Salita netta | `aabb` | `aaaa` |
| **R2** | Salita netta | `aabb` | `aaaa` |
| **R3** | Discesa | `bbaa` | `aaaa` |
| **R4** | Costante | `abab` (rumore) | `aaaa` |
| **R5** | Costante | `abab` (rumore) | `aaaa` |

### Esecuzione Passo-Passo

1. **Inizio:** Nodo Radice contenente . Livello 1. Pattern: `aaaa`.
2. **Tentativo Split a Livello 2:**
* Gruppo 1 (`aabb`): . Dimensione 2. ()  **Valido**.
* Gruppo 2 (`bbaa`): . Dimensione 1. ()  **Small Child**.
* Gruppo 3 (`abab`): . Dimensione 2. ()  **Valido**.


3. **Gestione Small Child ({R3}):**
* Il gruppo  è solo. Non ci sono altri *Small Children* con cui unirsi per raggiungere .
* **Azione Naive:** Lo split non può lasciare orfani.
* *Conseguenza:* Poiché non è possibile soddisfare la condizione  per R3 al Livello 2, l'algoritmo è costretto ad annullare il miglioramento per l'intero gruppo (o a mantenere R3 e gli altri unificati al livello precedente).
* **Risultato:** Tutti tornano a `aaaa`.



### Confronto Risultato Finale (Naive vs Ideale)

In questo caso, a causa di R3 (outlier), l'algoritmo Naive produrrà probabilmente:

| Record | Pattern Pubblicato | Note |
| --- | --- | --- |
| 1, 2, 3, 4, 5 | **aaaa** | Alta Pattern Loss (Informazione persa globalmente a causa di un solo outlier) |