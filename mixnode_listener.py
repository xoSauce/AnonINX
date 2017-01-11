import socket
import json
from generic_listener import GenericListener
from request_creator import RequestType
from mix import MixNode
from threading import Thread
from petlib.ec import EcPt
from binascii import unhexlify
from epspvt_utils import getGlobalSphinxParams
from logger import *

class Worker(Thread):
	def __init__(self, socket, address, mixnode):
		Thread.__init__(self)
		self.sock = socket
		self.addr = address
		self.mixnode = mixnode
		self.start()

	def run(self):
		def reconstruct_header(h_0, h_1, h_2):
			h_0 = unhexlify(h_0)
			params = getGlobalSphinxParams()
			group = params.group.G
			ecPt = EcPt.from_binary(h_0, group)
			return (ecPt, unhexlify(h_1), unhexlify(h_2))

		data = json.loads(self.sock.recv(4096).decode())
		log_debug(data['payload'])
		log_debug(data['type'])
		if data['type'] == RequestType.push_to_mix.value:
			data = data['payload']
			log.debug(data)
			header = reconstruct_header(data['header_0'], data['header_1'], data['header_2'])
			delta = unhexlify(data['delta'])
			result = self.mixnode.process(header, delta)
			log.debug(result)
			if result[1] is None:
				json_data, dest = RequestCreator().post_msg_to_mix(
					{'ip': addr, 'port': mix_port},
					{'header': header, 'delta': delta}
				)
				self.network_sender.send_data(json_data, dest)


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
		finally:
			self.serversocket.close()