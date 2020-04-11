"""
Script meant to be run with cronjob (or Windows 10 planning tool) in order to
automatically check for new reports, make new datasets and commit/push to a
specific branch in case of success. Email and system notifications are sent in
case case of errors or success.

This script will run in a copy of the repository that I don't use for development
and will be called by a bash/powershell script that executes "git pull" before
running this script.
"""
import argparse
import json
import logging
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

import git
from pynotifier import Notification

from download_reports import download_missing_reports
from make_datasets import make_full_dataset, make_single_date_datasets
from settings import get_date_from_filename

logging.basicConfig(
    format='%(asctime)-15s : %(levelname)s : %(message)s',
    level=logging.INFO
)

CREDENTIALS_PATH = Path('credentials.json')     # email credentials
COMMIT_TEMPLATE = '[iccas-bot] Update data to {date}'


class EmailSender:
    """ Wrapper of smtlib.SMTP for sending authenticated emails (bye default using GMail) """
    def __init__(self, email, password, host='smtp.gmail.com', port=587):
        self.email = email
        self.password = password
        self.smtp = smtp = smtplib.SMTP(host, port=port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(self.email, self.password)

    def quit(self):
        self.smtp.quit()

    def send_message(self, msg: EmailMessage):
        return self.smtp.send_message(msg)

    def send_mail(self, recipients, subject, content):
        msg = EmailMessage()
        msg['From'] = self.email
        msg['To'] = recipients
        msg['Subject'] = subject
        msg.set_content(content)
        return self.send_message(msg)


class Notifier:
    """ Send a system notification + optional email notifications """
    def __init__(self, system=True, emails=(), email_sender: Optional[EmailSender] = None,
                 prefix: str = ''):
        self.system_notification_enabled = system
        self.prefix = prefix
        self.emails = emails
        self.email_sender = email_sender
        if self.emails and not self.email_sender:
            raise ValueError('you must pass an email_sender for sending emails')

    def notify(self, title, description, duration=30, urgency=Notification.URGENCY_NORMAL,
               email_message: Optional[EmailMessage] = None):
        title = self.prefix + title
        Notification(
            title=title,
            description=description,
            duration=duration,
            urgency=urgency
        ).send()
        if self.emails:
            if email_message:
                return self.email_sender.send_message(email_message)
            else:
                return self.email_sender.send_mail(self.emails, title, description)


def main(branch='master', push=False, emails_to_notify=[]):
    creds = json.loads(CREDENTIALS_PATH.read_text())
    email_sender = EmailSender(creds['EMAIL_ADDRESS'], creds['EMAIL_PASSWORD'])
    notifier = Notifier(emails=emails_to_notify, email_sender=email_sender)

    logging.info('Opening and checking the repository...')
    repo = git.Repo('.')
    assert repo.active_branch.name == branch

    try:
        logging.info('Checking for new reports...')
        new_report_paths = download_missing_reports()
        if not new_report_paths:
            logging.info('No new reports. Exit.')
            sys.exit(0)
        logging.info('New reports found: %s', ', '.join(map(str, new_report_paths)))

        new_dataset_paths = make_single_date_datasets(skip_existing=True)
        if not new_dataset_paths:
            logging.info('No new datasets written. Exit.')
            sys.exit(0)
        logging.info('New datasets: %s', ', '.join(map(str, new_dataset_paths)))

        full_dataset_path = make_full_dataset()

        # git add
        files_to_add = [str(path) for path in new_dataset_paths + [full_dataset_path]]
        logging.info('Command: git add %s', ' '.join(files_to_add))
        repo.index.add(items=files_to_add)

        # git commit
        latest_date = max(get_date_from_filename(path.name) for path in new_dataset_paths)
        commit_msg = COMMIT_TEMPLATE.format(date=latest_date)
        logging.info('Command: git commit -m %r', commit_msg)
        repo.index.commit(commit_msg)

        # git push
        if push:
            # TODO: handle push errors
            refspec = '{0}:{0}'.format(branch)
            logging.info('Command: git push %s', refspec)
            repo.remote('origin').push(refspec=refspec)
            notifier.notify('Pushed new ICCAS datasets', commit_msg)
        else:
            notifier.notify('New commit waiting for push', commit_msg)

        sys.exit(0)

    except Exception as exc:
        notifier.notify('Fatal error', repr(exc))
        logging.exception('Exception was raised')
        raise
    finally:
        email_sender.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--branch', default='master', help='repository branch to commit on / push to')
    parser.add_argument('--push', action='store_true', help='commit and push new/updated datasets')
    parser.add_argument('--emails', nargs='*', default=[], help='email address(es) to notify')
    args = parser.parse_args()

    main(branch=args.branch, push=args.push, emails_to_notify=args.emails)
