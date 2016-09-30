#!/usr/bin/env python

"""

NOTE: You should really run this with root access as it will probably be
needed if you want full access to the Time Machine harddrive.

NOTE: This only supports files and directories.
It skips over links or any other non file/directory items.

"""

import shutil
import os
import os.path
import sys
import logging


logger = logging.getLogger('time_machine')


if sys.version_info >= (3, 0):
    raw_input = input


class TimeMachineException(Exception):
    pass


class TimeMachine(object):
    backup_directory = 'Backups.backupdb'
    store_directory = '.HFS+ Private Directory Data\x0D'

    def __init__(self, mount_path, host=None, version=None, partition=None):
        logger.info('Set mount_path "%s"', mount_path)
        self.mount_path = mount_path
        self._host = self._version = self._partition = None
        if host is not None:
            self.host = host
        if version is not None:
            self.version = version
        if partition is not None:
            self.partition = partition

    def __ensure_value(self, name):
        # Make sure we were supplied the value
        value = getattr(self, '_{}'.format(name))
        if value is None:
            # If only one option is available, we use that
            options = getattr(self, '{}s'.format(name))
            if len(options) == 1:
                return options[0]
            raise ValueError('You must set a "%s" value.', name)
        return value

    @property
    def hosts(self):
        return [
            x
            for x in os.listdir(
                os.path.join(
                    self.mount_path,
                    self.backup_directory
                )
            )
            if not x.startswith('.')
        ]

    def get_host(self):
        return self.__ensure_value('host')

    def set_host(self, host):
        logger.info('Set Host "%s"', host)
        self._host = host

    host = property(get_host, set_host)

    @property
    def host_path(self):
        return os.path.join(
            self.mount_path,
            self.backup_directory,
            self.host
        )

    @property
    def versions(self):
        return [x for x in os.listdir(self.host_path) if not x.startswith('.')]

    def get_version(self):
        return self.__ensure_value('version')

    def set_version(self, version):
        logger.info('Set Version "%s"', version)
        self._version = version

    version = property(get_version, set_version)

    @property
    def version_path(self):
        return os.path.join(self.host_path, self.version)

    @property
    def partitions(self):
        return [x for x in os.listdir(self.version_path) if not x.startswith('.')]

    def get_partition(self):
        return self.__ensure_value('partition')

    def set_partition(self, partition):
        logger.info('Set Partition "%s"', partition)
        self._partition = partition

    partition = property(get_partition, set_partition)

    @property
    def partition_path(self):
        return os.path.join(
            self.version_path,
            self.partition
        )

    def get_real_path(self, path):
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]
        bits = path.split('/')
        new_path = self.partition_path
        while bits:
            item = bits.pop(0)
            new_path = os.path.join(new_path, item)
            if os.path.isfile(new_path):
                stats = os.stat(new_path)
                size = stats.st_size
                link = stats.st_nlink
                if not size and link > 3:
                    new_path = os.path.join(
                        self.mount_path,
                        self.store_directory,
                        'dir_{}'.format(link)
                    )
            elif not os.path.isdir(new_path):
                # TODO: Handle non file and directory items, such as links
                return None
        logger.debug('Real Path "%s" -> "%s"', path, new_path)
        return new_path

    def copy_path(self, path, dst_path):
        """
        Given a path that would have worked on the backed up machine,
        copy the path out of the timemachine to a specified location.
        """
        real_path = self.get_real_path(path)
        logger.info('Copy Path "%s" -> "%s" -> "%s"', path, real_path, dst_path)
        if real_path:
            if os.path.isfile(real_path):
                self.copy_file(path, dst_path)
            elif os.path.isdir(real_path):
                self.copy_directory(path, dst_path)
        else:
            # TODO: Handle non file and directory items, such as links
            pass

    def copy_file(self, path, dst_path):
        """
        Given a path to a file that would have worked on the backed up machine,
        copy the path out of the timemachine to a specified location.
        """
        real_path = self.get_real_path(path)
        logger.info('Copy File "%s" -> "%s" -> "%s"', path, real_path, dst_path)
        shutil.copy(real_path, dst_path)

    def copy_directory(self, path, dst_path):
        """
        Given a path to a directory that would
        have worked on the backed up machine,
        copy the path out of the timemachine to a specified location.
        """
        real_path = self.get_real_path(path)
        logger.info('Copy Directory "%s" -> "%s" -> "%s"', path, real_path, dst_path)
        if path.endswith('/'):
            path = path[:-1]
        dst_path = os.path.join(dst_path, os.path.split(path)[1])
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        for item in self.listdir(real_path):
            new_item_path = os.path.join(path, item)
            self.copy_path(new_item_path, dst_path)

    @staticmethod
    def listdir(path):
        # TODO: Handle non file and directory items, such as links
        return [
            x for x in os.listdir(path) if
            os.path.isdir(os.path.join(path, x)) or
            os.path.isfile(os.path.join(path, x))
        ]


