import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

IGNORE_PATH = 'temp_sl'

COMPLETED_FILES = [
        'sonologo.gif',
        'REPORT.XML',
        'PT_PPS.XML',
        'PT_REPORT.HTML',
        ]

#these files must not be in the directory for it to be considered done.
#bonus if they're detected then removed, but there is the chance that this watcher
#doesn't encounter these files creations/removals while listening
EXIST_THEN_DELETED_FILES = [
        'REPORT.XSD',
        'PT_PPS.XSD',
        'PT_REPORT.FO',
        ]


#all other files are paired with XML
#C0000299.XML => 07.06.59 hrs __[0000299].jpeg or mp4



def upload_completed_exam(exam_path):
    """
    Given that the watchdog has determined a dump is completed from the sonosite, commence uploading to the server
    get the case_id from the xml

    authenticate (once the auth submits are done)

    make xform with case submit.

    attach all? or attach one at a time? 

    all images+original xml 
    get info from PT_PPS.XML to populate case block?


    extract annotations?

    upload via preformatted xform and put attachments
    """
    pass



if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    watch_dir(sys.argv[1]

def watch_dir(dirpath):
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=dirpath, recursive=True)
    observer.start()

    try:
        while True:
	    print "nothing..."
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

