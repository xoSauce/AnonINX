import socket
import asyncore
import json
from PirSocket import PIRSocket
from broker import Broker
from request_creator import RequestType
from RequestHandlerAsyncore import RequestHandler
# from generic_listener import GenericListener
# from threading import Thread

#
# class Worker(Thread):
# 	def __init__(self, socket, address, broker):
# 		Thread.__init__(self)
# 		self.sock = socket
# 		self.addr = address
# 		self.broker = broker
# 		self.start()
#
# 	def run(self):
# 		data = json.loads(self.sock.recv(1024).decode())
		# if data['type'] == RequestType.publish_mix_data.value:
		# 	self.broker.register(data['payload'], 'mix')
		# 	self.sock.send(b'Key will be published.')
		# 	print('MixNodes:')
		# 	print(self.broker.mix_public_keys)
		# elif data['type'] == RequestType.publish_db_data.value:
		# 	self.broker.register(data['payload'], 'db')
		# 	self.sock.send(b'Key will be published.')
		# 	print('DBs:')
		# 	print(self.broker.db_public_keys)
		# elif data['type'] == RequestType.request_mix_list.value:
		# 	data = self.broker.fetch(data['payload'], 'mix')
		# 	self.sock.send(json.dumps(data).encode())
		# elif data['type'] == RequestType.request_db_list.value:
		# 	data = self.broker.fetch(data['payload'], 'db')
		# 	self.sock.send(json.dumps(data).encode())
#
# class KeyListener(GenericListener):
#
# 	def __init__(self, port, broker):
# 		super().__init__(port)
# 		self.broker = broker
#
# 	def run(self):
# 		super().run()
# 		try:
# 			while 1:
# 				clientsocket, address = self.serversocket.accept()
# 				Worker(clientsocket, address, self.broker)
# 		finally:
# 			self.serversocket.close()


class KeyListenerHandler(RequestHandler):
	def setData(self, broker, callback_data=None):
		super().setData(callback_data)
		self.broker = broker

	def handle_read(self):
		data = super().handle_read()
		if data:
			data = json.loads(data.decode())
			print(data)
			if data['type'] == RequestType.publish_mix_data.value:
				self.broker.register(data['payload'], 'mix')
				print('MixNodes:')
				print(self.broker.mix_public_keys)
			elif data['type'] == RequestType.publish_db_data.value:
				self.broker.register(data['payload'], 'db')
				print('DBs:')
				print(self.broker.db_public_keys)
			elif data['type'] == RequestType.request_mix_list.value:
				data = self.broker.fetch(data['payload'], 'mix')
				self.socket.sendall(json.dumps(data).encode())
			elif data['type'] == RequestType.request_db_list.value:
				data = self.broker.fetch(data['payload'], 'db')
				self.socket.sendall(json.dumps(data).encode())


class KeyListener(asyncore.dispatcher):
	def __init__(self, host, port, broker):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind((host, port))
		self.listen(5)
		self.broker = broker

	def handle_accept(self):
		pair = self.accept()
		if pair is not None:
			sock, addr = pair
			handler = KeyListenerHandler(sock)
			handler.setData(self.broker)
