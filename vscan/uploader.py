import os
import shutil
import requests
from requests.auth import HTTPDigestAuth

URL = 'http://localhost:8000/a/hello'

SCANNER_DIR = '/Users/tyler/code/dimagi/uth-rhd-code/vscan/'

ARCHIVE_PATH = os.path.join(SCANNER_DIR, 'Archive')


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
            yield Exam(exam_dir, *exam.split('_'))


def pack_directory(directory):
    # name of the test directory we're packing
    test_dir_name = os.path.split(directory)[1]

    packed_directory = {}

    for root, dirs, files in os.walk(directory):
        for f in files:
            relative_path = os.path.join(test_dir_name, f)
            packed_directory[relative_path] = open(os.path.join(root, f))

    return packed_directory


def upload():
    exams = parse_archive()

    for exam in exams:
        files = pack_directory(exam.directory)

        r = requests.post(
            url='http://localhost:8000/a/hello/vscan_upload',
            auth=HTTPDigestAuth('t@w.com', 'asdf'),
            files=files,
            data={
                'scanner_serial': exam.serial,
                'scan_id': exam.scan_id,
                'date': exam.date
            },
        )
        print ""
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
            "Result: Failed"


if __name__ == '__main__':
    upload()
