import os
from datetime import datetime, timedelta
import uuid
from mock import self
from sonowatcher import celeryconfig


def get_xforms(sonowatch):
    """
    For a given completed sonowatcher instance
    generate the xform submisisons and their requisite attachments.

    submit all images in one xform with multiple attachments
    submit all videos as individual xform+attachments
    """
    xform = ""
    attachment_dict = {}

    yield xform, attachment_dict





#modified_date format 2013-08-23T11:38:45.396
#<attachment_group>
#<file_attachment>prop1</file_attachment>        
#</attachment_group> 
#<attachment_group>
#<file_attachment>prop2</file_attachment>        
#</attachment_group> 
#<attachment_group>
#<file_attachment>prop3</file_attachment>        
#</attachment_group> 


def render_xform(file_tuples, exam_uuid, patient_case_id=None):
    xform_template = None
    with open("upload_form.xml.template", 'r') as fin:
        xform_template = fin.read()

    def case_attach_block(key, filename):
        return '<n0:%s src="%s" from="local"/>' % (key, os.path.split(filename)[-1])
    case_attachments = [case_attach_block(t[0], t[1]) for t in file_tuples]

    def form_attachment_group(key, filename):
        return '<n0:%s src="%s" from="local"/>' % (key, os.path.split(filename)[-1])
    attach_group = [form_attachment_group(t[0], t[1]) for t in file_tuples]


    submit_id = uuid.uuid4().hex

    #we're making a new caseid to subcase this to the patient
    submit_case_id = uuid.uuid4().hex

    format_dict = {
        "time_start": (datetime.utcnow() - timedelta(seconds=5)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "time_end": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "date_modified": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "user_id": celeryconfig.UPLOADER_USER_ID,
        "username": celeryconfig.UPLOADER_USERNAME,
        "doc_id": submit_id,
        "case_id": submit_case_id,
        "patient_case_id": patient_case_id,
        "case_attachments": ''.join(case_attachments),
        "attachment_group": ''.join(attach_group)
    }

    final_xml = xform_template % format_dict
    #url = self.url_base + "/a/%s/receiver" % domain
    #print post_data(final_xml, url, path=None, use_curl=True, use_chunked=True, is_odk=True, attachments=attachment_tuples)
    return final_xml






    return ""

