TimeMachine
===========

Extract directories and files from an Apple TimeMachine external drive.

Ever moved from a Mac to a Linux machine and have to get some old content out of your Apple TimeMachine?

This script allows you to copy a specific file or a directory and it's contents from the TimeMachine to a destination on your local machine.


## NOTES:

- I don't know how well it works on a Windows machine as I developed it in Ubuntu, it has also come in handy when I'm pulling files after moving to a new mac.
- On occasion, you may get a permission denied error. When that happens you should run this with root access (sudo) as you will need it to access the protected files.
- This only copies Files and Directories. It **does not follow links**.


## Usage:

- Plug in your external HD
- Launch a terminal
- > python timemachine/__init__.py --help

 > timemachine --mount_path PATH [--host HOST] [--version VERSION] [--partition PARTITION] [--path PATH] [--dst_path PATH]

REQUIRED:
--mount_path PATH           Location where the timemachine HD is mounted. Usually something like "/Volumes/EXTERNAL_HARDDRIVE".

OPTIONAL:
--path PATH            Source path (Directory or File) as it would have appeared on your old computer. E.g. /Users/USERNAME/Desktop/work.odt
                       If a --dst_path is provided with this path, then we'll
                       copy this source to the destination.
                       If no --dst_path is provided then we'll enter interactive mode and you'll be prompted for commands.
--host HOST            Name of the host who's timemachine we want to access. Defaults to one with the most recent version.
--version VERSION      The name of the timemachine versions we want to access. Defaults to "Latest".
--partition PARTITION  The name of the partition in the timemachine we want to access. Usually "Macintosh HD"
--dst_path PATH        If provided we just copy path to dst_path, no interactive folder walking.


## ToDo:

- Copy/Follow symlinks.


## Issues and suggestions:

Fire on any issues or suggestions you have.


## Copyright and license
Copyright 2017 David Higgins

[MIT License](LICENSE)
