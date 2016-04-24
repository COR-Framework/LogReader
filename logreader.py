from cor.utils import adaptive_sleeper
from cor.api import CORModule, Message
import threading
import os


def follow(thefile):
	thefile.seek(0, 2)
	sleeper = adaptive_sleeper(0.01, 1.5, 0.2)
	while True:
		line = thefile.readline()
		if not line:
			sleeper()
			continue
		sleeper(reset=True)
		yield line


class LogReader(CORModule):

	def readlog(self):
		with open(self.path, 'r') as fifo:
			for line in follow(fifo):
				msg = Message("LOGREADER." + os.path.basename(self.path), {"value": line})
				self.messageout(msg)

	def __init__(self, path="/var/log/system.log", wipelog=False, **kwargs):
		super().__init__(**kwargs)
		self.path = path
		if wipelog:
			open(path, 'w').close()

		self.socket_thread = threading.Thread(target=self.readlog)
		self.socket_thread.start()
