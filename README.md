# Italian Coronavirus Cases by Age group and Sex (ICCAS)

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

## Python package and notebooks

In [iccas-python][iccas-python], you can find a 
Python package for downloading, processing and visualizing the data. 
It also contains a bunch of Jupyter notebooks with tables and charts that you 
can also run either locally or on Binder [clicking here][launch-binder] or on 
the badge at the top of the page.


## Updates
- **2020/11/30:**
    - published [iccas-python][iccas-python]
    
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
