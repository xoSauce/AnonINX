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
from socket_utils import recv_timeout
from request_creator import RequestCreator
from network_sender import NetworkSender
from sphinxmix.SphinxClient import Relay_flag
from broker_communicator import BrokerCommunicator
class Worker(Thread):
	def __init__(self, socket, dbnode, db_port):
		Thread.__init__(self)
		self.sock = socket
		self.mix_port = mix_port
		self.network_sender = NetworkSender()
		self.start()

	def run(self):
		data = json.loads(self.sock.recv(1024).decode())
		if data['type'] == RequestType.request_db.value:
			data = data['payload']
			message = data['message']
			print (message)

class DBListener(GenericListener):
	def __init__(self, port, dbnode):
		super().__init__(port)
		self.dbnode = dbnode
	
	def listen(self):
		super().listen()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, self.dbnode, self.port)
		finally:
			self.serversocket.close()