class InteractiveTimeMachine(TimeMachine):
    def __init__(self, mount_path, host=None, version=None, partition=None, path=None, dst_path=None):
        super(InteractiveTimeMachine, self).__init__(mount_path, host, version, partition)
        try:
            self.host
        except ValueError:
            self.host = self.interactive_select(
                self.hosts,
                'Select the host to use:'
            )
        try:
            self.version
        except ValueError:
            self.version = self.interactive_select(
                self.versions,
                'Select the version to use:'
            )
        try:
            self.partition
        except ValueError:
            self.partition = self.interactive_select(
                self.partitions,
                'Select the partition to use:'
            )
        if path and dst_path:
            self.copy_path(path, dst_path)
        else:
            self.interactive_directory_select(path)

    def interactive_select(self, choices, message, evaluate=True):
        print(message)
        for i, choice in enumerate(choices):
            print('{}. {}'.format(i, choice))
        choice = raw_input('Enter 0-{}: '.format(len(choices) - 1))
        if evaluate:
            return choices[int(choice)]
        return choice

    def interactive_directory_select(self, path=None):
        path = path if path else '/'
        while 1:
            real_path = self.get_real_path(path)
            if os.path.isfile(real_path):
                self.interactive_copy_path(path)
                break
            else:
                choices = ['Quit', 'Copy directory {}'.format(path), '..'] + self.listdir(real_path)
                message = 'Select a directory to enter or file to copy:'
                choice = int(self.interactive_select(choices, message, False))
                if choice == 0:
                    return
                elif choice == 1:
                    self.interactive_copy_path(path)
                    break
                elif choice == 2:
                    path = '/'.join(path.split('/')[:-1])
                elif os.path.isfile(self.get_real_path(os.path.join(path, choices[choice]))):
                    self.interactive_copy_path(os.path.join(path, choices[choice]))
                    break
                else:
                    path = os.path.join(path, choices[choice])

    def interactive_copy_path(self, path):
        dst_path = raw_input('Please enter a destination directory: ')
        self.copy_path(path, dst_path)


def usage(msg=''):
    if msg:
        msg = '\nERROR: {}\n'.format(msg)
    return '''
> timemachine --mount_path PATH [--host HOST] [--version VERSION] [--partition PARTITION] [--path PATH] [--dst_path PATH]
{}
REQUIRED:
--mount_path PATH           Location where the timemachine HD is mounted. Usually something like "/Volumes/__HD_NAME__".

OPTIONAL:
--path PATH            Local path to directory to start in. We'll try to infer anything not provided.
--host HOST            Name of the host who's timemachine we want to access. Defaults to one with the most recent version.
--version VERSION      The name of the timemachine versions we want to access. Defaults to "Latest".
--partition PARTITION  The name of the partition in the timemachine we want to access. Usually "Macintosh HD"
--dst_path PATH        If provided we just copy path to dst_path, no interactive folder walking.
    '''.format(msg)


def get_arg(args, name):
    value = None
    flag = '--{}'.format(name)
    equals = [x for x in args if x.startswith('{}='.format(flag))]
    if equals:
        value = equals[0]
        value = value[value.find('=') + 1:]
    if not value and flag in args:
        loc = args.index(flag)
        if len(args) > loc + 1 and not args[loc + 1].startswith('--'):
            value = args[loc + 1]
    return value


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    kwargs = {
        'mount_path': None,
        'host': None,
        'version': None,
        'partition': None,
        'path': None,
        'dst_path': None,
    }
    for n in kwargs.keys():
        kwargs[n] = get_arg(sys.argv, n)

    if '--help' in sys.argv:
        print(usage())
    elif kwargs['mount_path'] is None:
        print(usage('You MUST provide a "--mount_path" value.'))
    else:
        InteractiveTimeMachine(**kwargs)
