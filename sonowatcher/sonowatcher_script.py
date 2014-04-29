import os
import zipfile
from watcher import SonoSiteWatcher

SCANNER_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests', 'complete')

def get_subdirectories(directory):
    return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

def run():
    current_path = os.path.dirname(os.path.abspath(__file__))

    for session in get_subdirectories(SCANNER_OUTPUT_DIR):
        try:
            # each exam session has nested scan sessions
            # TODO this is "supposed to" only be one dir, but in theory
            # may be more
            session_dir = os.path.join(SCANNER_OUTPUT_DIR, session)
            scan_dir = os.path.join(session_dir, get_subdirectories(session_dir)[0])

            watcher = SonoSiteWatcher(session_dir)

            if not watcher.is_complete():
                next

            zip_file = zipfile.ZipFile('uploading.zip', 'w')

            zip_file.write(
                os.path.join(scan_dir, 'PT_PPS.XML'),
                os.path.join(os.path.split(scan_dir)[-1], 'PT_PPS.XML')
            )
            for media, xml in watcher.all_media():
                zip_file.write(
                    os.path.join(scan_dir, media),
                    os.path.join(
                        os.path.split(scan_dir)[-1],
                        xml.split('.')[0],
                        media)
                )
                zip_file.write(
                    os.path.join(scan_dir, xml),
                    os.path.join(
                        os.path.split(scan_dir)[-1],
                        xml.split('.')[0],
                        xml
                    )
                )

                # TODO do processing here
        finally:
            os.remove(os.path.join(current_path, 'uploading.zip'))


if __name__ == '__main__':
    run()
