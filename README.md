# KAPRA: $(k,P)$-Anonymity for Time Series

Questo progetto implementa l'algoritmo **KAPRA** basato sul paper: 
*"KAPRA: A Strategic Framework for $(k,P)$-Anonymity on Time Series Data"*.

## 🚀 Il Problema: Attacchi Unificati
Il $k$-anonimato tradizionale fallisce sulle serie temporali perché protegge i valori numerici ($K_v$) ma ignora la forma del grafico (**Pattern**, $K_p$). Un hacker può identificare un record usando la conoscenza parziale dell'andamento di un utente.

## 🛠️ La Soluzione: $(k,P)$-Anonymity
KAPRA introduce un doppio livello di protezione:
1. **Requisito-$k$**: Almeno $k$ record condividono lo stesso intervallo di valori (Envelope).
2. **Requisito-$P$**: Almeno $P$ record all'interno di ogni gruppo condividono lo stesso pattern (SAX Representation).

### Metriche di Qualità
L'algoritmo minimizza:
- **Instant Value Loss (VL)**: $VL(Q) = \sqrt{\sum_{i=1}^{n} \frac{(r_i^+ - r_i^-)^2}{n}}$
- **Pattern Loss (PL)**: La distorsione introdotta dalla rappresentazione simbolica SAX.

## 📦 Installazione
```bash
git clone [https://github.com/tuo-username/KAPRA-TimeSeries-Anonymization.git](https://github.com/tuo-username/KAPRA-TimeSeries-Anonymization.git)
pip install -r requirements.txt