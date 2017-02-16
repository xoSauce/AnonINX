from request_creator import RequestCreator
from threading import Thread
from network_sender import NetworkSender
from binascii import unhexlify
class Worker(Thread):
	def __init__(self, myid, mixnode, client):
		Thread.__init__(self)
		self.id = myid
		self.mixnode = mixnode
		self.network_sender = NetworkSender()
		self.request_creator = RequestCreator()
		self.client = client;
		self.start()

	def run(self):
		json_data, destination = self.request_creator.poll_mixnode(self.id, self.mixnode)
		response = ''
		from time import sleep
		while response == '':
			response = self.network_sender.send_data_wait_long_response(json_data, destination)
			sleep(0.5)
		for entry in response:
				msg = entry['delta']
				print(self.client.recoverMessage(msg, entry['myid']))

class ClientPoller():
	def __init__(self):
		pass

	def poll_with(self, description, client):
		myid, mixnode = description
		Worker(myid, mixnode, client)