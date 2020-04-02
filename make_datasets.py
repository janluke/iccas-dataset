"""
Download new reports and make all datasets, skipping existing ones.
"""
import json
import math
import re
from bisect import bisect
from pathlib import Path
from typing import List, Optional, Tuple

import numpy
import pandas as pd
import tabula

from settings import (
    FULL_DATASET_DIR,
    ISS_REPORTS_DIR,
    SINGLE_DATE_DATA_DIR,
    TABULA_TEMPLATES_DIR,
    get_date_from_filename,
    get_full_dataset_path,
    get_single_date_dataset_path
)

# Used to find the table page automatically
TABLE_CAPTION_PATTERN = re.compile(
    'TABELLA .+ DISTRIBUZIONE DEI CASI DIAGNOSTICATI .+ PER FASCIA DI ET. E SESSO',
    re.IGNORECASE)


def load_tabula_templates(dirpath=TABULA_TEMPLATES_DIR):
    """
    Returns a dictionary of tabula templates by date of first validity.

    Tabula templates are JSON files used to describe the location of the table
    inside a pdf report, i.e. the page and the selection area inside the page.
    This script ignores the page, since it is automatically detected and make
    use only of the selection area.

    Tabula templates are generated with the Tabula app and saved in a subfolder
    of the project with name "{date}.tabula-template.json" where {date} is the
    date of first validity of the template.
    """
    by_date = {}
    for relpath in dirpath.iterdir():
        date = relpath.name.split('.', 1)[0]
        with open(Path(dirpath, relpath)) as f:
            by_date[date] = json.load(f)[0]
    return by_date


def _tabula_template_getter(template_dir=TABULA_TEMPLATES_DIR):
    TEMPLATE_BY_DATE = load_tabula_templates(template_dir)
    DATES = sorted(TEMPLATE_BY_DATE.keys())   # dates of first validity of the templates

    def get_tabula_template(report_date):
        """ Returns the tabula template to use given the report date """
        i = bisect(DATES, report_date)  # index of 1st date >= report_date
        template_date = DATES[i - 1]
        return TEMPLATE_BY_DATE[template_date]

    return get_tabula_template


get_tabula_template_for = _tabula_template_getter()


def area_from_template(template):
    return template['y1'], template['x1'], template['y2'], template['x2']


def to_int(s):
    if not s: return math.nan
    return int(s.replace('.', '').replace(' ', ''))


def to_float(s):  # can't rely on pandas since ISS number notation is inconsistent
    if not s: return math.nan
    return float(s.replace(',', '.'))


def cartesian_join(*string_iterables, sep=''):
    from itertools import product
    return (sep.join(iterable) for iterable in product(*string_iterables))


# PDF table columns
INPUT_COLUMN_GROUPS = ('male_', 'female_', '')
INPUT_COLUMN_FIELDS = ('cases', 'cases_percentage', 'deaths', 'deaths_percentage', 'fatality_rate')
INPUT_COLUMNS = ('age_group', *cartesian_join(INPUT_COLUMN_GROUPS, INPUT_COLUMN_FIELDS))
INPUT_COLUMN_CONVERTERS = dict(zip(INPUT_COLUMNS,
    [str] + 3 * [to_int, to_float, to_int, to_float, to_float]))  # noqa


def find_table_page(pdf_path) -> Optional[int]:
    """ Return the index (1-based) of the page containing the data table. """
    import PyPDF3

    pdf = PyPDF3.PdfFileReader(str(pdf_path))
    num_pages = pdf.getNumPages()

    for i in range(1, num_pages):
        page = pdf.getPage(i)
        text = ''.join(page.extractText().split('\n'))
        if TABLE_CAPTION_PATTERN.search(text):
            return i + 1
    return None


def recompute_derived_columns(x: pd.DataFrame) -> pd.DataFrame:
    """ Recompute all derived columns """
    derived_cols = list(cartesian_join(
        INPUT_COLUMN_GROUPS, ['cases_percentage', 'deaths_percentage', 'fatality_rate']))
    y = x.drop(columns=derived_cols)  # to avoid SettingWithCopy warning

    total_cases = x['cases'].sum()
    total_deaths = x['deaths'].sum()
    y['cases_percentage'] = x['cases'] / total_cases * 100
    y['deaths_percentage'] = x['deaths'] / total_deaths * 100
    y['fatality_rate'] = x['deaths'] / x['cases'] * 100

    # REMEMBER: male_cases + female_cases don't add up to (total) cases
    for what in ['cases', 'deaths']:
        total = x[f'male_{what}'] + x[f'female_{what}']
        denominator = total.replace(0, 1)  # avoid division by 0
        for sex in ['male', 'female']:
            y[f'{sex}_{what}_percentage'] = x[f'{sex}_{what}'] / denominator * 100

    for sex in ['male', 'female']:
        y[f'{sex}_fatality_rate'] = x[f'{sex}_deaths'] / x[f'{sex}_cases'] * 100

    # sanity check
    for col in derived_cols:
        assert numpy.allclose(y[col], x[col], atol=0.1), \
            '\n' + str(pd.DataFrame({'recomputed': y[col], 'original': x[col]}))

    return y[x.columns]


