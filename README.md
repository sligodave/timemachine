TimeMachine
===========

Extract directories and files from an Apple TimeMachine external drive.

Ever moved from a Mac to a Linux machine and have to get some old content out of your Apple TimeMachine?

This script allows you to copy a specific file or a directory and it's contents from the TimeMachine to a destination on your local machine.


## NOTES:

- I don't know how well it works on a Windows machine as I developed it in Ubuntu.
- You should run this with root access (sudo) as you will probably need it to access all the files on the drive.
- This only copies Files and Directories. It does not follow links.


## Usage:

- Plug in your external HD
- Launch a terminal
- Two options:
  - Interactive:
    - This method presents you with prompts to pick the correct "hostname", "version" and "partition" from the TimeMachine. It will then allow you to navigate through the directory structure of your TimeMachine. You can select a specific directory or file to copy out of it. It will then prompt you for a destination directory.
    - sudo python timemachine/__init__.py MOUNT_PATH
    - e.g. sudo python timemachine/__init__.py /media/USERNAME/DRIVE_NAME
  - Automatic:
    - This method assumes that all reqiured variables have been provided. "mount_point", "hostname", "version", "partition", "source_path", "destination_directory". It will copy the "source_path" into the "destination_path".
    - sudo python timemachine/__init__.py MOUNT_POINT HOSTNAME VERSION PARTITION SOURCE_PATH DESTINATION_PATH
    - e.g. sudo python timemachine/__init__.py /media/USERNAME/DRIVE_NAME COMPUTER_NAME Latest Macintosh /User/USERNAME/Desktop/my_file.txt /home/USERNAME/Desktop/my_file.txt

- MOUNT_POINT = Where the external harddrive is mounted on your system.
- HOSTNAME = The computer name that the Mac had.
- VERSION = Each TimeMachine backup has a version or date, to get the latest use "Latest".
- PARTITION = The partitions on your mac that were backed up. You usually have a main one called "Macintosh".
- SOURCE_PATH = Path to the file or directory you want to copy. The path is as it would have been on your Mac.
- DESTINATION_DIRECTORY = The directory you want to copy the supplied SOURCE_PATH to on your local machine.


## ToDo:



## Issues and suggestions:

Fire on any issues or suggestions you have.


## Copyright and license
Copyright 2014 David Higgins

[MIT License](LICENSE)