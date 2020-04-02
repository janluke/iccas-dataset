"""
Parse the ISS news page to obtain all links to reports published until now,
then download all reports missing in the ISS_REPORT folder.
"""
import re
from pathlib import Path
from urllib.parse import unquote, urljoin

import requests
from reagex import reagex

from settings import ISS_REPORTS_DIR, ISS_REPORT_MIN_DATE, get_report_path

ISS_NEWS_URL = 'https://www.epicentro.iss.it/coronavirus/aggiornamenti'

ITA_MONTHS = ('gennaio febbraio marzo aprile maggio giugno luglio agosto '
              'settembre ottobre novembre dicembre').split()
ITA_MONTH_TO_NUM = dict(zip(ITA_MONTHS, range(1, 13)))

# Used for extracting the report date from the pdf filename (kinda fragile but it works)
DATE_PATTERN = re.compile(
    reagex(
        r'{day}{_sep}{month}{_sep}{year}',
        day='\d{1,2}', year='\d{4}',
        month='|'.join(ITA_MONTHS),
        _sep='[-_ ]'),
    re.IGNORECASE
)


def extract_date_from_report_fname(fname):
    normalized_fname = unquote(fname).lower()
    match = DATE_PATTERN.search(normalized_fname)
    if not match:
        raise Exception('unable to extract date from ISS report filename: ' + fname)
    groups = match.groupdict()
    groups['day'] = int(groups['day'])
    groups['month'] = ITA_MONTH_TO_NUM[groups['month']]
    return '{year}-{month:02d}-{day:02d}'.format(**groups)


def fetch_all_report_urls(iss_news_url=ISS_NEWS_URL):
    resp = requests.get(iss_news_url)
    resp.raise_for_status()
    relative_urls = re.findall('href="(bollettino/Bollettino.+[.]pdf)"', resp.text)
    return [urljoin(ISS_NEWS_URL, relurl) for relurl in relative_urls]


def download_file(url: str, path: Path):
    resp = requests.get(url)
    resp.raise_for_status()
    path.write_bytes(resp.content)


def download_missing_reports(iss_news_url=ISS_NEWS_URL,
                             output_dir=ISS_REPORTS_DIR,
                             min_date=ISS_REPORT_MIN_DATE):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    report_urls = fetch_all_report_urls(iss_news_url)
    new_report_paths = []
    for url in report_urls:
        date = extract_date_from_report_fname(url)
        if date < min_date:
            continue
        path = get_report_path(date=date, dirpath=output_dir)
        if not path.exists():
            print('Found new report (%s): %s' % (date, url))
            print('Downloading to', path, '...', end=' ')
            download_file(url, path)
            new_report_paths.append(path)
            print('DONE')
    if not new_report_paths:
        print('No new reports found')
    return new_report_paths


if __name__ == '__main__':
    download_missing_reports()
