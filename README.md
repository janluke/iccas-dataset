# Italy Coronavirus Cases by Age group and Sex (ICCAS)

_[Leggilo in italiano](README.it.md)._

**NOTICE:** since the script used for automating the generation and deployment of 
new datasets stopped working after changes introduced in new pdf reports and 
given that I've not observed much interest in this data (and I lost interest 
myself), **this dataset won't see any update in the future.**

This repository contains datasets about the number of Italian Sars-CoV-2 
confirmed cases and deaths disaggregated by age group and sex. 
The data is (automatically) extracted from pdf reports 
(like [this](https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_30-marzo-2020.pdf)) 
published by _Istituto Superiore di Sanità_ (ISS) two times a week.
A link to the most recent report can be found in [this page](https://www.epicentro.iss.it/coronavirus/sars-cov-2-sorveglianza-dati)
under section "Documento esteso".

PDF reports were published two times a week but, starting from 2020-04-16, they
are published once a week. Each report contains data updated to the 4 p.m. of 
the day day before its release. 

I wrote a script that is runned periodically in order to automatically update 
this repository when a new report is published. 
The code is hosted in a [separate repository](https://github.com/janLuke/iccas-code).


## Data folder structure
The `data` folder is structured as follows:
```
data
├── by-date                    
│   └── iccas_{date}.csv   Dataset with cases/deaths updated to 4 p.m. of {date}
└── iccas_full.csv         Dataset with data from all reports (by date)
```
The full dataset is obtained by concatenating all datasets in `by-date` and has
an additional `date` column. If you use `pandas`, I suggest you to read this
dataset using a multi-index on the first two columns:
```python
import pandas as pd
df = pd.read_csv('iccas_full.csv', index_col=(0, 1))  # ('date', 'age_group')
``` 

**NOTE:** `{date}` is the date the data refers to, NOT the release date of the report 
it was extracted from: as written above, a report is usually released with a day 
of delay. For example, `iccas_2020-03-19.csv` contains data relative to 2020-03-19 
which was extracted from the report published in 2020-03-20.


## Dataset details
Each dataset in the `by-date` folder contains the same data you can find in 
"Table 1" of the corresponding ISS report.
This table contains the number of confirmed cases, deaths and other derived
information disaggregated by age group (0-9, 10-19, ..., 80-89, >=90) and sex.

**WARNING**: the sum of male and female cases is **not** equal to the total 
number of cases, since the sex of some cases is unknown. The same applies to deaths.

Below, `{sex}` can be `male` or `female`.

| Column                    | Description                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------|
| `date`                    | **(Only in `iccas_full.csv`)** Date the format `YYYY-MM-DD`; numbers are updated to 4 p.m of this date |
| `age_group`               | Values: `"0-9", "10-19", ..., "80-89", ">=90"`                                               |
| `cases`                   | Number of confirmed cases (both sexes + unknown-sex; active + closed)                        |
| `deaths`                  | Number of deaths (both sexes + unknown-sex)                                                  |
| `{sex}_cases`             | Number of cases of sex {sex}                                                                 |
| `{sex}_deaths`            | Number of cases of sex {sex} ended up in death                                               |
| `cases_percentage`        | `100 * cases / cases_of_all_ages`                                                            |
| `deaths_percentage`       | `100 * deaths / deaths_of_all_ages`                                                          |
| `fatality_rate`           | `100 * deaths / cases`                                                                       |
| `{sex}_cases_percentage`  | `100 * {sex}_cases / (male_cases + female_cases)` (cases of unknown sex excluded)            |
| `{sex}_deaths_percentage` | `100 * {sex}_deaths / (male_deaths + female_deaths)` (cases of unknown sex excluded)         | 
| `{sex}_fatality_rate`     | `100 * {sex}_deaths / {sex}_cases`                                                           |

All columns that can be computed from absolute counts of cases and deaths (bottom 
half of the table above) were all re-computed to increase precision.
