"""
Parse the ISS news page to obtain all links to reports published until now,
then download all reports missing in the ISS_REPORT folder.
"""
import re
from pathlib import Path
from pprint import pprint
from urllib.parse import unquote, urljoin

import requests
from reagex import reagex

from settings import ISS_REPORTS_DIR, ISS_REPORT_MIN_DATE, get_report_path

# Page where reports URL are searched
ISS_NEWS_URL = 'https://www.epicentro.iss.it/coronavirus/aggiornamenti'

# Some reports may not be published in the ISS News page (by mistake) or have
# problematic/wrong filenames (not happened yet). Put problematic URLs here when
# they present to you.
REPORT_URLS = {
    '2020-03-16': 'https://www.epicentro.iss.it/coronavirus/bollettino/Bollettino%20sorveglianza%20integrata%20COVID-19_16%20marzo%202020.pdf'
}


def _iss_report_filename_date_parser():
    italian_months = ('gennaio febbraio marzo aprile maggio giugno luglio agosto '
                      'settembre ottobre novembre dicembre').split()
    italian_month_as_num = dict(zip(italian_months, range(1, 13)))

    # Used for extracting the report date from the pdf filename (kinda fragile but it works)
    date_pattern = re.compile(
        reagex(
            r'{day}{_sep}{month}{_sep}{year}',
            day='\d{1,2}', year='\d{4}',
            month='|'.join(italian_months),
            _sep='[-_ ]'),
        re.IGNORECASE)

    def parse_date_from_filename(fname):
        normalized_fname = unquote(fname).lower()
        match = date_pattern.search(normalized_fname)
        if not match:
            raise Exception('unable to extract date from ISS report filename: ' + fname)
        groups = match.groupdict()
        groups['day'] = int(groups['day'])
        groups['month'] = italian_month_as_num[groups['month']]
        return '{year}-{month:02d}-{day:02d}'.format(**groups)

    return parse_date_from_filename


get_date_from_report_filename = _iss_report_filename_date_parser()


def find_report_urls_in(iss_news_url=ISS_NEWS_URL):
    resp = requests.get(iss_news_url)
    resp.raise_for_status()
    relative_urls = re.findall('href="(bollettino/Bollettino.+[.]pdf)"', resp.text)
    return [urljoin(ISS_NEWS_URL, relurl) for relurl in relative_urls]


def download_file(url: str, path: Path):
    resp = requests.get(url)
    resp.raise_for_status()
    path.write_bytes(resp.content)


def download_missing_reports(urls_by_date=REPORT_URLS,
                             scrape_url=ISS_NEWS_URL,
                             output_dir=ISS_REPORTS_DIR,
                             min_date=ISS_REPORT_MIN_DATE):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fetched_urls = find_report_urls_in(scrape_url) if scrape_url else []
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
