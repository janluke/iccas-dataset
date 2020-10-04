import abc
import math
import re
from typing import Tuple

import PyPDF3
import pandas as pd
from PyPDF3.pdf import PageObject

from common import cartesian_join


def to_int(s):
    if not s:
        return math.nan
    return int(s.replace('.', '').replace(' ', ''))


def to_float(s):
    if not s:
        return math.nan
    return float(s.replace(',', '.'))


# Useful to find the page containing the table
TABLE_CAPTION_PATTERN = re.compile(
    'TABELLA [0-9- ]+ DISTRIBUZIONE DEI CASI .+ PER FASCIA DI ET. ',
    re.IGNORECASE)

COLUMN_PREFIXES = ('male_', 'female_', '')
COLUMN_FIELDS = ('cases', 'cases_percentage', 'deaths', 'deaths_percentage', 'fatality_rate')
COLUMNS = ('age_group', *cartesian_join(COLUMN_PREFIXES, COLUMN_FIELDS))
COLUMN_CONVERTERS = [str] + [to_int, to_float, to_int, to_float, to_float] * 3  # noqa
CONVERTER_BY_COLUMN = dict(zip(COLUMNS, COLUMN_CONVERTERS))


class TableExtractionError(Exception):
    pass


class TableExtractor(abc.ABC):
    @abc.abstractmethod
    def extract(self, report_path) -> pd.DataFrame:
        pass

    def __call__(self, report_path):
        return self.extract(report_path)


class PyPDFTableExtractor(TableExtractor):
    unknown_age_matcher = re.compile('(età non nota|non not[ao])', flags=re.IGNORECASE)

    def extract(self, report_path) -> pd.DataFrame:
        pdf = PyPDF3.PdfFileReader(str(report_path))
        page, _ = find_table_page(pdf)
        # For some reason, the extracted text contains a lot of superfluous newlines
        text = page.extractText().replace('\n', '')
        text = self.unknown_age_matcher.sub('unknown', text)
        start = text.find('0-9')
        text = text[start:]
        text = text.replace(', ', ',')   # from 28/09, they write "1,5" as "1, 5"
        tokens = text.split(' ')
        num_rows = 11
        num_columns = len(COLUMNS)
        rows = []
        for i in range(num_rows):
            start = i * num_columns
            end = start + num_columns
            row = tokens[start:end]
            for j in range(num_columns):
                row[j] = COLUMN_CONVERTERS[j](row[j])
            rows.append(row)
        df = pd.DataFrame(rows, columns=COLUMNS)

        return normalize_table(df)


def find_table_page(pdf: PyPDF3.PdfFileReader) -> Tuple[PageObject, int]:
    """ Returns the page containing the table and its 0-based index. """
    num_pages = pdf.getNumPages()

    for i in range(1, num_pages):  # skip the first page, the table is certainly not there
        page = pdf.getPage(i)
        text = page.extractText().replace('\n', '')
        if TABLE_CAPTION_PATTERN.search(text):
            return page, i
    else:
        raise TableExtractionError('could not find the table in the pdf')


def normalize_table(table: pd.DataFrame) -> pd.DataFrame:
    # Replace '≥90' with ascii equivalent '>=90'
    table.at[9, 'age_group'] = '>=90'
    # Replace 'Età non nota' with english translation
    table.at[10, 'age_group'] = 'unknown'
    return table


def sanity_check_with_totals(table: pd.DataFrame, totals):
    columns = cartesian_join(COLUMN_PREFIXES, ['cases', 'deaths'])
    for col in columns:
        actual_sum = table[col].sum()
        if actual_sum != totals[col]:
            raise TableExtractionError(
                f'column "{col}" sum() is inconsistent with the value reported '
                f'in the last row of the table: {actual_sum} != {totals[col]}')


def convert_row(row, converters=CONVERTER_BY_COLUMN):
    return {key: converters[key](value) for key, value in row.items()}
