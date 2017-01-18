import socket
import json
from generic_listener import GenericListener
from threading import Thread
from broker import Broker
from request_creator import RequestType

class Worker(Thread):
	def __init__(self, socket, address, broker):
		Thread.__init__(self)
		self.sock = socket
		self.addr = address
		self.broker = broker
		self.start()

	def run(self):
		data = json.loads(self.sock.recv(1024).decode())
		if data['type'] == RequestType.publish_mix_data.value:
			self.broker.register(data['payload'])
			self.sock.send(b'Key will be published.')
			print(self.broker.get_cache())
		elif data['type'] == RequestType.publish_db_data:
			self.broker.register(data['payload'])
			self.sock.send(b'Key will be published.')
			print(self.broker.get_cache())
		elif data['type'] == RequestType.request_mix_list.value:
			data = self.broker.fetch(data['payload'], 'mix')
			self.sock.send(json.dumps(data).encode())
		elif data['type'] == RequestType.request_db_list.value:
			data = self.broker.fetch(data['payload'], 'db')
			self.sock.send(json.dumps(data).encode())

class KeyListener(GenericListener):

	def __init__(self, port, broker):
		super().__init__(port)
		self.broker = broker

	def listen(self):
		super().listen()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, address, self.broker)
		finally:
			self.serversocket.close()
