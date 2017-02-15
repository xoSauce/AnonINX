import json
from request_creator import RequestType
from generic_listener import GenericListener
from threading import Thread
from socket_utils import recv_timeout
from petlib.pack import decode
from binascii import unhexlify
import socket


class Worker(Thread):
	def __init__(self, socket, client, client_port, requested_index):
		Thread.__init__(self)
		self.sock = socket
		self.client = client
		self.client_port = client_port
		self.requested_index = requested_index
		self.start()

	def run(self):
		print("here")
		raw_data = recv_timeout(self.sock, timeout=0.1)
		data = json.loads(raw_data)
		if data['type'] == RequestType.push_to_client.value:
			msg = decode(unhexlify(data['payload']))
			print(self.client.recoverMessage(msg))

class ClientListener(GenericListener):
	def __init__(self, port, client):
		super().__init__(port)
		self.client = client
	
	def listen_for(self, requested_index):
		super().listen()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, self.client, self.port, requested_index)
		finally:
			self.serversocket.close()