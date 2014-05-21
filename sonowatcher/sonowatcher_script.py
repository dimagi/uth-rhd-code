import os
from watcher import SonoSiteWatcher
import requests
from requests.auth import HTTPDigestAuth
import shutil
import ConfigParser

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

SCANNER_OUTPUT_DIR = os.path.join(CURRENT_PATH, 'complete')


def get_subdirectories(directory):
    return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]


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

        watcher = SonoSiteWatcher(session_dir)

        if not watcher.is_complete():
            # if this directory is still being copied, just skip for now
            continue

        files = {}
        files['PT_PPS.XML'] = open(os.path.join(scan_dir, 'PT_PPS.XML'), 'r')

        for media, xml in watcher.all_media():
            files[media] = open(os.path.join(
                scan_dir,
                media
            ), 'rb')

        s = requests.Session()
        s.auth = HTTPDigestAuth(config['username'], config['password'])
        r = s.post(
            config['url'] + '/sonosite_upload',
            files=files,
            data={}
        )

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
            print "%s: %s" % (r.json()['result'], r.json()['message'])
        else:
            print r
            print "Unknown error"


if __name__ == '__main__':
    cfg_file = ConfigParser.RawConfigParser()
    cfg_file.read('config.cfg')

    config = {}

    config['server'] = cfg_file.get('sonowatcher', 'server')
    config['username'] = cfg_file.get('sonowatcher', 'username')
    config['password'] = cfg_file.get('sonowatcher', 'password')

    if config['server'] and config['username'] and config['password']:
        config['url'] = '%s/a/%s' % (config['server'], 'uth-rhd')

        run(config)
    else:
        print "Missing configuration values. Please make sure server, username and password are stored in config.cfg."
