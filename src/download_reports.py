"""
Parse the ISS news page to obtain all links to reports published until now,
then download all reports missing in the ISS_REPORT folder.
"""
import json
import logging
import re
from pathlib import Path
from typing import Dict
from urllib.parse import unquote, urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from common import (
    REPORTS_DIR,
    get_italian_date_pattern,
    get_latest_data_date,
    get_report_path,
    process_datetime_tokens,
)

# Page from which reports URL are extracted
ISS_NEWS_URL = "https://www.epicentro.iss.it/coronavirus/aggiornamenti"

# Only reports after this date contain the data we are looking for
SKIP_REPORTS_TO_DATE = "2020-03-11"

# Some reports may not be published in the ISS News page (by mistake).
EXTRA_REPORT_URLS = {
    "2020-03-16": "https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino%20sorveglianza%20integrata%20COVID-19_16%20marzo%202020.pdf"  # noqa
}

# Used for extracting the report date from the pdf filename
FILENAME_DATE_PATTERN = re.compile(get_italian_date_pattern(sep="[-_ ]"), re.IGNORECASE)

logger = logging.getLogger(__name__)


def get_date_from_report_url(fname: str) -> str:
    normalized_fname = unquote(fname).lower()
    match = FILENAME_DATE_PATTERN.search(normalized_fname)
    if not match:
        raise ValueError("the file name does not contain a date: %s" % fname)
    datetime_dict = process_datetime_tokens(match.groupdict())
    return "{year}-{month:02d}-{day:02d}".format(**datetime_dict)


def extract_report_urls_from(page_url=ISS_NEWS_URL, session=None):
    resp = session.get(page_url) if session else requests.get(page_url)
    resp.raise_for_status()
    relative_urls = re.findall('href="(bollettino/Bollettino.+[.]pdf)"', resp.text)
    return [urljoin(ISS_NEWS_URL, relurl) for relurl in relative_urls]


def get_http_session(
    retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)
) -> requests.Session:
    """
    Taken from: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def download_file(url: str, path: Path, session=None):
    resp = session.get(url) if session else requests.get(url)
    resp.raise_for_status()
    path.write_bytes(resp.content)


def download_missing_reports(
    urls_by_date: Dict[str, str] = EXTRA_REPORT_URLS,
    scrape_url: str = ISS_NEWS_URL,
    output_dir: Path = REPORTS_DIR,
    after: str = SKIP_REPORTS_TO_DATE,
):
    """
    Downloads missing reports to `output_dir`. Report URLs are extracted from
    `scrape_url` but you can use `urls_by_date` to override them or add new ones.
    All reports relative to any date <= `after` and in any case less or equal to
    `SKIP_REPORTS_TO_DATE` are ignored.
    """
    after = max(after, SKIP_REPORTS_TO_DATE)
    logger.info('Looking for reports following %s', after)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    session = get_http_session()
    fetched_urls = extract_report_urls_from(scrape_url, session) if scrape_url else []
    date2url = {get_date_from_report_url(url): url for url in fetched_urls}
    date2url.update(urls_by_date)
    logger.debug("Report URLs by date:\n%s", json.dumps(date2url, indent=2))

    new_report_paths = []
    for date, url in date2url.items():
        if date <= after:
            continue
        path = get_report_path(date=date, dirpath=output_dir)
        if not path.exists():
            logger.info("Downloading new report (%s): %s", date, url)
            download_file(url, path, session)
            new_report_paths.append(path)
    if not new_report_paths:
        logger.info("Nothing new")
    return new_report_paths


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Download PDF reports not already available in the reports/ folder. "
                    "Outputs the (space-separated) list of new reports (if any)."
    )
    parser.add_argument(
        # This option exists for running the script in GitHub actions. The repo doesn't
        # store the PDF reports, so I use the date of the latest dataset in data/by-date
        # to decide what report(s) to download.
        '--since-latest-dataset-date', action='store_true',
        help="Ignore reports predating the date of the latest dataset (in data/by-date)"
    )
    parser.add_argument('--debug', action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    new_paths = download_missing_reports(
        after=get_latest_data_date() if args.since_latest_dataset_date else ''
    )

    print(" ".join(str(path) for path in new_paths))
