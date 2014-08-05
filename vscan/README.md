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


Testing
=======

- To test this script there are a few flags that can be used.
    - `--test`: Ignore checking if there is a matching, untouched exam case on the server.
    - `--local-files`: Use files in the `Archive/` path in the script directory instead of a real Vscan.

- In your local HQ instance, import cases of type child to domain uth-rhd that have the following two properties set:
    - `scanner_serial`: The files in `Archive/` use "VH014466XK" for this property.
    - `exam_number`: The files in `Archive/` use 4, 10, 12 and 16 for this. Make sure this property is marked as an integer type on the uploader.

