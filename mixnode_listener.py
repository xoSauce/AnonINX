import socket
import json
from generic_listener import GenericListener
from epspvt_utils import RequestType
from mix import MixNode
from threading import Thread

class Worker(Thread):
	def __init__(self, socket, address, mixnode):
		Thread.__init__(self)
		self.sock = socket
		self.addr = address
		self.mixnode = mixnode
		self.start()

	def run(self):
		data = json.loads(self.sock.recv(1024).decode())
		print (data)

class MixNodeListener(GenericListener):
	def __init__(self, port, mixnode):
		super().__init__(port)
		self.mixnode = mixnode
	
	def listen(self):
		super().listen()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, address, self.mixnode)
			pass
		finally:
			self.serversocket.close()