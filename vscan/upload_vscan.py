import os
import shutil
import requests
from requests.auth import HTTPBasicAuth
from collections import namedtuple
import string
import ConfigParser
import getpass
import sys

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


def get_file_size(file_path):
    return float(os.stat(file_path).st_size) / 1024 / 1024


def pack_directory(directory, max_upload_size):
    current_mbs = 0
    skipped = False
    packed_directory = {}

    for root, dirs, files in os.walk(directory):
        for f in files:
            file_path = os.path.join(root, f)
            file_size = get_file_size(file_path)

            if f[-4:].lower() == '.wav' or f[0] == '.':
                # we don't care about sound clips for the study
                # so lets not waste bandwidth on them. also ignore any bogus
                # .DS_Store or other files like that that will
                # crash the xml parser
                continue

            # only add the file if we aren't going over our system limit
            if current_mbs + file_size < max_upload_size:
                packed_directory[f] = open(file_path, 'rb')
                current_mbs += file_size
            else:
                skipped = True

    if skipped:
        print "Some images or videos were skipped due to exam size being too large."

    return packed_directory


def upload_exam(config, exam, index, total_count, retry_count=0):
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
    files = pack_directory(exam.directory, config['max_upload_size'])

    try:

        s = requests.Session()
        s.auth = HTTPBasicAuth(config['username'], config['password'])
        url = config['url'] + '/vscan_upload/'
        r = s.post(
            url,
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

    print "Finished exam: %s" % os.path.split(exam.directory)[-1]

    if r.status_code == 200:
        print "Result: %s" % r.json()['result']

        current_dir = os.path.dirname(os.path.realpath(__file__))
        shutil.move(
            exam.directory,
            os.path.join(
                current_dir,
                'complete',
                os.path.split(exam.directory)[-1]
            )
        )

    else:
        if r.status_code == 502:
            print "Result: Failed due to timeout (502) with the server. If this continues to be a problem, you can try to lower the max_upload_size option in the configuration file."
        else:
            print "Result: Failed (%s)" % r.status_code

    return r


def find_duplicate_exam_ids(exam_ids):
    dupes = []
    for exam in exam_ids:
        if exam not in dupes and exam_ids.count(exam) > 1:
            dupes.append(exam)

    return dupes


def upload(config, test_mode=False):
    print "Checking exams"
    exams = list(parse_archive())
    print "Done checking exams"

    if not len(exams):
        print "No exams to upload"
        return

    url = config['url'] + '/pending_exams/' + exams[0].serial
    r = requests.get(
        url=url,
        auth=HTTPBasicAuth(config['username'], config['password']),
    )

    if r.status_code != 200 or 'exam_ids' not in r.json().keys():
        print "Failed to get pending exam list from server. Please try again later."
        return

    pending_exams = r.json()['exam_ids']
    duplicate_exams = find_duplicate_exam_ids(pending_exams)

    failed_uploads = []
    FailedUpload = namedtuple(
        'FailedUpload', 'exam exam_index failure_count'
    )

    for i, exam in enumerate(exams):
        if not test_mode and exam.scan_id.lstrip('0') not in pending_exams:
            print "\nSkipping exam %s since there is no found pending exam." % exam.scan_id.lstrip('0')
            continue

        if exam.scan_id.lstrip('0') in duplicate_exams:
            print "\nSkipping exam %s since there are duplicate potential exams to match to." % exam.scan_id.lstrip('0')
            continue

        result = upload_exam(config, exam, i, len(exams))

        if not result or result.status_code != 200:
            failed_uploads.append(FailedUpload(
                exam,
                i,
                1
            ))

    while len(failed_uploads):
        if not test_mode:
            current_upload = failed_uploads.pop(0)

            result = upload_exam(
                config,
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
    test_mode = False

    if '--test' in sys.argv[1:]:
        SCANNER_DIR = os.path.join(
            os.getcwd(),
            'ARCHIVE'
        )
        test_mode = True

    if SCANNER_DIR:
        try:
            cfg_file = ConfigParser.RawConfigParser()
            cfg_file.read('config.cfg')

            config = {}

            config['server'] = cfg_file.get('uploader', 'server')
            config['username'] = cfg_file.get('uploader', 'username')
            config['password'] = cfg_file.get('uploader', 'password')
            config['max_upload_size'] = cfg_file.getfloat('uploader', 'max_upload_size')

            config['url'] = '%s/a/%s' % (config['server'], 'uth-rhd')

            if not config['username']:
                config['username'] = raw_input("Enter CommCareHQ username: ")

                # if there is no username, password is probably wrong anyway
                config['password'] = getpass.getpass()
            elif not config['password']:
                config['password'] = getpass.getpass()

            upload(config, test_mode)
        except Exception as e:
            raise
    else:
        print "Vscan not found"

    print('\nUploading complete. Press enter to exit.')
    raw_input()
