import os
import zipfile
import shutil

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

    def create_zip(self):
        test_dir_name = os.path.split(self.directory)[1]
        zip_filename = '%s.zip' % (test_dir_name)

        # TODO: create uploads/ if it doesn't exist
        zipf = zipfile.ZipFile(
            os.path.join('uploads', zip_filename),
            'w'
        )

        for root, dirs, files in os.walk(self.directory):
            for file in files:
                absolute_path = os.path.join(
                    root,
                    file
                )
                relative_path = os.path.join(
                    test_dir_name,
                    file
                )

                zipf.write(absolute_path, relative_path)

        zipf.close()

        return zip_filename


def parse_archive():
    exams = os.listdir(ARCHIVE_PATH)
    for exam in exams:
        exam_dir = os.path.join(ARCHIVE_PATH, exam)
        if exam not in ['.', '..'] and os.path.isdir(exam_dir):
            yield Exam(exam_dir, *exam.split('_'))


def upload():
    exams = parse_archive()
    zipped_exams = []

    # first zip all new files and archive their directories
    for exam in exams:
        zip_filename = exam.create_zip()

        current_dir = os.path.dirname(os.path.realpath(__file__))

        if zip_filename:
            shutil.move(
                exam.directory,
                os.path.join(current_dir, 'parsed')
            )

        zipped_exams.append(os.path.join(current_dir, 'uploads', zip_filename))

    # then post exam data
    # TODO


if __name__ == '__main__':
    # from requests.auth import HTTPBasicAuth
    upload()
