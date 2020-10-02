"""
Parse the ISS news page to obtain all links to reports published until now,
then download all reports missing in the ISS_REPORT folder.
"""
import re
from pathlib import Path
from pprint import pprint
from typing import Dict
from urllib.parse import (
    unquote,
    urljoin
)

import requests
from reagex import reagex
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from paths import (
    REPORTS_DIR,
    get_report_path
)

# Page from which reports URL are extracted
ISS_NEWS_URL = 'https://www.epicentro.iss.it/coronavirus/aggiornamenti'

# Only reports after this date contain the data we are looking for
SKIP_REPORTS_TO_DATE = '2020-03-11'

# Some reports may not be published in the ISS News page (by mistake).
EXTRA_REPORT_URLS = {
    '2020-03-16': 'https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino%20sorveglianza%20integrata%20COVID-19_16%20marzo%202020.pdf'
}


def _report_date_extractor():
    italian_months = ('gennaio febbraio marzo aprile maggio giugno luglio agosto '
                      'settembre ottobre novembre dicembre').split()
    italian_month_as_num = dict(zip(italian_months, range(1, 13)))

    # Used for extracting the report date from the pdf filename (kinda fragile but it works)
    date_pattern = re.compile(
        reagex(
            r'{day}{_sep}{month}{_sep}{year}',
            day=r'\d{1,2}', year=r'\d{4}',
            month='|'.join(italian_months),
            _sep='[-_ ]'),
        re.IGNORECASE)

    def extract_date_from_filename(fname):
        normalized_fname = unquote(fname).lower()
        match = date_pattern.search(normalized_fname)
        if not match:
            raise ValueError('the file name does not contains a date: %s' % fname)
        groups = match.groupdict()
        groups['day'] = int(groups['day'])
        groups['month'] = italian_month_as_num[groups['month']]
        return '{year}-{month:02d}-{day:02d}'.format(**groups)

    return extract_date_from_filename


get_date_from_report_filename = _report_date_extractor()


def extract_report_urls_from(page_url=ISS_NEWS_URL, session=None):
    resp = session.get(page_url) if session else requests.get(page_url)
    resp.raise_for_status()
    relative_urls = re.findall('href="(bollettino/Bollettino.+[.]pdf)"', resp.text)
    return [urljoin(ISS_NEWS_URL, relurl) for relurl in relative_urls]


def get_http_session(retries=3, backoff_factor=0.3,
                     status_forcelist=(500, 502, 504)) -> requests.Session:
    """ Taken from: https://www.peterbe.com/plog/best-practice-with-retries-with-requests """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def download_file(url: str, path: Path, session=None):
    resp = session.get(url) if session else requests.get(url)
    resp.raise_for_status()
    path.write_bytes(resp.content)


def download_missing_reports(urls_by_date: Dict[str, str] = EXTRA_REPORT_URLS,
                             scrape_url: str = ISS_NEWS_URL,
                             output_dir: Path = REPORTS_DIR,
                             after: str = SKIP_REPORTS_TO_DATE):
    """
    Downloads missing reports to `output_dir`. Report URLs are extracted from `scrape_url`
    but you can use `urls_by_date` to override them or add new ones.
    All reports relative to any date <= `after`, and in any case <= `SKIP_REPORTS_TO_DATE`,
    are ignored.
    """
    after = max(after, SKIP_REPORTS_TO_DATE)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    session = get_http_session()
    fetched_urls = extract_report_urls_from(scrape_url, session) if scrape_url else []
    date2url = {
        get_date_from_report_filename(url): url
        for url in fetched_urls
    }
    date2url.update(urls_by_date)
    print('Report URLs by date:')
    pprint(date2url, indent=2)
    print('')

    new_report_paths = []
    for date, url in date2url.items():
        if date <= after:
            continue
        path = get_report_path(date=date, dirpath=output_dir)
        if not path.exists():
            print('Found new report (%s): %s' % (date, url))
            print('Downloading to', path, '...', end=' ')
            download_file(url, path, session)
            new_report_paths.append(path)
            print('DONE')
    if not new_report_paths:
        print('No new reports found')
    return new_report_paths


if __name__ == '__main__':
    download_missing_reports()
