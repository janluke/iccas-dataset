# Italy Coronavirus Cases by Age group and Sex (ICCAS)

_[Leggilo in italiano](README.it.md)._

This repository contains datasets about the number of Italian Sars-CoV-2 
confirmed cases and deaths disaggregated by age group and sex. 
The data is (automatically) extracted from pdf reports 
(like [this](https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino-sorveglianza-integrata-COVID-19_30-marzo-2020.pdf)) 
published by _Istituto Superiore di Sanità_ (Italian National Institute of Health), 
ISS in short. A link to the most recent report can be found in
[this page](https://www.epicentro.iss.it/coronavirus/sars-cov-2-sorveglianza-dati)
under section "Documento esteso".

Reports were originally published twice per week; since april, they are 
published only once per week, usually on Friday. There may be exceptions to this
schedule though, e.g. in august one report was skipped.

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
└── iccas_full.csv         Concatenation of all datasets iccas_{date}.csv
```


## Dataset details

Below, `{sex}` can be `male` or `female`.

Of course, all numerical values are relative to the first two fields: the date
and the age group.

| Column                    | Description                                                                                  |
|---------------------------|----------------------------------------------------------------------------------------------|
| `date`                    | Italian local time in ISO-8601 format `yyyy-mm-ddThh:mm`                                     |
| `age_group`               | Values: `"0-9", "10-19", ..., "80-89", ">=90", "unknown"`                                    |
| `cases`                   | Number of confirmed cases (both sexes + unknown-sex; active + closed)                        |
| `deaths`                  | Number of deaths (both sexes + unknown-sex)                                                  |
| `{sex}_cases`             | Number of cases for `{sex}`                                                                  |
| `{sex}_deaths`            | Number of cases ended up in death for `{sex}`                                                |
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


## How datasets are updated 

This repository contains also the Python code used to fetch new reports, extract
the data from them and generate the datasets. The main script is periodically 
run by a GitHub Action [workflow](.github/workflows/update-data.yaml).
At the moment, the workflow doesn't push changes directly into the master branch;
instead, it creates a pull request that I can check. This is just a temporary 
precaution, since the script already performs several sanity checks on the 
extracted data.
