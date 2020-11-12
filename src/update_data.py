"""
Download new reports and make all datasets, skipping existing ones.
"""
import logging

from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

from common import (
    DATA_DIR,
    REPORTS_DIR,
    REPORTS_DATA_DIR,
    get_dataset_path,
    get_latest_data_date,
    get_report_data_path,
    list_datasets_by_date,
)
from table_extraction import TableExtractor, PyPDFTableExtractor

logger = logging.getLogger(__name__)


def extract_data_from_reports(
    reports_dir: Path = REPORTS_DIR,
    output_dir: Path = REPORTS_DATA_DIR,
    table_extractor: TableExtractor = PyPDFTableExtractor(),
    skip_existing=True,
) -> List[Path]:
    """
    Extracts table data from PDF reports saved in `reports_dir` and generates
    one file per report in `output_dir`. If `skip_existing` is `True`, all
    reports corresponding to existing datasets (in `output_dir`) are ignored.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    new_dataset_paths = []
    relative_paths = sorted(reports_dir.iterdir())
    for relpath in relative_paths:
        path = reports_dir / relpath
        date = relpath.stem
        out_path = get_report_data_path(date, dirpath=output_dir)
        if skip_existing and out_path.exists():
            logger.info("Dataset for report of %s already exists", date)
        else:
            logger.info("Making dataset for report of %s", date)
            table = table_extractor(path)
            # Check that the date on the filename matches that written in the PDF
            pdf_date = table.date.iloc[0].strftime("%Y-%m-%d")
            if pdf_date != date:
                raise Exception(
                    f"Date extracted from the PDF ({pdf_date}) is inconsistent "
                    f"with that extracted from the filename ({date}). Give a look."
                )
            table["date"] = table["date"].apply(
                lambda dt: datetime.isoformat(dt, timespec="minutes")
            )
            table.to_csv(out_path, index=False, line_terminator="\n")
            new_dataset_paths.append(out_path)
            logger.info("Dataset saved to: %s", out_path)

    logger.info("New datasets written: %s\n", new_dataset_paths)
    return new_dataset_paths


def make_dataset(input_dir=REPORTS_DATA_DIR, output_dir=DATA_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = get_dataset_path(dirpath=output_dir)

    ordered_parts = [
        pd.read_csv(path, index_col="date")
        for _, path in list_datasets_by_date(input_dir)
    ]
    if not ordered_parts:
        logger.info("No datasets found in", input_dir)
        return False

    dataset = pd.concat(ordered_parts, axis=0)
    dataset.to_csv(out_path, line_terminator="\n")
    logger.info("Full dataset written to: %s", out_path)
    return out_path


if __name__ == "__main__":
    import argparse
    from download_reports import download_missing_reports

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    download_missing_reports(after=get_latest_data_date())
    change_list = extract_data_from_reports(skip_existing=not args.overwrite)
    if args.overwrite or change_list:
        path_full = make_dataset()
        change_list.append(path_full)

    print(' '.join(str(path) for path in change_list))
