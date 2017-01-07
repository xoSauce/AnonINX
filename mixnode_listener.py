import socket
import json
from generic_listener import GenericListener
from request_creator import RequestType
from mix import MixNode
from threading import Thread
from petlib.ec import EcPt
from binascii import unhexlify
from epspvt_utils import getGlobalSphinxParams

class Worker(Thread):
	def __init__(self, socket, address, mixnode):
		Thread.__init__(self)
		self.sock = socket
		self.addr = address
		self.mixnode = mixnode
		self.start()

	def run(self):
		##### TODO -- fix this -- reconstruct object
		def reconstruct_header(h_0, h_1):
			h_0 = unhexlify(h_0)
			h_1 = unhexlify(h_1)
			params = getGlobalSphinxParams()
			group = params.group.G
			ecPt = EcPt.from_binary(h_0, group)
			return (ecPt, h_1)

		data = json.loads(self.sock.recv(4096).decode())
		if data['type'] == RequestType.push_to_mix.value:
			data = data['payload']
			header = reconstruct_header(data['header_0'], data['header_1'])
			delta = unhexlify(data['delta'])
			print (header, delta)

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