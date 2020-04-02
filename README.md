# Italy Coronavirus Cases by Age group and Sex (ICCAS)

This repository contains (unofficial) datasets about the number of Italian 
Sars-CoV-2 confirmed cases and deaths disaggregated by age group and sex. 
The data is (automatically) extracted from pdf reports published by 
_Istituto Superiore di Sanità_ (ISS) each 3-4 days.

The code for the download of ISS reports and the generation of datasets is 
included.

Hopefully, ISS or other institutions will finally release more detailed 
machine-readable data making this repository useless. 

## Data folder structure
The `data` folder is structured as follows:
```
data
├── single-date                     
│   └── iccas_only_{date}.csv  Dataset with data from the report of {date}
└── iccas_full.csv             Dataset with data extracted from all reports
```

## Description
For each report, data is extracted from a single table (it has been "Table 1").
The table contains the number of all confirmed cases and deaths disaggregated 
by age group (0-9, 10-19, ..., 80-89, >=90) and sex.

**WARNING**: the sum of male and female cases is **not** equal to the total 
number of cases, since the sex of some cases is unknown.

Columns can be divided into four groups of columns:
- `date` (missing in `iccas_only_{date}.csv` datasets) and `age_group`;
- columns about males, starting with `male_`;
- columns about females, starting with `female_`;
- columns with totals (males + females + **unknown sex**).

Below, `{sex}` can be `male` or `female`. The order is arbitrary.

| Column                  | Description                                                                                  |
|-------------------------|----------------------------------------------------------------------------------------------|
| date                    | **(Only present in `iccas_full.csv`)** Date formatted as YYYY-MM-DD |
| age_group               | Values: `"0-9", "10-19", ..., "80-89", ">=90"`    
| cases                   | Number of confirmed cases (both sexes + unknown-sex; active + closed)                |
| deaths                  | number of deaths (both sexes + unknown-sex)                           |
| {sex}_cases             | number of cases of sex {sex} (relative to the age group)                                     |
| {sex}_deaths            | number of cases of sex {sex} (relative to the age group) ended up in death        |
| cases_percentage        | `100 * cases / cases_of_all_ages`                                                            |
| deaths_percentage       | `100 * deaths / deaths_of_all_ages`                                                          |
| fatality_rate           | `100 * deaths / cases`                                                                       |
| {sex}_cases_percentage  | `100 * {sex}_cases / (male_deaths + female_deaths)` [cases of unknown sex excluded]          |
| {sex}_deaths_percentage | `100 * {sex}_deaths / (male_deaths + female_deaths)` [cases of unknown sex excluded]         | 
| {sex}_fatality_rate     | `100 * {sex}_deaths / {sex}_cases`                                                           |

Columns from `cases_percentage` to the bottom of the table were all recomputed.

## Reading with `pandas`
```python 
import pandas as pd

# Reading a single-date dataset
part = pd.read_csv('iccas_only_2020-03-30.csv', index_col='age_group')   # or index_col=0

# Reading the full dataset
full = pd.read_csv('iccas_full.csv', index_col=('date', 'age_group'))  # or index_col=(0, 1)
```

## About the code

I tried to automate as much as possible, more for the sake of exercising than 
for convenience (however it'll be convenient if ISS reports remain minimally 
consistent over time). 

1. The [ISS news page]() is parsed to obtain the links to all PDF reports 
   (see `download_reports.py`) and if new reports are found they are downloaded 
   into the `reports` folder.
2. For each new report:
    1. the page containing the table is found using a regular expression;
    2. the table is extracted from the page using [tabula-py](https://github.com/chezou/tabula-py) 
       passing the `area` parameter which describe the area of the page containing 
       the data rows of the table; the area was manually selected and tested 
       with the [Tabula app](https://tabula.technology/) and has been stable 
       since 2020/03/19;
    3. computed columns are recomputed;
    4. the dataset files are generated using `pandas`.

I quickly tried to use `PyPDF3` to extract the table as text from the PDF but  
the solution felt hacky/fragile, so in the end I preferred using `tabula-py`.
