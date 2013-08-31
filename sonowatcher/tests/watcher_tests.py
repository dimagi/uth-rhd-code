from datetime import timedelta, datetime
from unittest import TestCase
from sonowatcher.watcher import SonoSiteWatcher
import os


class WatcherTests(TestCase):
    """
    Tests to ensure that sonosite file watching works
    """

    def setUp(self):
        pass

    def tearDown(self):
        #delete target dir?
        pass


    def testCompleteDirs(self):
        currpath = os.path.dirname(os.path.abspath(__file__))
        print currpath
        cpath = os.path.join(currpath, 'complete')
        completes = os.listdir(cpath)
        for c in completes:
            watcher = SonoSiteWatcher(os.path.join(currpath, 'complete', c))
            self.assertTrue(watcher.is_complete())
            print "media!"
            print list(watcher.all_media())
            self.assertIsNotNone(watcher.patient_exam_xml())



    def testGenerateSubmission(self):
        pass


    def testGetIDs(self):
        study_ids = ["1.2.840.114340.03.000008251017183037.1.20130425.163744.0000053",
                     "1.2.840.114340.03.000008251017183037.2.20130821.094421.0000080"]


        case_ids = ["JHUYIIYIUIY", "(_No_ID_)" ]
        currpath = os.path.dirname(os.path.abspath(__file__))
        cpath = os.path.join(currpath, 'complete')
        completes = os.listdir(cpath)
        for c in completes:
            watcher = SonoSiteWatcher(os.path.join(currpath, 'complete', c))
            self.assertTrue(watcher.is_complete())
            study_id = watcher.get_study_id()
            case_id = watcher.get_case_id()

            self.assertTrue(study_id in study_ids)
            study_ids.remove(study_id)

            self.assertTrue(case_id in case_ids)
            case_ids.remove(case_id)








