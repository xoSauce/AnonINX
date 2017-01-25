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
from petlib.pack import encode, decode
from sphinxmix.SphinxClient import create_surb, package_surb, rand_subset

class Worker(Thread):
	def __init__(self, socket, dbnode, db_port):
		Thread.__init__(self)
		self.sock = socket
		self.dbnode = dbnode
		self.db_port = db_port
		self.network_sender = NetworkSender()
		self.start()

	def run(self):
		data = json.loads(self.sock.recv(1024).decode())
		if data['type'] == RequestType.push_to_db.value:
			data = json.loads(data['payload'])
			iv = unhexlify(data["iv"].encode())
			text = unhexlify(data["text"].encode())
			pk = EcPt.from_binary(unhexlify(data["pk"].encode()), getGlobalSphinxParams().group.G)
			tag = unhexlify(data["tag"].encode())
			decrypted_msg = decode(self.dbnode.decrypt(iv, text, pk, tag))
			try:
				###TODO encrypt for destination
				answer = json.dumps(self.dbnode.fetch_answer(decrypted_msg))
				nymtuple = decrypted_msg['nymtuple']
				reply = encode(answer)
				header,delta = package_surb(getGlobalSphinxParams(), nymtuple, reply)
				mix_list = self.dbnode.get_mixnode_list()
				use_nodes = rand_subset(mix_list.keys(), 5)
				json_data, dest = RequestCreator().post_msg_to_mix(
					{'ip': use_nodes[0], 'port': 8081},
					{'header': header, 'delta': delta}
				)
				print(json_data, dest)
				self.network_sender.send_data(json_data, dest)
				print (use_nodes)
				print (mix_list)
			except Exception as e:
				print(e)
				log_debug("Requested message did not have the right type. {}".format(e))

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