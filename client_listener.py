import json
from request_creator import RequestType
from generic_listener import GenericListener
from threading import Thread
import socket
class Worker(Thread):
	def __init__(self, socket, client, client_port):
		Thread.__init__(self)
		self.sock = socket
		self.client = client
		self.client_port = client_port
		self.start()

	def run(self):
		data = json.loads(self.sock.recv(1024).decode())
		if data['type'] == RequestType.push_to_client.value:
			print (data)

class ClientListener(GenericListener):
	def __init__(self, port, client):
		super().__init__(port)
		self.client = client
	
	def listen(self):
		super().listen()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, self.client, self.port)
		finally:
			self.serversocket.close()