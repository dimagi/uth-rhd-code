import unittest
from uploader import Exam, ARCHIVE_PATH, parse_archive


class UploaderTests(unittest.TestCase):
    def setUp(self):
        # serial, scan id, date string, file count
        self.expected_exams = [
            ('VH014466XK', '000004', '20130510T175307', 2),
            ('VH014466XK', '000010', '20130528T163904', 3),
            ('VH014466XK', '000012', '20130709T174340', 4),
            ('VH014466XK', '000016', '20130722T175057', 10),
        ]

    def testDirectoryParsing(self):
        exams = parse_archive()
        for i, exam in enumerate(exams):
            self.assertEqual(exam.serial, self.expected_exams[i][0])
            self.assertEqual(exam.scan_id, self.expected_exams[i][1])
            self.assertEqual(exam.date, self.expected_exams[i][2])
            self.assertEqual(len(list(exam.files)), self.expected_exams[i][3])

if __name__ == '__main__':
    unittest.main()
