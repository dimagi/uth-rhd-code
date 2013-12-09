# Filesystem Watcher for SonoSite Image Uploads

## (or anything else you want to watch being deposited in the filesystem)

This filesystem watching script will examind the contents of a directory
and upload the contents as attachments to CommCareHQ as an xform with said attachments.

## Process

Windows necessary

Using Sonosite file downloader, it'll download by default to c:\sonosite

Using a celery task that's registered to windows service, scan the c:\sonosite

The task will scan the directory and determine if the directory is "Done" by the contents of the directory.

There are key files that should and should not exist for the directory to be considered "done"

If done, move the directory over to the "transmitted" folder. Begin processing of folder to create an xform
and put attachments.

Parse the xml submission to determine case id, and create xform with case block and attachments to upload to HQ

Purge the directory if the server confirms receipt.

If the exists the off chance that a case ID is not on the filesystem, submit anyway and create a new case
or create a blank entry for reassignment later (TBD)