class TableExtractionError(Exception):
    pass


def extract_table(pdf_path, area, page=None, recompute_derived_cols=True) -> pd.DataFrame:
    """ Returns the table in a pd.DataFrame """
    if page is None:
        page = find_table_page(pdf_path)
        if page is None:
            raise TableExtractionError("couldn't find the table anywhere in the pdf")

    tables = tabula.read_pdf(
        str(pdf_path), pages=page, area=area, multiple_tables=False,
        pandas_options={'names': INPUT_COLUMNS, 'converters': INPUT_COLUMN_CONVERTERS})
    if not tables:
        raise TableExtractionError('tabula.read_pdf did not return anything')

    df = tables[0]

    # Sanity checks
    if len(df) != 12:
        raise TableExtractionError('unexpected table length: %s' % list(df.age_group))

    # Replace '≥90' with ascii equivalent '>=90'
    df.at[9, 'age_group'] = '>=90'
    # Replace 'non nota' with english translation
    df.at[10, 'age_group'] = 'unknown'

    # Extract row containing totals
    total = df.iloc[11]
    df = df.iloc[:11].copy()

    # Sanity checks
    for col in ['cases', 'male_cases', 'female_cases']:
        actual_sum = df[col].sum()
        if actual_sum != total[col]:
            raise TableExtractionError(
                f'column "{col}" sum() is inconsistent with the value reported'
                f'in the last row of the table: {actual_sum} != {total[col]}')

    if recompute_derived_cols:
        df = recompute_derived_columns(df)

    return df


def make_single_date_datasets(reports_dir: Path = ISS_REPORTS_DIR,
                              data_dir: Path = SINGLE_DATE_DATA_DIR,
                              skip_existing=True) -> int:
    data_dir.mkdir(parents=True, exist_ok=True)
    new_dataset_count = 0
    errors = []
    relative_paths = sorted(reports_dir.iterdir())
    for relpath in relative_paths:
        path = reports_dir / relpath
        date = relpath.stem
        out_path = get_single_date_dataset_path(date, dirpath=data_dir)
        if skip_existing and out_path.exists():
            print(f'Dataset for report of {date} already exists')
        else:
            print(f"Making dataset for report of {date} ...")
            template = get_tabula_template_for(date)
            table_area = area_from_template(template)
            try:
                df = extract_table(path, table_area)
                df.to_csv(out_path, index=False)
                new_dataset_count += 1
                print('Dataset saved to', out_path)
            except TableExtractionError as exc:
                print('ERROR:', exc)
                errors.append((date, exc))
            print('-' * 80)

    print('\nRecap:')
    print('* new datasets written:', new_dataset_count)
    if errors:
        print('* errors (%d):' % len(errors))
        for date, exc in errors:
            print(f'  - report {date}:', exc)
    print('')

    return new_dataset_count


def list_datasets_by_date(dirpath: Path) -> List[Tuple[str, Path]]:
    date_path = [(get_date_from_filename(path.name), path)
                 for path in dirpath.iterdir()]
    return sorted(date_path, key=lambda p: p[0])


def make_full_dataset(input_dir=SINGLE_DATE_DATA_DIR,
                      output_dir=FULL_DATASET_DIR):
    date_path_pairs = list_datasets_by_date(input_dir)
    if not date_path_pairs:
        print('No datasets found in', input_dir)
        return False

    out_path = get_full_dataset_path(dirpath=output_dir)
    iccas_by_date = {}
    for date, path in date_path_pairs:
        iccas_by_date[date] = pd.read_csv(path, index_col='age_group')

    full = pd.concat(iccas_by_date.values(), axis=0,
        keys=iccas_by_date.keys(), names=['date', 'age_group'])

    output_dir.mkdir(parents=True, exist_ok=True)
    full.to_csv(out_path)
    print('Full dataset written to', out_path)


if __name__ == '__main__':
    from download_reports import download_missing_reports

    download_missing_reports()
    make_single_date_datasets()
    make_full_dataset()
