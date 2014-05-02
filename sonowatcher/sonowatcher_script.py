import os
from watcher import SonoSiteWatcher
import requests
from requests.auth import HTTPDigestAuth
import shutil

SCANNER_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'tests', 'complete'
)


def get_subdirectories(directory):
    return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]


def run():
    current_path = os.path.dirname(os.path.abspath(__file__))

    for session in get_subdirectories(SCANNER_OUTPUT_DIR):
        # each exam session has nested scan sessions
        # TODO this is "supposed to" only be one dir, but in theory
        # may be more
        session_dir = os.path.join(SCANNER_OUTPUT_DIR, session)
        scan_dir = os.path.join(session_dir, get_subdirectories(session_dir)[0])

        watcher = SonoSiteWatcher(session_dir)

        if not watcher.is_complete():
            # if this directory is still being copied, just skip for now
            next

        files = {}
        files['PT_PPS.XML'] = open(os.path.join(scan_dir, 'PT_PPS.XML'), 'r')

        for media, xml in watcher.all_media():
            files[media] = open(os.path.join(
                scan_dir,
                media
            ), 'r')
            """
            zip_file.write(
                os.path.join(scan_dir, xml),
                os.path.join(
                    os.path.split(scan_dir)[-1],
                    xml.split('.')[0],
                    xml
                )
            )
            """

        r = requests.post(
            url='http://localhost:8000/a/hello/sonosite_upload',
            auth=HTTPDigestAuth('t@w.com', 'asdf'),
            files=files,
            data={}
        )

        if r.status_code == 200:
            if r.json()['result'] == 'uploaded':
                pass
                # TODO enable this after testing
                # shutil.move(
                #     session_dir,
                #     os.path.join(current_path, 'complete')
                # )
            print "%s: %s" % (r.json()['result'], r.json()['message'])
        else:
            print "Unknown error"


if __name__ == '__main__':
    run()
