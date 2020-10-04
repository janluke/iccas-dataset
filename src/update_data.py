"""
Download new reports and make all datasets, skipping existing ones.
"""
import re
from pathlib import Path
from typing import (
    List,
    Tuple
)

import numpy
import pandas as pd

from common import (
    DATA_DIR,
    REPORTS_DIR,
    REPORTS_DATA_DIR,
    get_dataset_path,
    get_report_data_path,
    cartesian_join
)
from table_extraction import (
    TableExtractor,
    PyPDFTableExtractor,
    COLUMN_PREFIXES
)


def extract_data_from_reports(reports_dir: Path = REPORTS_DIR,
                              output_dir: Path = REPORTS_DATA_DIR,
                              table_extractor: TableExtractor = PyPDFTableExtractor(),
                              skip_existing=True) -> List[Path]:
    """
    Extracts table data from PDF reports saved in `reports_dir` and generates one file per report
    in `output_dir`. If `skip_existing` is `True`, all reports corresponding to existing datasets
    (in `output_dir`) are ignored. 
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    new_dataset_paths = []
    relative_paths = sorted(reports_dir.iterdir())
    for relpath in relative_paths:
        path = reports_dir / relpath
        date = relpath.stem
        out_path = get_report_data_path(date, dirpath=output_dir)
        print('-' * 80)
        if skip_existing and out_path.exists():
            print(f'Dataset for report of {date} already exists')
        else:
            print(f"Making dataset for report of {date} ...")
            table = table_extractor(path)
            table = recompute_derived_columns(table)
            table.to_csv(out_path, index=False)
            new_dataset_paths.append(out_path)
            print('Saved to', out_path)

    print('\nNew datasets written:', new_dataset_paths, end='\n\n')
    return new_dataset_paths


def get_date_from_filename(fname):
    # Note: of course, I could use splits here, but a regex makes this
    # function shorter, more general and so more closed to modifications.
    match = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    if match is None:
        raise ValueError('filename does not contain a date: ' + fname)
    return match.group(1)


def list_datasets_by_date(dirpath: Path) -> List[Tuple[str, Path]]:
    date_path = [(get_date_from_filename(path.name), path)
                 for path in dirpath.iterdir()]
    return sorted(date_path, key=lambda p: p[0])


def make_dataset(input_dir=REPORTS_DATA_DIR,
                 output_dir=DATA_DIR):
    date_path_pairs = list_datasets_by_date(input_dir)
    if not date_path_pairs:
        print('No datasets found in', input_dir)
        return False

    out_path = get_dataset_path(dirpath=output_dir)
    iccas_by_date = {}
    for date, path in date_path_pairs:
        iccas_by_date[date] = pd.read_csv(path, index_col='age_group')

    full = pd.concat(iccas_by_date.values(), axis=0,
                     keys=iccas_by_date.keys(), names=['date', 'age_group'])

    output_dir.mkdir(parents=True, exist_ok=True)
    full.to_csv(out_path)
    print('Full dataset written to', out_path)
    return out_path


def recompute_derived_columns(x: pd.DataFrame) -> pd.DataFrame:
    """ Recomputes all derived columns. This is mostly for sanity checking. """
    derived_cols = list(cartesian_join(
        COLUMN_PREFIXES, ['cases_percentage', 'deaths_percentage', 'fatality_rate']))
    y = x.drop(columns=derived_cols)  # to avoid SettingWithCopy warning

    total_cases = x['cases'].sum()
    total_deaths = x['deaths'].sum()
    y['cases_percentage'] = x['cases'] / total_cases * 100
    y['deaths_percentage'] = x['deaths'] / total_deaths * 100
    y['fatality_rate'] = x['deaths'] / x['cases'] * 100

    # REMEMBER: male_cases + female_cases != total_cases,
    # because total_cases also includes cases of unknown sex
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


def get_latest_dataset_date(default: str = '') -> str:
    dataset_list = list_datasets_by_date(REPORTS_DATA_DIR)
    return dataset_list[-1][0] if dataset_list else default


if __name__ == '__main__':
    from download_reports import download_missing_reports

    download_missing_reports(after=get_latest_dataset_date())
    new_report_datasets = extract_data_from_reports(skip_existing=True)
    if new_report_datasets:
        make_dataset()
