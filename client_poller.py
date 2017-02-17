from request_creator import RequestCreator
from threading import Thread
from network_sender import NetworkSender
from binascii import unhexlify
from petlib.pack import decode
class Worker(Thread):
	def __init__(self, myid, mixnode, client, message_pool):
		Thread.__init__(self)
		self.id = myid
		self.mixnode = mixnode
		self.network_sender = NetworkSender()
		self.request_creator = RequestCreator()
		self.client = client;
		self.message_pool = message_pool

	def run(self):
		json_data, destination = self.request_creator.poll_mixnode(self.id, self.mixnode)
		response = ''
		from time import sleep
		while response == '':
			response = self.network_sender.send_data_wait_long_response(json_data, destination)
			sleep(0.5)
		id = response['id']
		response = response['response']
		for entry in response:
			msg = entry['delta']
			recoveredMessage = self.client.recoverMessage(msg, entry['myid'])
			self.message_pool[id] = (recoveredMessage[0], recoveredMessage[1])

class ClientPoller():
	def __init__(self):
		pass

	def poll_with(self, description, client, messages):
		myid, mixnode = description
		return Worker(myid, mixnode, client, messages)