VScan Uploads
=============

This project manages the uploading of Vscan images and videos to CommCareHQ. The script can be run when the VScan is plugged into a computer and then uploaded to the server via post requests.

Dependencies
============

Python 2.7 and the Requests library are required for this script.


GE VScan Example Exports
========================

The `Archive` folder contains example exports taken from a VScan. This is how the device will look when mounted as a USB device.

On an android device, it will be /mnt/storagefolder/Archive/\<serial_number\>\_\<exam_id\>\_\<date\>. Where the `exam_id` is an integer left padded with zeroes to 6 places and format for `date` is YYYYMMDDTHHmmss.

On Windows, it will be mounted as a USB readable drive, such as F:\\Archive\.

The root folder for the dvice will also have a file named `ScannerID.GEUSHH` with some metadata on the scanner itself.

The android interaction should allow for the clinician to choose files they want to select.
