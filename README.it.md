# Italy Coronavirus Cases by Age group and Sex (ICCAS)

_[Read the full version in English](README.md)_.

Questa repository contiene dataset sul numero di casi confermati di coronavirus 
(Sars-CoV-2) e di morti per/con coronavirus in Italia disaggregati per fascia 
d'età e sesso. I dati sono estratti (automaticamente) dai "bollettini estesi" 
in formato pdf (come [questo](https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_30-marzo-2020.pdf)) 
pubblicati dall'Istituto Superiore di Sanità (ISS) ogni 3-4 giorni.
Un link al report più recente può essere trovato in [questa pagina](https://www.epicentro.iss.it/coronavirus/sars-cov-2-sorveglianza-dati)
alla sezione "Documento esteso".
 
La repository contiene anche il codice usato per scaricare i bollettini e per 
generare i dataset. 

Sperabilmente, l'ISS o altre istituzioni rilasceranno in futuro dati come questi
(o meglio, più dettagliati) in formato _machine-readable_, rendendo questa 
repository inutile.

## Struttura della cartella `data`
```
data
├── single-date                     
│   └── iccas_only_{data}.csv  Dataset con dati relativi al report pubblicato in data {data}
└── iccas_full.csv             Dataset con dati relativi a tutti i report
```


## Descrizione del dataset
Per ogni report, i dati sono estratti da una singola tabella (che fino ad ora è
stata la "Tabella 1"). La tabella contiene il numero di casi confermati e di 
morti per coronavirus disaggregati per:
- fascia d'età (0-9, 10-19, ..., 80-89, >=90) 
- e sesso

**ATTENZIONE**: il sesso di alcuni pazienti è sconosciuto non essendo stato 
comunicato per tempo all'ISS, quindi il numero di casi (e morti) totali è 
maggiore della somma dei dati disaggregati per sesso. In altre parole:
``` 
numero_totale_casi = casi_maschi + casi_femmine + casi_di_sesso_sconosciuto
```

Nella seguente tabella, `{sex}` (sesso) può essere `male` (maschio) or `female` 
(femmina). Per esempio, la voce `{sex}_cases` indica che nel dataset ci sono due
colonne: `male_cases` e `female_cases`.

| Column                    | Description                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------|
| `date`                    | **(Presente solo in `iccas_full.csv`)** Data nel formato `AAAA-MM-GG`                        |
| `age_group`               | Fascia d'età: `"0-9", "10-19", ..., "80-89", ">=90"`                                         |
| `cases`                   | Numero di casi confermati (maschi + femmine + sesso sconosciuto / casi attivi + casi chiusi) |
| `deaths`                  | Numero di morti (maschi + femmine + sesso sconosciuto)                                       |
| `{sex}_cases`             | Numero di casi di un certo sesso ({sex})                                                     |
| `{sex}_deaths`            | Numero di morti di un certo sesso ({sex})                                                    |
| `cases_percentage`        | `100 * casi_fascia_di_età / casi_di_tutte_le_età`;                                           |
| `deaths_percentage`       | `100 * morti_fascia_di_età / morti_di_tutte_le_età`;                                         |
| `fatality_rate`           | `100 * morti / casi` (Letalità)                                                              |
| `{sex}_cases_percentage`  | `100 * casi_{sesso} / (casi_maschi + casi_femmine)` (casi di sesso sconosciuto esclusi)      |
| `{sex}_deaths_percentage` | `100 * morti_{sesso} / (morti_maschi + morti_femmine)` (morti di sesso sconosciuto esclusi)  | 
| `{sex}_fatality_rate`     | `100 * morti_{sesso} / casi_{sesso}` (Letalità per i pazienti di un dato sesso)              |

Tutte le colonne da `cases_percentage` in giù sono state ricalcolate.

## Leggere i dataset con `pandas`
```python 
import pandas as pd

# Reading a single-date dataset
single = pd.read_csv('iccas_only_2020-03-30.csv', index_col='age_group')   # or index_col=0

# Reading the full dataset
full = pd.read_csv('iccas_full.csv', index_col=('date', 'age_group'))  # or index_col=(0, 1)
```

## Come funziona il codice incluso

Questa sezione è disponibile solo in [inglese](README.md#how-the-code-works).

