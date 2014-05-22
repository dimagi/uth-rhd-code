SonoSite image and video uploader
=================================

This process manages collecting and uploading the images and videos from the SonoSite device to CommCareHQ.

Process
=======

The SonoSite SiteLink software will be running at all times to download exams from the device to C:\\sonosite. When this task runs, it will scan the directories to ensure that they are completely copied based on checking for key files that should or should not exist in the directory.

If a directory is done, the script will package the files and attempt to post them to CommCareHQ. If this succeeds, the directory will be archived.

Dependencies
============

Python 2.7, LXML and the Requests library are required for this script.

SonoSite Example Exports
========================

In the `tests/complete` directory there are two example exams from the SonoSite device. One with a patient id and one without.
