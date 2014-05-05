from unittest import TestCase
from sonowatcher.watcher import SonoSiteWatcher
import os


class WatcherTests(TestCase):
    """
    Tests to ensure that sonosite file watching works

    Most functionality was moved to server side.

    `./setup.py test` from repository root
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
