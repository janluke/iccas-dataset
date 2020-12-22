# Casi Italiani di Coronavirus per fascia d'età e sesso

[iccas-python]: https://github.com/janLuke/iccas-python
[launch-binder]: https://mybinder.org/v2/gh/janLuke/iccas-python/main?filepath=notebooks

[![Badge: health of "Update data" workflow](
    https://github.com/janLuke/iccas-dataset/workflows/Update%20data/badge.svg)](
    https://github.com/janLuke/iccas-dataset/actions)
[![Badge: data updated to](
    https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/janluke/155f87dfa7e7a88887fa1c7da879f7f8/raw/iccas-last-update.json)](
    https://github.com/janLuke/iccas-dataset/tree/master/data)
[![Badge: launch notebooks](
    https://img.shields.io/badge/launch-notebooks-579ACA.svg?logo=data:image/png;base64,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)][launch-binder]

_[Read it in English (Leggilo in Inglese)](README.md)_.

**AVVISO (22/12/2020):** L'ISS ha recentemente iniziato a rilasciare 
[dati giornalieri in formato xlsx](
https://www.epicentro.iss.it/coronavirus/open-data/covid_19-iss.xlsx).
Il workflow che aggiorna questa repository continuerà a essere eseguito ancora 
per qualche mese (o finché non smetterà di funzionare).

***

Questa repository contiene dataset sul numero di casi italiani di Coronavirus 
(e morti per/con Coronavirus) disaggregati per fascia d'età e sesso. 
ICCAS è l'acronimo del nome inglese del dataset (*"Italian Coronavirus Cases by 
Age group and Sex"*).

I dati sono estratti (automaticamente) dai "documenti estesi" in formato pdf 
(come [questo](https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_30-marzo-2020.pdf)) 
pubblicati dall'Istituto Superiore di Sanità (ISS). Un link al report più recente 
può essere trovato a [questa pagina](https://www.epicentro.iss.it/coronavirus/sars-cov-2-sorveglianza-dati)
alla sezione "Documento esteso".

I documenti estesi erano originariamente pubblicati due volte a settimana e sono
adesso pubblicati una volta a settimana.

Questa repository è aggiornata automaticamente da un [workflow di GitHub](.github/workflows/update-data.yaml) 
che viene eseguito regolarmente (si veda il workflow stesso per maggiori dettagli).

## Pacchetto Python e notebook

In [iccas-python](https://github.com/janLuke/iccas-python), ho pubblicato un 
pacchetto Python con funzioni per il download, l'elaborazione e la visualizzazione
dei dati.
La repository contiene anche dei Jupyter notebook con tabelle e grafici che puoi 
eseguire anche su Binder [cliccando qui][launch-binder] o sul badge in 
cima alla pagina.


## Aggiornamenti

- **2020/11/30:**
    - pubblicato [iccas-python][iccas-python]
    
- **2020/10/07:** 
    - la colonna `date` include adesso anche l'ora (formato ISO, `yyyy-mm-ddThh:mm`).
    - la colonna `date` è adesso presente anche nei dataset per data (`by-date`);
      ovviamente, in tali dataset, la colonna `date` contiene un unico valore replicato.


## Struttura della cartella `data`
```
data
├── by-date                     
│   └── iccas_{data}.csv   Dataset con dati aggiornati a giorno {data}
├── util       
│   ├── italian_population_by_age_2020.csv
│   │                      Numero di italiani per età (0, 1, ..., 99, >=100) [1]
│   └── italian_population_by_age_group_2020.csv
│                          Numero di italiani per fascia d'età (0-9, ..., 80-89, >=90) [1]
└── iccas_full.csv         Concatenazione di tutti i dataset iccas_{data}.csv
```

[1] Fonte: [ISTAT](https://www.istat.it/it/popolazione-e-famiglie?dati).


## Descrizione del dataset

Tutti i campi numerici sono relativi ai primi due campi in tabella:
la data e la fascia d'età.

Nella seguente tabella, `{sex}` (sesso) può essere `male` (maschio) o `female` 
(femmina). Per esempio, la voce `{sex}_cases` indica che nel dataset ci sono due
colonne: `male_cases` e `female_cases`.

| Colonna                   | Descrizione                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------|
| `date`                    | Data e ora locale italiana in formato ISO-8601 `yyyy-mm-ddThh:mm`                            |
| `age_group`               | Fascia d'età: `"0-9", "10-19", ..., "80-89", ">=90", "unknown"`                              |
| `cases`                   | Numero di casi confermati (inclusi quelli di sesso non noto) dall'inizio della pandemia      |
| `deaths`                  | Numero di morti (inclusi quelli di sesso non noto) dall'inizio della pandemia                |
| `{sex}_cases`             | Numero di casi di un certo sesso ({sex}) dall'inizio della pandemia                          |
| `{sex}_deaths`            | Numero di morti di un certo sesso ({sex}) dall'inizio della pandemia                         |
| `cases_percentage`        | Il campo `cases` in percentuale: `100 * casi_fascia_età / totale_casi`;                      |
| `deaths_percentage`       | Il campo `deaths` in percentuale`: 100 * morti_fascia_di_età / totale_morti`;                |
| `fatality_rate`           | `100 * morti / casi` (Letalità)                                                              |
| `{sex}_cases_percentage`  | `100 * casi_{sesso} / (casi_maschi + casi_femmine)`                                          |
| `{sex}_deaths_percentage` | `100 * morti_{sesso} / (morti_maschi + morti_femmine)`                                       | 
| `{sex}_fatality_rate`     | `100 * morti_{sesso} / casi_{sesso}` (Letalità per i pazienti di un dato sesso)              |

### Dettagli a cui prestare attenzione

- La somma di `male_cases` e `female_cases` **non** dà `cases`, dato che 
  quest'ultimo valore include anche i casi di sesso non noto.
   
- La somma di `male_deaths` e `female_deaths` **non** dà `deaths`, dato che 
  quest'ultimo valore include anche i morti di sesso non noto.

- Nel calcolo di `cases_percentage`, il denominatore (`totale_casi`) include
  i casi di età non nota; nel caso si fosse interessati a una stima della 
  distribuzione di età dei casi, tecnicamente è meglio non includere i casi di 
  età non nota nel denominatore.
  
- Il ragionamento al punto precedente si applica analogamente a `deaths_percentage`. 
