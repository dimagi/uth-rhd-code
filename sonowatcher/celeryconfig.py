from datetime import timedelta
#BROKER_URL defind by local_config, see local_config.py.example
CELERY_RESULT_BACKEND = ''
BROKER_URL = ''

## Worker settings
## If you're doing mostly I/O you can have more processes,
## but if mostly spending CPU, try to keep it close to the
## number of CPUs on your machine. If not set, the number of CPUs/cores
## available will be used.
CELERYD_CONCURRENCY = 2
UPLOADER_USER_ID = ''
UPLOADER_USERNAME = ''

CELERYBEAT_SCHEDULE = {
        "upload_exams": {
            "task": "tasks.get_qr_queue",
            "schedule": timedelta(seconds=60),
            },
        "server_checkin": {
            "task": "tasks.server_checkin",
            "schedule": timedelta(hours=24),
            }
        }

try:
    from local_config import *
except:
    pass

