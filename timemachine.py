
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
		These will have to be set eventually or we can't access paths to
		read or extract.
		"""
		self.mount_path = mount_path
		self.date = 'Latest'
		self.partition = 'Macintosh HD'

		self.get_machines()
		if not machine == None:
			self.set_machine(machine)
			if not date == None:
				self.set_date(date)
				if not partition == None:
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
		if isinstance(date, int):
			self.date = self.dates[date]
		else:
			self.date = date
		self.get_partitions()

	def set_partition(self, partition):
		"""
		Set what partition in the backup date you want to use.
		"""
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
		while not exists(real_path):
			real_path, head = split(real_path)
			removed.append(head)
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
		if not exists(dest_path):
			makedirs(dest_path)
		for item in listdir(real_path):
			new_item_path = join(path, item)
			self.copy_path(new_item_path, dest_path)


if __name__ == "__main__":
	tm = TimeMachine('/media/My Passport/', u'David\u2019s MacBook Air')
	tm.copy_path('/Users/sligodave/Desktop', '/tmp/')
