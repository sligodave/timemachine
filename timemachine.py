
from shutil import copy
from os import listdir, stat, makedirs
from os.path import join, isdir, isfile, exists, split


class TimeMachine(object):
	"""
	Access an Apple Timemachine and extract files and directories.
	NOTE: There can be issues accessing some content because your
	user doesn't have access because of the uid and gid from the
	timemachine partition.
	"""
	def __init__(self, mount_path, machine=None, date=None, partition=None):
		"""
		Provide a path to the mount point of your timemachine drive on the
		local machine.
		You can also optionally provide a machine in the timemachine to use
		and a date of that machine to use.
		At least a machine will have to be set eventually
		or we can't access paths to read or extract.

		mount_path: The path to where the external
					timemachine hard drive is mounted.
		machine: The name of the backed up computer in the timemachine. 
					Tip: You'll find it at:
					MOUNT_PATH/Backups.backupdb/MACHINE
		date: The date of the backup in the timemachine you want to extract
					from
					Tip: You'll find it at:
					MOUNT_PATH/Backups.backupdb/MACHINE/DATE
		partition: The partition on the machine you want to access.
					Tip: You'll find it in the date directory:
					MOUNT_PATH/Backups.backupdb/MACHINE/DATE/PARTITION

		Only the mount point needs to be provided here.
		You can use the get_[machine|date|partition] methods to help you
		set the other attributes after instantiation of the class instance.
		"""
		# We must at least be given a path to the mounted timemachine
		self.mount_path = mount_path
		# We don't attempt to guess the machine name, it must be set.
		self.machine = None
		# Some sensible defaults but can optionally be provided
		self.date = 'Latest'
		self.partition = 'Macintosh HD'

		# Get all the machine options
		self.get_machines()
		if machine:
			self.set_machine(machine)
		if date:
			self.set_date(date)
		if partition:
			self.set_partition(partition)

	def get_machines(self):
		"""
		Get a list of all machines in the timemachine.
		"""
		self.machines = []
		for machine in listdir(join(self.mount_path, 'Backups.backupdb')):
			if machine.startswith('.'):
				continue
			self.machines.append(machine)
		return self.machines

	def get_dates(self):
		"""
		Get a list of all backup dates in the machine.
		"""
		self.dates = []
		for date in listdir(join(self.mount_path, 'Backups.backupdb',
		                    	 self.machine)):
			self.dates.append(date)
		return self.dates

	def get_partitions(self):
		"""
		Get a list of all partitions under a backup date.
		"""
		self.partitions = []
		for partition in listdir(join(self.mount_path, 'Backups.backupdb',
		                    	 self.machine, self.date)):
			self.partitions.append(partition)
		return self.partitions

	def set_machine(self, machine):
		"""
		Set what machine in the timemachine you want to use.
		"""
		if isinstance(machine, int):
			self.machine = self.machines[machine]
		else:
			self.machine = machine
		self.get_dates()

	def set_date(self, date):
		"""
		Set what backup date in the machine you want to use.
		"""
		if not self.machine:
			raise Exception('You must set the machine before setting the date')
		if isinstance(date, int):
			self.date = self.dates[date]
		else:
			self.date = date
		self.get_partitions()

	def set_partition(self, partition):
		"""
		Set what partition in the backup date you want to use.
		"""
		if not self.date:
			raise Exception('You must set the date before '\
			                'setting the partition')
		if isinstance(partition, int):
			self.partition = self.partitions[partition]
		else:
			self.partition = partition

	def get_real_path(self, path):
		"""
		Given a path that would have worked on the backed up machine,
		return it's real path in the timemachine's folder structure.
		"""
		if path.startswith('/'):
			path = path[1:]
		if path and path.endswith('/'):
			path = path[:-1]
		real_path = join(self.mount_path, 'Backups.backupdb', self.machine,
		                 self.date, self.partition, path)
		removed = []
		# Get what part of the provided path actually exists
		while not exists(real_path):
			real_path, head = split(real_path)
			removed.append(head)
		# Now work through the parts of the path that didn't exist
		# Replacing each step with it's actual
		# path in the dir_####### directories
		while removed:
			item = removed.pop()
			if isdir(real_path):
				real_path = join(real_path, item)
			elif isfile(real_path):
				stats = stat(real_path)
				size = stats.st_size
				link = stats.st_nlink
				if size or link <= 3:
					if not removed:
						return real_path
					raise Exception('Found a non direction component to the '\
					                'path that was of a size greater than 0,'\
					                ' so it\'s not a valid link.')
				real_path = join(self.mount_path,
				                 ".HFS+ Private Directory Data\x0D",
				                 "dir_%s" % link, item)
			else:
				raise Exception('Need to handle non file and directory nodes.')
			# Once we have finished we should go around again in case
			# the last item appended to the list is also a link
			if not removed and isfile(real_path):
				removed.append('')
		return real_path

	def copy_path(self, path, dest_path):
		"""
		Given a path that would have worked on the backed up machine,
		copy the path out of the timemachine to a specified location.
		"""
		real_path = self.get_real_path(path)
		if isfile(real_path):
			self.copy_file(path, dest_path)
		elif isdir(real_path):
			self.copy_directory(path, dest_path)

	def copy_file(self, path, dest_path):
		"""
		Given a path to a file that would have worked on the backed up machine,
		copy the path out of the timemachine to a specified location.
		"""
		real_path = self.get_real_path(path)
		# Copy real path to the destination
		copy(real_path, dest_path)

	def copy_directory(self, path, dest_path):
		"""
		Given a path to a directory that would
		have worked on the backed up machine,
		copy the path out of the timemachine to a specified location.
		"""
		real_path = self.get_real_path(path)
		if path.endswith('/'):
			path = path[:-1]
		dest_path = join(dest_path, split(path)[1])
		# Create the directory at the destination
		if not exists(dest_path):
			makedirs(dest_path)
		# Copy each item in the real path into the new destination
		# that we just created
		for item in listdir(real_path):
			new_item_path = join(path, item)
			self.copy_path(new_item_path, dest_path)


if __name__ == "__main__":
	tm = TimeMachine('/media/My Passport/', u'David\u2019s MacBook Air')
	tm.copy_path('/Users/sligodave/Desktop', '/tmp/')
