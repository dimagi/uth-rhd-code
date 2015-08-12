import os
from requests.auth import HTTPBasicAuth
from watcher import SonoSiteWatcher
import requests
import shutil
import ConfigParser

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

SCANNER_OUTPUT_DIR = "C:\\sonosite"

ATTEMPT_COUNT = 4


def get_subdirectories(directory):
    return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]


def get_file_size(file_path):
    return float(os.stat(file_path).st_size) / 1024 / 1024


def run(config):

    for session in get_subdirectories(SCANNER_OUTPUT_DIR):
        # each exam session has nested scan sessions
        # TODO this is "supposed to" only be one dir, but in theory
        # may be more
        session_dir = os.path.join(SCANNER_OUTPUT_DIR, session)
        subdirectories = get_subdirectories(session_dir)
        if subdirectories:
            scan_dir = os.path.join(session_dir, subdirectories[0])
        else:
            continue

        print ""

        print "Uploading: " + os.path.split(session_dir)[-1]

        watcher = SonoSiteWatcher(session_dir)

        if not watcher.is_complete():
            # if this directory is still being copied, just skip for now
            print "Session not complete. This likely means it has not finished copying from the SonoSite device."
            continue

        files = {}
        files['PT_PPS.XML'] = open(os.path.join(scan_dir, 'PT_PPS.XML'), 'r')

        current_mbs = 0
        skipped = False

        for media, xml in watcher.all_media():
            file_size = get_file_size(os.path.join(scan_dir, media))

            if current_mbs + file_size < config['max_upload_size']:
                files[media] = open(os.path.join(
                    scan_dir,
                    media
                ), 'rb')
            else:
                skipped = True

        if skipped:
            print "Some images or videos were skipped due to exam size being too large."

        try:
            s = requests.Session()
            s.auth = HTTPBasicAuth(config['username'], config['password'])
            for attempt in range(ATTEMPT_COUNT):
                if attempt > 0:
                    print "Retrying... retry attempt %s" % attempt

                r = s.post(
                    config['url'] + '/sonosite_upload',
                    files=files,
                )
                if r.status_code == 200:
                    break
                else:
                    # need to reset the file pointers before
                    # attempting again (or no content will be sent)
                    for f in files.values():
                        f.seek(0)
                    print "Error (%s)" % r.status_code

        except requests.ConnectionError:
            print "Could not connect to server."
            continue

        # clean up
        for f in files.values():
            f.close()

        if r.status_code == 200:
            if r.json()['result'] == 'uploaded':
                shutil.move(
                    session_dir,
                    os.path.join(
                        CURRENT_PATH,
                        'complete',
                        os.path.split(session_dir)[-1]
                    )
                )
            print "Success: %s" % r.json()['message']
        else:
            if r.status_code == 502:
                print "Result: Failed due to timeout (502) with the server. If this continues to be a problem, you can try to lower the max_upload_size option in the configuration file."
            else:
                print "Result: Failed (%s)" % r.status_code


if __name__ == '__main__':
    try:
        cfg_file = ConfigParser.RawConfigParser()
        cfg_file.read('config.cfg')

        config = {}

        config['server'] = cfg_file.get('sonowatcher', 'server')
        config['username'] = cfg_file.get('sonowatcher', 'username')
        config['password'] = cfg_file.get('sonowatcher', 'password')
        config['max_upload_size'] = cfg_file.getfloat('sonowatcher', 'max_upload_size')

        if config['server'] and config['username'] and config['password']:
            config['url'] = '%s/a/%s' % (config['server'], 'uth-rhd')

            run(config)
        else:
            print "Missing configuration values. Please make sure server, username and password are stored in config.cfg."

    except Exception as e:
        print e

    print('\nUploading complete. Press enter to exit.')
    raw_input()
