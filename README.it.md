# Italy Coronavirus Cases by Age group and Sex (ICCAS)

_[Read the full version in English](README.md)_.

Questa repository contiene dataset sul numero di casi confermati di coronavirus 
(Sars-CoV-2) e di morti per/con coronavirus in Italia disaggregati per fascia 
d'età e sesso. I dati sono estratti (automaticamente) dai "bollettini estesi" 
in formato pdf (come [questo](https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_30-marzo-2020.pdf)) 
pubblicati dall'Istituto Superiore di Sanità (ISS) due volte a settimana.
Un link al report più recente può essere trovato in [questa pagina](https://www.epicentro.iss.it/coronavirus/sars-cov-2-sorveglianza-dati)
alla sezione "Documento esteso".
 
La repository contiene anche il codice usato per scaricare i bollettini e per 
generare i dataset (ma sto valutando di spostarlo in una repository separata). 

Sperabilmente, l'ISS o altre istituzioni rilasceranno in futuro dati come questi
(o meglio, più dettagliati) in formato _machine-readable_, rendendo questa 
repository inutile.

## Struttura della cartella `data`
```
data
├── by-date                     
│   └── iccas_{data}.csv   Dataset con dati aggiornati alle 16:00 di giorno {data}
└── iccas_full.csv         Dataset con i dati di tutti i bollettini pubblicati finora
```
`iccas_full.csv` contiene i dati di tutti i dataset nella cartella `by-date` e
ha una colonna aggiuntiva rispetto a questi: `date` (data). 

## Descrizione del dataset
I dataset della cartella `by-date` contengono gli stessi dati che puoi trovare
nella "Tabella 1" dei bollettini dell'ISS. La tabella contiene il numero di casi 
confermati, il numero di morti e altri dati derivati disaggregati per fascia d'età 
(0-9, 10-19, ..., 80-89, >=90) e sesso.

**ATTENZIONE**: il sesso di alcuni pazienti non è noto poiché non è stato 
comunicato per tempo all'ISS, quindi il numero di casi (e di morti) totali è 
maggiore della somma dei dati disaggregati per sesso. In altre parole:
``` 
numero_totale_casi = casi_maschi + casi_femmine + casi_di_sesso_non_noto
numero_totale_morti = maschi_morti + femmine_morte + morti_di_sesso_non_noto
```

Nella seguente tabella, `{sex}` (sesso) può essere `male` (maschio) or `female` 
(femmina). Per esempio, la voce `{sex}_cases` indica che nel dataset ci sono due
colonne: `male_cases` e `female_cases`.

| Column                    | Description                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------|
| `date`                    | **(Presente solo in `iccas_full.csv`)** Data nel formato `AAAA-MM-GG`                        |
| `age_group`               | Fascia d'età: `"0-9", "10-19", ..., "80-89", ">=90"`                                         |
| `cases`                   | Numero di casi confermati (maschi + femmine + sesso non noto / casi attivi + casi chiusi) |
| `deaths`                  | Numero di morti (maschi + femmine + sesso non noto)                                       |
| `{sex}_cases`             | Numero di casi di un certo sesso ({sex})                                                     |
| `{sex}_deaths`            | Numero di morti di un certo sesso ({sex})                                                    |
| `cases_percentage`        | `100 * casi_fascia_di_età / casi_di_tutte_le_età`;                                           |
| `deaths_percentage`       | `100 * morti_fascia_di_età / morti_di_tutte_le_età`;                                         |
| `fatality_rate`           | `100 * morti / casi` (Letalità)                                                              |
| `{sex}_cases_percentage`  | `100 * casi_{sesso} / (casi_maschi + casi_femmine)` (casi di sesso non noto esclusi)      |
| `{sex}_deaths_percentage` | `100 * morti_{sesso} / (morti_maschi + morti_femmine)` (morti di sesso non noto esclusi)  | 
| `{sex}_fatality_rate`     | `100 * morti_{sesso} / casi_{sesso}` (Letalità per i pazienti di un dato sesso)              |

Tutte le colonne da `cases_percentage` in giù sono state ricalcolate.

## Come funziona il codice incluso

Questa sezione è disponibile solo in [inglese](README.md#how-the-code-works).

