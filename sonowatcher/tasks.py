from celery.decorators import task
import logging
import requests
from datetime import datetime
import simplejson


@task
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



@task
def server_checkin():
    """
    Get amqp state and send stats back to HQ
    """
    pass

