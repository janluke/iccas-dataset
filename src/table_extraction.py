import abc
import logging
import math
import re
from datetime import datetime
from typing import Any, Callable, Tuple

import pandas as pd
from PyPDF3 import PdfFileReader
from reagex import reagex

from common import cartesian_join, get_italian_date_pattern, process_datetime_tokens

logger = logging.getLogger(__name__)


def parse_int(s: str) -> int:
    if s == "-":  # report of 2020-10-20
        return 0
    return int(s.replace(".", "").replace(" ", ""))


def parse_float(s: str) -> float:
    if not s:
        # This case was useful on a previous version of the script (using Tabula)
        # that read the row with totals which contains empty values
        return math.nan
    if s == "-":  # report of 2020-10-20
        return 0.0
    return float(s.replace(",", "."))


COLUMN_PREFIXES = ("male_", "female_", "")
COLUMN_FIELDS = (
    "cases",
    "cases_percentage",
    "deaths",
    "deaths_percentage",
    "fatality_rate",
)
DERIVED_COLUMNS = list(
    cartesian_join(
        COLUMN_PREFIXES, ["cases_percentage", "deaths_percentage", "fatality_rate"]
    )
)

# Report table columns
INPUT_COLUMNS = ("age_group", *cartesian_join(COLUMN_PREFIXES, COLUMN_FIELDS))
Converter = Callable[[str], Any]
FIELD_CONVERTERS = [parse_int, parse_float, parse_int, parse_float, parse_float]
COLUMN_CONVERTERS = [lambda x: x] + FIELD_CONVERTERS * 3
# Output DataFrame columns
OUTPUT_COLUMNS = ("date", *INPUT_COLUMNS)

# Useful to find the page containing the table
TABLE_CAPTION_PATTERN = re.compile(
    "tabella [0-9- ]+ distribuzione dei casi .+ per fascia di et. ", re.IGNORECASE
)

DATETIME_PATTERN = re.compile(
    get_italian_date_pattern(sep="[ ]?")
    + reagex(
        "[- ]* ore {hour}:{minute}",
        hour="[o0-2]?[o0-9]|3[o0-1]",  # in some reports they wrote 'o' instead of zero
        minute="[o0-5][o0-9]",
    ),
    re.IGNORECASE,
)


class TableExtractionError(Exception):
    pass


class TableExtractor(abc.ABC):
    """
    Having a base class may seem unnecessary now that I have a single implementation,
    but, trust me, it was convenient in the past and it may turn useful again in the
    future. Furthermore, there's no harm in it.
    """

    @abc.abstractmethod
    def _extract(self, report_path) -> pd.DataFrame:
        """Extracts the report table as it is, adding only the "date" column."""
        pass

    def extract(self, report_path) -> pd.DataFrame:
        """
        Extracts the report table and returns it as a DataFrame after renaming
        stuff (remove non-ASCII characters, translate italian to english) and
        recomputing derived columns. It also performs some sanity checks on the
        extracted data.
        """
        table = self._extract(report_path)

        # Replace '≥90' with ascii equivalent '>=90'
        table.at[9, "age_group"] = ">=90"
        # Replace 'Età non nota' with english translation
        table.at[10, "age_group"] = "unknown"

        # Ensure (male_{something} + female_{something} <= {something})
        # Remember that {something} includes people of unknown sex
        check_sum_of_males_and_females_not_more_than_total(table)
        refined_table = recompute_derived_columns(table)
        return refined_table

    def __call__(self, report_path):
        return self.extract(report_path)


