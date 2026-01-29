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

# Report Esperimento: Confronto Naive vs KAPRA

## Configurazione dell'Esperimento

L'esperimento è stato condotto su un dataset sintetico di 200 profili di attività lavorativa (8 ore, `H1`...`H8`), generati con pattern strutturati (es. rising, falling, peak) e rumore gaussiano.

**Parametri di Anonimizzazione:**
* **K (Privacy Group Size):** 8
* **P (Pattern Group Size):** 2
* **PAA Segments:** 4 (Riduzione da 8 ore a 4 segmenti per mitigare il rumore)
* **SAX Level (Naive):** Variabile (limitato dal fallback).
* **SAX Level (KAPRA):** 8 (Massimo dettaglio).

## Risultati Quantitativi

| Metrica | Algoritmo Naive | Algoritmo KAPRA | Interpretazione |
| :--- | :--- | :--- | :--- |
| **Tempo Esecuzione** | ~0.08s | ~0.07s | Entrambi molto efficienti. |
| **Avg Value Loss (VL)** | **8.42** | 16.00 | Naive crea intervalli più stretti (migliore per query sui valori). |
| **Avg Pattern Loss (PL)**| 0.09* | **0.35** | *Vedi Analisi Qualitativa sotto. |
| **Pattern Complexity** | Bassa ("aaaa") | **Alta ("cedf")** | KAPRA preserva la forma reale. |

## Analisi Qualitativa (Il "Paradosso" delle Metriche)

### 1. Il caso della Pattern Loss (PL)
Numericamente, il Naive sembra avere una PL migliore (0.09 vs 0.35). Tuttavia, questa è una **metrica ingannevole** in questo contesto.
* **Naive:** Quando non trova corrispondenze esatte, il Naive appiattisce il pattern a livello 1 (**"aaaa"**). Matematicamente, una linea piatta ha una distanza media bassa da curve rumorose, ma **sematicamente l'informazione è nulla**. Il pattern è andato perso.
* **KAPRA:** Mantiene pattern complessi a livello 8 (es. **"cedf"**, **"gcdc"**). La PL è matematicamente più alta perché cerca di adattare curve complesse a dati reali, ma l'informazione sulla forma (picchi e valli) è preservata perfettamente.

### 2. Il Trade-off Value Loss vs Pattern
I risultati confermano la teoria del paper $(k,P)$-anonymity:
* **Naive (Mondrian-First):** Raggruppa per valori simili. Ottimo per sapere *quanto* un impiegato ha lavorato (intervallo stretto), pessimo per sapere *quando*.
* **KAPRA (Pattern-First):** Raggruppa per forme simili. Un impiegato che lavora poco (10h) e uno che lavora tanto (40h) finiscono insieme se hanno lo stesso profilo orario. Questo allarga l'intervallo (VL sale a 16.00), ma mantiene intatta la dinamica temporale.

## Esempio Reale dai Dati

**Output Naive (Gruppo X):**
> Pattern: `aaaa`
> Intervalli: `[12-19], [12-19], ...`
> *Analisi:* Sappiamo che i valori sono bassi, ma non sappiamo se salgono o scendono.

**Output KAPRA (Gruppo Y):**
> Pattern: `hfbb` (Alto inizio, discesa rapida, basso fine)
> Intervalli: `[37-46], [30-41], ... [0-17]`
> *Analisi:* Identifichiamo chiaramente un profilo "Early Bird" (chi lavora molto al mattino). L'intervallo è più ampio, ma il comportamento è evidente.

## Conclusione
L'esperimento dimostra che **KAPRA è superiore** per applicazioni di Data Mining dove la forma della serie temporale (trend, periodicità) è più importante del valore puntuale assoluto. Il Naive è preferibile solo per query statistiche aggregate (es. somma totale ore).