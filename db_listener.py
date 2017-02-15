import socket
import json
from generic_listener import GenericListener
from request_creator import RequestType, RequestCreator
from mix import MixNode
from threading import Thread
from petlib.ec import EcPt
from binascii import unhexlify
from epspvt_utils import getGlobalSphinxParams
from logger import *
from socket_utils import recv_timeout
from network_sender import NetworkSender
from sphinxmix.SphinxClient import Relay_flag
from broker_communicator import BrokerCommunicator
from petlib.pack import encode, decode
from sphinxmix.SphinxClient import create_surb, package_surb, rand_subset

class Worker(Thread):
	def __init__(self, socket, dbnode, db_port, mix_port):
		Thread.__init__(self)
		self.sock = socket
		self.dbnode = dbnode
		self.db_port = db_port
		self.mix_port = mix_port
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
			pir_method = data["pir_method"]
			decrypted_msg = decode(self.dbnode.decrypt(iv, text, pk, tag))
			try:
				###TODO encrypt for destination
				answer = json.dumps(self.dbnode.fetch_answer(decrypted_msg, pir_method))
				nymtuple = decrypted_msg['nymtuple']
				first_node = decode(nymtuple[0])
				reply = encode(answer)
				header,delta = package_surb(getGlobalSphinxParams(), nymtuple, reply)
				print("DELTA_DB {}".format(delta))
				mix_list = self.dbnode.get_mixnode_list()
				json_data, dest = RequestCreator().post_msg_to_mix(
					{'ip': first_node[1], 'port': self.mix_port},
					{'header': header, 'delta': delta}
				)
				self.network_sender.send_data(json_data, dest)
			except Exception as e:
				raise e

class DBListener(GenericListener):
	def __init__(self, db_port, mix_port, dbnode):
		super().__init__(db_port)
		self.dbnode = dbnode
		self.mixport = mix_port
	
	def listen(self):
		super().listen()
		try:
			while 1:
				clientsocket, address = self.serversocket.accept()
				Worker(clientsocket, self.dbnode, self.port, self.mix_port)
		finally:
			self.serversocket.close()