class PyPDFTableExtractor(TableExtractor):
    unknown_age_matcher = re.compile("(età non nota|non not[ao])", flags=re.IGNORECASE)

    def _extract(self, report_path) -> pd.DataFrame:
        num_rows = 11
        num_columns = len(INPUT_COLUMNS)

        pdf = PdfFileReader(str(report_path))
        date = extract_datetime(extract_text(pdf, page=0))
        page, _ = find_table_page(pdf)
        page = self.unknown_age_matcher.sub("unknown", page)
        data_start = page.find("0-9")
        # on 2020-09-28, they wrote floats like "1, 5"
        raw_data = page[data_start:].replace(", ", ",")
        tokens = raw_data.split()
        # In some cases, PyPDF3 doesn't read the token "≥90" (probably a bug),
        # so I insert that manually in case is missing. Couldn't the token in
        # that position be "90" by coincidence? Nope. If "≥90" is missing, the
        # token in that position is the cumulative total of cases with age >= 90
        # which has never been equal to 90 (and never will be).
        if tokens[9 * num_columns] not in {"90", ">90", "≥90"}:
            tokens.insert(9 * num_columns, ">=90")
        rows = []
        for i in range(num_rows):
            start = i * num_columns
            end = start + num_columns
            row_tokens = tokens[start:end]
            try:
                values = convert_values(row_tokens, COLUMN_CONVERTERS)
            except ValueError or TypeError as err:
                logger.debug('Error in row %d: ')
                raise TableExtractionError(
                    f"\nError while converting values of row {i}: {err}.\n"
                    f"Row tokens: {' | '.join(row_tokens)}"
                )
            row = [date, *values]
            rows.append(row)
        report_data = pd.DataFrame(rows, columns=["date", *INPUT_COLUMNS])
        return report_data


def extract_text(pdf: PdfFileReader, page: int) -> str:
    # For some reason, the extracted text contains a lot of superfluous newlines
    return pdf.getPage(page).extractText().replace("\n", "")


def extract_datetime(text: str) -> datetime:
    match = DATETIME_PATTERN.search(text)
    if match is None:
        raise TableExtractionError("extraction of report datetime failed")
    datetime_dict = process_datetime_tokens(match.groupdict())
    return datetime(**datetime_dict)  # type: ignore


def find_table_page(pdf: PdfFileReader) -> Tuple[str, int]:
    """
    Finds the page containing the data table, then returns a tuple with:
    - the text extracted from the page, pre-processed
    - the page number (0-based)
    """
    num_pages = pdf.getNumPages()

    for i in range(1, num_pages):  # skip the first page, the table is not there
        text = extract_text(pdf, page=i)
        if TABLE_CAPTION_PATTERN.search(text):
            return text, i
    else:
        raise TableExtractionError("could not find the table in the pdf")


def check_sum_of_males_and_females_not_more_than_total(table: pd.DataFrame):
    for what in ["cases", "deaths"]:
        males_plus_females = table[[f"male_{what}", f"female_{what}"]].sum(axis=1)
        deltas = table[what] - males_plus_females
        if (deltas < 0).any():
            raise TableExtractionError(
                f"table[male_{what}] + table[female_{what}] > table[{what}] for some "
                f"age groups. Deltas:\n{deltas}"
            )


def convert_values(values, converters):
    if len(values) != len(converters):
        raise ValueError
    return [converter(value) for value, converter in zip(values, converters)]


def recompute_derived_columns(x: pd.DataFrame) -> pd.DataFrame:
    """ Returns a new DataFrame with all derived columns (re)computed. """
    y = x.copy()
    total_cases = x["cases"].sum()
    total_deaths = x["deaths"].sum()
    y["cases_percentage"] = x["cases"] / total_cases * 100
    y["deaths_percentage"] = x["deaths"] / total_deaths * 100
    y["fatality_rate"] = x["deaths"] / x["cases"] * 100

    # REMEMBER: male_cases + female_cases != total_cases,
    # because total_cases also includes cases of unknown sex
    for what in ["cases", "deaths"]:
        total = x[f"male_{what}"] + x[f"female_{what}"]
        denominator = total.replace(0, 1)  # avoid division by 0
        for sex in ["male", "female"]:
            y[f"{sex}_{what}_percentage"] = x[f"{sex}_{what}"] / denominator * 100

    for sex in ["male", "female"]:
        y[f"{sex}_fatality_rate"] = x[f"{sex}_deaths"] / x[f"{sex}_cases"] * 100

    return y[list(OUTPUT_COLUMNS)]  # ensure columns are in the right order
