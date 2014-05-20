import os
import shutil
import requests
from requests.auth import HTTPDigestAuth
from collections import namedtuple
import string

SERVER = 'http://localhost:8000'
DOMAIN = 'uth-rhd'
URL = "%s/a/%s" % (SERVER, DOMAIN)

# SCANNER_DIR = '/Users/tyler/code/dimagi/uth-rhd-code/vscan/'
# SCANNER_DIR = '/Volumes/NO NAME'
# SCANNER_DIR = '/Users/tyler/Desktop'
# SCANNER_DIR = '/Volumes/PENDRIVE'

try:
    # find first windows drive with the special scanner file present
    SCANNER_DIR = ['%s:' % d for d in string.uppercase if (
                   os.path.exists(os.path.join('%s:' % d, 'Archive')) and
                   os.path.exists(os.path.join('%s:' % d, 'ScannerID.GEUSHH'))
    )][0]
except IndexError:
    SCANNER_DIR = None

ARCHIVE_PATH = os.path.join(SCANNER_DIR or '', 'Archive')


class Exam(object):
    def __init__(self, directory, serial, scan_id, date):
        self.serial = serial
        self.scan_id = scan_id
        self.date = date
        self.directory = directory

        self.files = self.collect_files()

    def collect_files(self):
        files = os.listdir(self.directory)
        for f in files:
            if f not in ['.', '..']:
                yield f


def parse_archive():
    exams = os.listdir(ARCHIVE_PATH)
    for exam in exams:
        exam_dir = os.path.join(ARCHIVE_PATH, exam)
        if exam not in ['.', '..'] and os.path.isdir(exam_dir):
            try:
                yield Exam(exam_dir, *exam.split('_'))
            except Exception:
                # if the directory doesn't resemble an exam, we don't
                # care about the error or the directory
                continue


def pack_directory(directory):
    packed_directory = {}

    for root, dirs, files in os.walk(directory):
        for f in files:
            packed_directory[f] = open(os.path.join(root, f), 'rb')

    return packed_directory


def upload_exam(exam, index, total_count, retry_count=0):
    if not retry_count:
        print ""
        print "Uploading exam with id %s (%s of %s)." % (
            exam.scan_id.lstrip('0'),
            index + 1,
            total_count
        )
    else:
        print ""
        print "Retrying exam with id %s (%s of %s), attempt %s" % (
            exam.scan_id.lstrip('0'),
            index + 1,
            total_count,
            retry_count + 1
        )
    files = pack_directory(exam.directory)

    try:
        s = requests.Session()
        s.auth = HTTPDigestAuth('twymer@dimagi.com', 'a long password that i should change')
        r = s.post(
            URL + '/vscan_upload',
            files=files,
            data={
                'scanner_serial': exam.serial,
                'scan_id': exam.scan_id,
                'scan_time': exam.date
            },
        )
    except requests.ConnectionError:
        print "Could not connect to server."
        return

    # clean up
    for f in files.values():
        f.close()

    print "Processed exam: %s" % os.path.split(exam.directory)[-1]
    print "Result code: %s" % r.status_code

    if r.status_code == 200:
        print "Result: %s" % r.json()['result']
        print "Message: %s" % r.json()['message']

        current_dir = os.path.dirname(os.path.realpath(__file__))
        shutil.move(
            exam.directory,
            os.path.join(current_dir, 'complete')
        )

    else:
        print "Result: Failed"

    return r


def find_duplicate_exam_ids(exam_ids):
    dupes = []
    for exam in exam_ids:
        if exam not in dupes and exam_ids.count(exam) > 1:
            dupes.append(exam)

    return dupes


def upload():
    print "Checking exams"
    exams = list(parse_archive())
    print "Done checking exams"

    if not len(exams):
        print "No exams to upload"
        return

    r = requests.get(
        url=URL + '/pending_exams/' + exams[0].serial,
        auth=HTTPDigestAuth('t@w.com', 'asdf'),
    )

    if r.status_code != 200 or 'exam_ids' not in r.json().keys():
        import bpdb; bpdb.set_trace()
        print "Failed to get pending exam list from server. Please try again later."
        return

    pending_exams = r.json()['exam_ids']
    duplicate_exams = find_duplicate_exam_ids(pending_exams)

    failed_uploads = []
    FailedUpload = namedtuple(
        'FailedUpload', 'exam exam_index failure_count'
    )

    for i, exam in enumerate(exams):
        if exam.scan_id.lstrip('0') not in pending_exams:
            print "\nSkipping exam %s since there is no found pending exam." % exam.scan_id.lstrip('0')
            continue

        if exam.scan_id.lstrip('0') in duplicate_exams:
            print "\nSkipping exam %s since there are duplicate potential exams to match to." % exam.scan_id.lstrip('0')
            continue

        result = upload_exam(exam, i, len(exams))

        if not result or result.status_code != 200:
            failed_uploads.append(FailedUpload(
                exam,
                i,
                1
            ))

    while len(failed_uploads):
        current_upload = failed_uploads.pop(0)

        result = upload_exam(
            current_upload.exam,
            current_upload.exam_index,
            len(exams),
            current_upload.failure_count
        )

        if (not result or result.status_code != 200) and current_upload.failure_count < 3:
            failed_uploads.append(FailedUpload(
                current_upload.exam,
                current_upload.exam_index,
                current_upload.failure_count + 1
            ))


if __name__ == '__main__':
    if SCANNER_DIR:
        try:
            upload()
        except Exception as e:
            print e
    else:
        print "Vscan not found"

    print('\nUploading complete. Press enter to exit.')
    raw_input()
