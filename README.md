# Italian Coronavirus Cases by Age group and Sex (ICCAS)

![Update data](https://github.com/janLuke/iccas-dataset/workflows/Update%20data/badge.svg)

_[Leggilo in italiano (Read it in Italian)](README.it.md)._

This repository contains datasets about the number of Italian Sars-CoV-2 
confirmed cases and deaths disaggregated by age group and sex. 
The data is (automatically) extracted from pdf reports 
(like [this](https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_30-marzo-2020.pdf)) 
published by _Istituto Superiore di Sanità_ (Italian National Institute of Health), 
ISS in short. A link to the most recent report can be found in
[this page](https://www.epicentro.iss.it/coronavirus/sars-cov-2-sorveglianza-dati)
under section "Documento esteso".

Reports were originally published by ISS twice per week; since april, they are 
published only once per week.

This repository is automatically updated by a [GitHub workflow](.github/workflows/update-data.yaml)
that is run regularly (see the workflow file for more details).


## Updates

- **2020/10/07:** 
    - the `date` column now includes the hour (in ISO format, `yyyy-mm-ddThh:mm`).
    - the `date` column was added to all datasets by date; of course, it contains
      a unique duplicated datetime.


## Data folder structure
The `data` folder is structured as follows:
```
data
├── by-date                    
│   └── iccas_{date}.csv   Dataset with cases/deaths updated to a specific {date}
├── util       
│   ├── italian_population_by_age_2020.csv [1]
│   └── italian_population_by_age_group_2020.csv [1]
└── iccas_full.csv         Concatenation of all datasets iccas_{date}.csv
```

[1] Source: [ISTAT](https://www.istat.it/it/popolazione-e-famiglie?dati).

## Dataset details

All numerical values are relative to the first two fields: the date and the age group.

Below, `{sex}` can be `male` or `female`.

| Column                    | Description                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------|
| `date`                    | Italian local time in ISO-8601 format `yyyy-mm-ddThh:mm`                                     |
| `age_group`               | Values: `"0-9", "10-19", ..., "80-89", ">=90", "unknown"`                                    |
| `cases`                   | Number of confirmed cases (including cases of unknown sex) since the start of the pandemic   |
| `deaths`                  | Number of deaths (including cases of unknown sex) since the start of the pandemic            |
| `{sex}_cases`             | Number of `{sex}` cases since the start of the pandemic                                      |
| `{sex}_deaths`            | Number of `{sex}` cases ended up in death since the start of the pandemic                    |
| `cases_percentage`        | `100 * cases_in_age_group / all_cases`                                                       |
| `deaths_percentage`       | `100 * deaths_in_age_group / all_deaths`                                                     |
| `fatality_rate`           | `100 * deaths / cases`                                                                       |
| `{sex}_cases_percentage`  | `100 * {sex}_cases / (male_cases + female_cases)`                                            |
| `{sex}_deaths_percentage` | `100 * {sex}_deaths / (male_deaths + female_deaths)`                                         | 
| `{sex}_fatality_rate`     | `100 * {sex}_deaths / {sex}_cases`                                                           |

### Caveats

- The sum of `male_cases` and `female_cases` is **not** `cases`, since this also
  includes cases of unknown sex.
   
- The sum of `male_deaths` and `female_deaths` is **not** `deaths`, since this 
  also includes deaths of unknown sex.

- In computing `cases_percentage`, the denominator (`all_cases`) includes
  cases of unknown age; if you are interested in estimating the age distribution
  of cases, you should instead ignore cases of unknown age.
  
- The same reasoning of the previous point applies to `deaths_percentage`.
