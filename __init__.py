"""

NOTE: You should really run this with root access as it will probably be
needed if you want full access to the Time Machine harddrive.

NOTE: This only supports files and directories.
It skips over links or any other non file/directory items.

THOUGHTS:
- Change the TimeMachine class to actually keep a cwd, so you can walk,
list current directory and copy it or items from it etc.

"""

import shutil
import os
import os.path
import sys


if sys.version_info >= (3, 0):
    raw_input = input


class TimeMachine(object):
    """
    Note: Skips links!!
    """
    backup_directory = 'Backups.backupdb'
    store_directory = '.HFS+ Private Directory Data\x0D'

    def __init__(self, mount_path, hostname=None, version=None, partition=None):
        self.mount_path = mount_path
        self.hostname = hostname
        self.version = version
        self.partition = partition

    @property
    def hostname_path(self):
        if self.hostname is None:
            return None
        return os.path.join(
            self.mount_path,
            self.backup_directory,
            self.hostname
        )

    @property
    def hostnames(self):
        return os.listdir(
            os.path.join(
                self.mount_path,
                self.backup_directory
            )
        )

    @property
    def version_path(self):
        if self.hostname is None or self.version is None:
            return None
        return os.path.join(
            self.mount_path,
            self.backup_directory,
            self.hostname,
            self.partition,
            self.version
        )

    @property
    def versions(self):
        if self.hostname is None:
            return None
        return os.listdir(
            os.path.join(
                self.mount_path,
                self.backup_directory,
                self.hostname
            )
        )

    @property
    def partition_path(self):
        if self.hostname is None or self.version is None or self.partition is None:
            return None
        return os.path.join(
            self.mount_path,
            self.backup_directory,
            self.hostname,
            self.version,
            self.partition
        )

    @property
    def partitions(self):
        if self.hostname is None or self.version is None:
            return None
        return os.listdir(
            os.path.join(
                self.mount_path,
                self.backup_directory,
                self.hostname,
                self.version
            )
        )

    def get_real_path(self, path):
        if path.startswith(os.sep):
            path = path[1:]
        if path.endswith(os.sep):
            path = path[:-1]
        bits = path.split(os.sep)
        path = self.partition_path
        while bits:
            item = bits.pop(0)
            path = os.path.join(path, item)
            if os.path.isfile(path):
                stats = os.stat(path)
                size = stats.st_size
                link = stats.st_nlink
                if not size and link > 3:
                    path = os.path.join(
                        self.mount_path,
                        self.store_directory,
                        'dir_{}'.format(link)
                    )
            elif not os.path.isdir(path):
                # TODO: Handle non file and directory items, such as links
                return None
        return path

    def copy_path(self, path, dest_path):
        """
        Given a path that would have worked on the backed up machine,
        copy the path out of the timemachine to a specified location.
        """
        real_path = self.get_real_path(path)
        if os.path.isfile(real_path):
            self.copy_file(path, dest_path)
        elif os.path.isdir(real_path):
            self.copy_directory(path, dest_path)

    def copy_file(self, path, dest_path):
        """
        Given a path to a file that would have worked on the backed up machine,
        copy the path out of the timemachine to a specified location.
        """
        real_path = self.get_real_path(path)
        shutil.copy(real_path, dest_path)

    def copy_directory(self, path, dest_path):
        """
        Given a path to a directory that would
        have worked on the backed up machine,
        copy the path out of the timemachine to a specified location.
        """
        real_path = self.get_real_path(path)
        if path.endswith('/'):
            path = path[:-1]
        dest_path = os.path.join(dest_path, os.path.split(path)[1])
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        for item in self.listdir(real_path):
            new_item_path = os.path.join(path, item)
            self.copy_path(new_item_path, dest_path)

    @classmethod
    def listdir(self, path):
        # We only support files or directories
        return [
            x for x in os.listdir(path) if
            os.path.isdir(os.path.join(path, x)) or
            os.path.isfile(os.path.join(path, x))
        ]


class InteractiveTimeMachine(TimeMachine):
    def interact(self):
        euid = os.geteuid()
        if euid != 0:
            print('IMPORTANT: It is recommended you run this as root\n'
                  'Without it you may not have full access '
                  'to the timemachine\'s files.\n'
                  'Consider ctrl-C to start again.\n')
        # Get Host
        if self.hostname is None:
            self.hostname = self.interactive_select(
                self.hostnames,
                'Select the hostname to use:'
            )
        # Get Version
        if self.version is None:
            self.version = self.interactive_select(
                self.versions,
                'Select the version to use:'
            )
        # Get Partition
        if self.partition is None:
            self.partition = self.interactive_select(
                self.partitions,
                'Select the partition to use:'
            )
        # List directories on loop to walk. Copy a file or directory to dst
        self.interactive_directory_select()

    def interactive_select(self, choices, message, evaluate=True):
        print(message)
        for i, choice in enumerate(choices):
            print('{}. {}'.format(i, choice))
        choice = raw_input('Enter 0-{}: '.format(len(choices) - 1))
        if evaluate:
            return choices[int(choice)]
        return choice

    def interactive_directory_select(self):
        path = '/'
        while 1:
            real_path = self.get_real_path(path)
            choices = ['Quit', 'Copy directory {}'.format(path), '..'] + self.listdir(real_path)
            message = 'Select a directory to enter or file to copy:'
            choice = int(self.interactive_select(choices, message, False))
            if choice == 0:
                return
            elif choice == 1:
                self.interactive_copy_path(path)
                break
            elif choice == 2:
                path = os.sep.join(path.split(os.sep)[:-1])
            elif os.path.isfile(self.get_real_path(os.path.join(path, choices[choice]))):
                self.interactive_copy_path(os.path.join(path, choices[choice]))
                break
            else:
                path = os.path.join(path, choices[choice])

    def interactive_copy_path(self, path):
        destination_path = raw_input('Please enter a destination directory: ')
        self.copy_path(path, destination_path)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        tm = InteractiveTimeMachine(sys.argv[1])
        tm.interact()
    elif len(sys.argv) == 7:
        tm = TimeMachine(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        tm.copy_path(sys.argv[5], sys.argv[6])
    else:
        print(
            'USAGE:\n'
            'python {} HARDDRIVE_MOUNTED_PATH\n'
            'OR\n'
            'python {} HARDDRIVE_MOUNTED_PATH HOSTNAME VERSION '
            'PARTITION MAC_SOURCE_PATH DESTINATION_DIRECTORY'.format(sys.argv[0], sys.argv[0])
        )
