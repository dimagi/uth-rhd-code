from lxml import etree
import os


class SonoSiteWatcher(object):
    IGNORE_PATH = 'temp_sl'

    NEEDED_FOR_COMPLETION = [
        'sonologo.gif',
        'REPORT.XML',
        'PT_PPS.XML',
        'PT_REPORT.HTML',
    ]

    REPORT_PDF = 'PT_REPORT.PDF'

    SHOULD_NOT_EXIST = [
        'REPORT.XSD',
        'PT_PPS.XSD',
        'PT_REPORT.FO',
    ]

    def __init__(self, full_path):
        self.path = full_path

    def exam_dirs(self):
        exams = os.listdir(self.path)
        for exam in exams:
            if exam not in ['.', '..'] and \
               os.path.isdir(os.path.join(self.path, exam)):
                yield exam

    def return_pairs(self, exam_dir, file_filter):
        """
        All exam binaries (jpg or video) are paired with an xml file.
        This method returns tuples of them.

        Assumption here is that the caller of this method will
        do the actual processing of the exam files.
        """
        files = self.exam_files(exam_dir)
        non_report_files = filter(lambda x: x not in self.NEEDED_FOR_COMPLETION+ [self.REPORT_PDF], files)
        image_files = filter(file_filter, non_report_files)
        xml_files = filter(lambda x: x.endswith('.XML'), non_report_files)

        def parse_num(n):
            #07.01.32 hrs __[0000279]
            return n[n.index('[')+1:n.index(']')]

        file_map = dict((parse_num(x), x) for x in image_files)

        for xml in xml_files:
            #e.g. C0000282.XML
            seq = xml[1:-4]
            if seq in file_map:
                yield file_map[seq], xml

    def exam_image_pairs(self, exam_dir):
        def img_filter(x):
            return x.endswith('.jpeg') or x.endswith('.jpg')
        file_filter = img_filter
        return self.return_pairs(exam_dir, file_filter)

    def exam_video_pairs(self, exam_dir):
        def vid_filter(x):
            return x.endswith('.mp4')
        file_filter = vid_filter
        return self.return_pairs(exam_dir, file_filter)

    def patient_exam_xml(self):
        if hasattr(self, '_patient_xml'):
            return self._patient_xml

        for exam_dir in self.exam_dirs():
            files = self.exam_files(exam_dir)
            if "PT_PPS.XML" in files:
                with open(os.path.join(self.path, exam_dir, 'PT_PPS.XML')) as fin:
                    patient_xml = fin.read()
                    self._patient_xml = patient_xml
                    return patient_xml
        return None

    def exam_files(self, exam_dir):
        files = os.listdir(os.path.join(self.path, exam_dir))
        return files

    def get_case_id(self):
        """
        This is the case_id if it's extracted, assumed to be in the PatientID
        However, there's a nonzero chance of them either forgetting to scan it
        Or putting it in the wrong field like PatientsName
        """
        patient_xml = self.patient_exam_xml()
        exam_root = etree.fromstring(patient_xml)
        return exam_root.find("PatientID").text

    def get_study_id(self):
        """
        The GUID the sonosite generates for the particular exam
        """
        patient_xml = self.patient_exam_xml()
        exam_root = etree.fromstring(patient_xml)
        return exam_root.find("SonoStudyInstanceUID").text

    def all_media(self):
        for exam_dir in self.exam_dirs():
            #return self.exam_image_pairs(exam_dir)
            for img, xml in self.exam_image_pairs(exam_dir):
                yield img, xml

            for img_pair in self.exam_video_pairs(exam_dir):
                yield img_pair

    def is_complete(self):
        """
        Given the directory that the process is looking at,
        determine if it's complete and ready for processing.

        To do this, we check every test directory for completion. We do this
        for completion and edge case protection, even though there should
        only be one test directory per exam.
        """
        for file_or_dir in self.exam_dirs():
            if not self.is_test_complete(os.path.join(self.path, file_or_dir)):
                return False

        return True

    def is_test_complete(self, test_dir):
        files = self.exam_files(test_dir)

        done_files = 0
        for x in self.NEEDED_FOR_COMPLETION:
            if x in files:
                done_files += 1

        completed = False
        if done_files == len(self.NEEDED_FOR_COMPLETION):
            completed = True

        # check for shouldn't exist files
        for x in self.SHOULD_NOT_EXIST:
            if x in files:
                completed = False
                break
        return completed

    def archive_exam(self, exam_dir):
        """
        Assuming that processing is complete, move the exam directory to the
        archive location so that it won't be processed again.
        """
        pass
