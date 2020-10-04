from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent

REPORTS_DIR = Path(PROJECT_DIR, 'reports')
REPORT_FNAME = '{date}.pdf'

DATA_DIR = Path(PROJECT_DIR, 'data')
REPORTS_DATA_DIR = Path(DATA_DIR, 'by-date')
REPORT_DATA_FNAME = 'iccas_{date}'  # dataset containing data extracted from a single report
DATASET_FNAME = 'iccas_full'  # dataset containing data extracted from all reports


def get_report_path(date, dirpath=REPORTS_DIR):
    return Path(dirpath, REPORT_FNAME.format(date=date))


def get_report_data_path(date, ext='.csv', dirpath=REPORTS_DATA_DIR):
    return Path(dirpath, REPORT_DATA_FNAME.format(date=date) + ext)


def get_dataset_path(ext='.csv', dirpath=DATA_DIR):
    return Path(dirpath, DATASET_FNAME + ext)
